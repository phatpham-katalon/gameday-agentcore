# Copyright 2025 Amazon.com and its affiliates; all rights reserved.
# This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

"""
Pattern Detective Agent - Pattern-Based Ciphers
Handles Morse code, Rail Fence ciphers, and Polybius square ciphers using AI agents
"""

from strands import Agent, tool
from strands.models import BedrockModel

# Initialize the model
model_id = "us.amazon.nova-pro-v1:0"
model = BedrockModel(model_id=model_id)

@tool
def morse_code_decoder(encrypted_text: str) -> str:
    """Decode Morse code using an AI agent"""
    try:
        MORSE_AGENT_PROMPT = """
        You are a cryptography expert specializing in Morse code.
        
        Morse code represents letters as combinations of dots (.) and dashes (-):

        {TODO I bet it'll be smarter if it knows what these are}
        
        Always return your answer in the format: "DECODED: [result]"
        """
        
        morse_agent = Agent(
            system_prompt=MORSE_AGENT_PROMPT,
            model=model
        )
        response = morse_agent(f"Decode this Morse code: {encrypted_text}")
        return str(response)
    except Exception as e:
        return f"Error decoding Morse code: {str(e)}"

@tool
def rail_fence_decoder(encrypted_text: str) -> str:
    """Decode Rail Fence cipher using an AI agent"""
    try:
        RAIL_FENCE_AGENT_PROMPT = """
        You are a cryptography expert specializing in Rail Fence ciphers.

        
        {Todo: only thing i know with rails is trains and this isn't a train i'm so in over my head}
        
        
        To decrypt:
        {There's like 5 steps i think it needs to know}
        
        Always return your answer in the format: "DECODED: [result]"

        """
        
        rail_fence_agent = Agent(
            system_prompt=RAIL_FENCE_AGENT_PROMPT,
            model=model
        )
        response = rail_fence_agent(f"Decode this Rail Fence cipher: {encrypted_text}")
        return str(response)
    except Exception as e:
        return f"Error decoding Rail Fence cipher: {str(e)}"

@tool
def polybius_square_decoder(encrypted_text: str) -> str:
    """Decode Polybius square cipher using an AI agent"""
    try:
        POLYBIUS_AGENT_PROMPT = """
        You are a cryptography expert specializing in Polybius square ciphers.
        
        Polybius square maps letters to coordinate pairs in a 5x5 grid:
        
        {TODO I dunno what that word means}
        
        
        To decrypt:
        {TODO I heard this was an algo-rythem but i don't know what music has to do with it}
        
        Always return your answer in the format: "DECODED: [result]"
        """
        
        polybius_agent = Agent(
            system_prompt=POLYBIUS_AGENT_PROMPT,
            model=model
        )
        response = polybius_agent(f"Decode this Polybius square cipher: {encrypted_text}")
        return str(response)
    except Exception as e:
        return f"Error decoding Polybius square: {str(e)}"

