# Copyright 2025 Amazon.com and its affiliates; all rights reserved.
# This file is Amazon Web Services Content and may not be duplicated without permission.

"""
Cipher Command Agent - Multi-Agent Orchestration
Main orchestration agent that coordinates all specialist cipher-breaking agents
"""

import asyncio
import logging
import os
from threading import Lock
from typing import Dict, Any, Optional, Tuple

from strands import Agent
from strands.multiagent import Swarm
from strands_tools import current_time
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from botocore.config import Config as BotocoreConfig
import boto3

# Import specialist agent tools
from cipher_rookie_agent import caesar_cipher_decoder, atbash_cipher_decoder, simple_substitution_decoder
from pattern_detective_agent import morse_code_decoder, rail_fence_decoder, polybius_square_decoder
from steganography_hunter_agent import acrostic_detector, numeric_encoding_decoder
from cipher_master_agent import multi_layer_decoder, cipher_type_identifier

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_SWARM_LOCK = Lock()
_swarm: Optional[Swarm] = None
_cipher_agents: Optional[Dict[str, Agent]] = None


def _determine_region() -> str:
    """Best-effort region resolution with safe fallbacks."""
    session = boto3.Session()
    region = session.region_name
    if region:
        return region
    return os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"


def _build_boto_config() -> BotocoreConfig:
    return BotocoreConfig(
        retries={"max_attempts": 3, "mode": "standard"},
        connect_timeout=15,
        read_timeout=360,
    )


def _create_model(region: str) -> BedrockModel:
    return BedrockModel(
        model_id="us.amazon.nova-pro-v1:0",
        boto_client_config=_build_boto_config(),
        region_name=region,
    )


def _create_agents(model: BedrockModel) -> Dict[str, Agent]:
    """Instantiate all specialized agents for the swarm."""
    cipher_rookie = Agent(
        name="cipher_rookie",
        model=model,
        tools=[caesar_cipher_decoder, atbash_cipher_decoder, simple_substitution_decoder, cipher_type_identifier],
        system_prompt="""You are Cipher Rookie, specializing in basic substitution ciphers (Caesar, Atbash, simple substitution).

Use cipher_type_identifier first, then the appropriate decoder tool.
Return: "DECRYPTED: [message]"
If it's not your cipher type, hand off to the appropriate specialist.""",
    )

    pattern_detective = Agent(
        name="pattern_detective",
        model=model,
        tools=[morse_code_decoder, rail_fence_decoder, polybius_square_decoder, cipher_type_identifier],
        system_prompt="""You are Pattern Detective, specializing in pattern-based ciphers (Morse code, Rail Fence, Polybius square).

Use cipher_type_identifier first, then the appropriate decoder tool.
Return: "DECRYPTED: [message]"
If it's not your cipher type, hand off to the appropriate specialist.""",
    )

    steganography_hunter = Agent(
        name="steganography_hunter",
        model=model,
        tools=[acrostic_detector, numeric_encoding_decoder, cipher_type_identifier],
        system_prompt="""You are Steganography Hunter, specializing in hidden message detection (acrostic messages, numeric encoding).

Use cipher_type_identifier first to check for hidden messages, then use appropriate detector.
Return: "DECODED: [message]" or "NO HIDDEN MESSAGE DETECTED"
If it's a regular cipher, hand off to the appropriate specialist.""",
    )

    cipher_master = Agent(
        name="cipher_master",
        model=model,
        tools=[multi_layer_decoder, cipher_type_identifier],
        system_prompt="""You are Cipher Master, the entry point for all cipher challenges. Use cipher_type_identifier first to analyze the cipher type.

Based on identification, either:
- Handle advanced/multi-layer ciphers yourself using multi_layer_decoder
- Hand off to appropriate specialist:
  * cipher_rookie for Caesar, Atbash, simple substitution
  * pattern_detective for Morse code, Rail Fence, Polybius square (coordinate pairs like "44 23 15")
  * steganography_hunter for hidden messages and simple numeric encoding (like "8 5 12 16")

IMPORTANT ROUTING RULES:
- Coordinate pairs with spaces/slashes (like "44 23 15 / 32 15 54") → pattern_detective (Polybius square)
- Simple sequential numbers (like "8 5 12 16") → steganography_hunter (A1Z26 encoding)
- Dots and dashes → pattern_detective (Morse code)
- Mixed letters → cipher_rookie (substitution ciphers)

Return: "DECRYPTED: [message]" or hand off to the right specialist.""",
    )

    intelligence_analyst = Agent(
        name="intelligence_analyst",
        model=model,
        tools=[cipher_type_identifier],
        system_prompt="""You are Intelligence Analyst, specializing in message analysis and threat assessment.

Use your tools for analysis: keyword_extractor, message_correlator, threat_assessor.
If data appears encrypted, use cipher_type_identifier then hand off to appropriate cipher agent.
Return complete analysis results from your tools.""",
    )

    return {
        "cipher_rookie": cipher_rookie,
        "pattern_detective": pattern_detective,
        "steganography_hunter": steganography_hunter,
        "cipher_master": cipher_master,
        "intelligence_analyst": intelligence_analyst,
    }


def _create_swarm() -> Tuple[Swarm, Dict[str, Agent]]:
    agents = _create_agents(_create_model(_determine_region()))
    swarm_instance = Swarm(
        list(agents.values()),
        entry_point=agents["cipher_master"],
        max_handoffs=5,
        max_iterations=5,
        execution_timeout=180.0,
        node_timeout=60.0,
        repetitive_handoff_detection_window=3,
        repetitive_handoff_min_unique_agents=2,
    )
    return swarm_instance, agents


def _ensure_swarm_initialized() -> Swarm:
    """Lazy-load the swarm so container startup stays fast."""
    global _swarm, _cipher_agents
    if _swarm is None:
        with _SWARM_LOCK:
            if _swarm is None:
                logger.info("Initializing cipher swarm for the first time")
                _swarm, _cipher_agents = _create_swarm()
    return _swarm

# Export swarm for external testing (used by validation scripts)
def get_cipher_swarm() -> Swarm:
    """Get the configured cipher swarm for external testing"""
    return _ensure_swarm_initialized()


# Export individual agents for testing
def get_cipher_agents() -> Dict[str, Agent]:
    """Get all cipher agents for individual testing"""
    _ensure_swarm_initialized()
    return dict(_cipher_agents or {})



# Validation function for deployment script compatibility
def validate_swarm_functionality():
    """Validate swarm functionality for deployment validation"""
    
    try:
        swarm_instance = get_cipher_swarm()
        # Test that swarm can be created and configured
        if not swarm_instance or not swarm_instance.agents:
            return False, "Swarm not properly initialized"
        
        if len(swarm_instance.agents) != 5:
            return False, f"Expected 5 agents, found {len(swarm_instance.agents)}"
        
        # Test that all agents have proper tools
        agent_names = [agent.name for agent in swarm_instance.agents]
        expected_agents = ["cipher_rookie", "pattern_detective", "steganography_hunter", "cipher_master", "intelligence_analyst"]
        
        for expected_agent in expected_agents:
            if expected_agent not in agent_names:
                return False, f"Missing agent: {expected_agent}"
        
        return True, "Swarm validation passed"
        
    except Exception as e:
        return False, f"Swarm validation error: {str(e)}"

# Initialize BedrockAgentCoreApp with Strands integration
app = BedrockAgentCoreApp()


async def _heartbeat_loop(context, interval_seconds: int = 30):
    """Continuously ping AgentCore so long operations stay alive."""
    while True:
        try:
            await context.ping(status="HEALTHY_BUSY")
        except Exception as exc:
            logger.debug("Heartbeat ping failed: %s", exc)
        await asyncio.sleep(interval_seconds)


@app.entrypoint
async def strands_agent_bedrock(payload: Dict[str, Any], context: Optional[Any] = None) -> str:
    """
    Simple cipher command agent entrypoint - let the swarm handle routing and complexity
    """
    user_input = payload.get("prompt", "")
    
    if not user_input:
        return "Error: No prompt provided. Please provide encrypted text or cryptographic challenge."
    
    swarm_instance = get_cipher_swarm()
    ping_task = None
    if context and hasattr(context, "ping"):
        ping_task = asyncio.create_task(_heartbeat_loop(context))
    
    try:
        # Let the swarm handle all routing and agent coordination
        response = await swarm_instance.invoke_async(user_input)
        
        # Extract just the text content from the response
        if hasattr(response, 'results') and response.results:
            # Get the last successful result from the swarm
            for agent_name, node_result in reversed(response.results.items()):
                if hasattr(node_result, 'result') and hasattr(node_result.result, 'message'):
                    message = node_result.result.message
                    if isinstance(message, dict) and 'content' in message:
                        content = message['content'][0]['text']
                        return content
        
        # Fallback for other response formats
        if hasattr(response, 'message'):
            if isinstance(response.message, dict) and 'content' in response.message:
                return response.message['content'][0]['text']
            else:
                return str(response.message)
        
        # Final fallback
        return str(response)
        
    except Exception as e:
        return f"Error processing cipher: {str(e)}"
    finally:
        if ping_task:
            ping_task.cancel()
            try:
                await ping_task
            except asyncio.CancelledError:
                pass

if __name__ == "__main__":
    # Run app for AgentCore deployment
    app.run()
