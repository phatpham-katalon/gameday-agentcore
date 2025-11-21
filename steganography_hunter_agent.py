# Copyright 2025 Amazon.com and its affiliates; all rights reserved.
# This file is Amazon Web Services Content and may not be distributed without permission.

"""
Steganography Hunter Agent - Hidden Message Detection
Handles acrostic messages, spacing patterns, and numeric encoding schemes using AI agents
"""

from strands import Agent, tool
from strands.models import BedrockModel

# Initialize the model
model_id = "us.amazon.nova-pro-v1:0"
model = BedrockModel(model_id=model_id)

@tool
def acrostic_detector(text: str) -> str:
    """Detect acrostic messages using an AI agent"""
    try:
        ACROSTIC_AGENT_PROMPT = """
        You are a cryptography expert specializing in acrostic message detection.
        
        Acrostic messages hide text in the first letters of lines, words, or sentences.
        1. Extract the first letter of each line
        2. Combine these letters to reveal the hidden message
        3. Also check first letters of words or sentences if line-based doesn't work
        
        Always return your answer in the format: "DECODED: [result]" or "NO HIDDEN MESSAGE DETECTED"
        """
        
        acrostic_agent = Agent(
            system_prompt=ACROSTIC_AGENT_PROMPT,
            model=model
        )
        response = acrostic_agent(f"Detect acrostic messages in this text: {text}")
        return str(response)
    except Exception as e:
        return f"Error detecting acrostic messages: {str(e)}"

@tool
def numeric_encoding_decoder(text: str) -> str:
    """Decode numeric encoding schemes using an AI agent"""
    try:
        NUMERIC_AGENT_PROMPT = """
        You are a cryptography expert specializing in numeric encoding schemes.
        
        Common numeric encoding methods:
        1. A1Z26: A=1, B=2, C=3, ..., Z=26 (e.g., "8 5 12 12 15" = HELLO)
        2. ASCII: Character codes (e.g., 72=H, 69=E, 76=L, 76=L, 79=O)
        3. Phone keypad: 2=ABC, 3=DEF, 4=GHI, 5=JKL, 6=MNO, 7=PQRS, 8=TUV, 9=WXYZ
        4. Binary: 8-bit patterns (e.g., 01001000 = H)
        
        Try all applicable methods and return the most readable result.
        
        Always return your answer in the format: "DECODED: [result]" or "NO VALID ENCODING DETECTED"
        """
        
        numeric_agent = Agent(
            system_prompt=NUMERIC_AGENT_PROMPT,
            model=model
        )
        response = numeric_agent(f"Decode numeric encoding in this text: {text}")
        return str(response)
    except Exception as e:
        return f"Error decoding numeric encoding: {str(e)}"

