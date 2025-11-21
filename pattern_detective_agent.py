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
        A=.- B=-... C=-.-. D=-.. E=. F=..-. G=--. H=.... I=.. J=.--- K=-.- L=.-.. M=-- N=-. O=--- P=.--. Q=--.- R=.-. S=... T=- U=..- V=...- W=.-- X=-..- Y=-.-- Z=--..
        
        Decode by splitting on spaces and mapping each pattern to its letter.
        
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
        
        Rail Fence cipher writes text in a zigzag pattern across multiple rails, then reads off each rail.
        
        To decrypt:
        1. Determine the number of rails (typically 2-4)
        2. Calculate how many characters go on each rail
        3. Reconstruct the zigzag pattern
        4. Read the message following the zigzag path
        5. Try different rail counts if needed
        
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
          1 2 3 4 5
        1 A B C D E
        2 F G H I/J K
        3 L M N O P
        4 Q R S T U
        5 V W X Y Z
        
        To decrypt:
        1. Split the input into coordinate pairs (e.g., "44 23 15" or "44/23/15")
        2. First digit is row, second digit is column
        3. Look up each pair in the grid to get the letter
        4. Combine letters to form the message
        
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

