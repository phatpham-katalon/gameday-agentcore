# Copyright 2025 Amazon.com and its affiliates; all rights reserved.
# This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

"""
Cipher Rookie Agent - Basic Substitution Ciphers
Handles Caesar ciphers, Atbash ciphers, and simple substitution ciphers using AI agents
"""

from strands import Agent, tool
from strands.models import BedrockModel

# Initialize the model
model_id = "us.amazon.nova-pro-v1:0"
model = BedrockModel(model_id=model_id)

@tool
def caesar_cipher_decoder(encrypted_text: str) -> str:
    """Decrypt Caesar cipher using an AI agent"""
    try:
        CAESAR_AGENT_PROMPT = """
        You are a cryptography expert specializing in Caesar ciphers.
        
        To decrypt Caesar ciphers:
        1. Try all 26 possible shifts (ROT1 through ROT25)
        2. For each shift, move each letter forward/backward in the alphabet
        3. Identify which shift produces readable English text
        4. Look for common words like THE, AND, OF, IS
        
        Always return your answer in the format: "DECRYPTED: [result]"
        """
        
        caesar_agent = Agent(
            system_prompt=CAESAR_AGENT_PROMPT,
            model=model
        )
        response = caesar_agent(f"Decrypt this Caesar cipher: {encrypted_text}")
        return str(response)
    except Exception as e:
        return f"Error decrypting Caesar cipher: {str(e)}"

@tool
def atbash_cipher_decoder(encrypted_text: str) -> str:
    """Decrypt Atbash cipher using an AI agent"""
    try:
        ATBASH_AGENT_PROMPT = """
        You are a cryptography expert specializing in Atbash ciphers.
        
        To decrypt Atbash:
        1. Atbash is a reverse alphabet substitution: A↔Z, B↔Y, C↔X, D↔W, etc.
        2. Replace each letter with its mirror opposite in the alphabet
        3. A becomes Z, B becomes Y, C becomes X, and so on
        4. Atbash is its own inverse - applying it twice returns the original
        
        Always return your answer in the format: "DECRYPTED: [result]"
        """
        
        atbash_agent = Agent(
            system_prompt=ATBASH_AGENT_PROMPT,
            model=model
        )
        response = atbash_agent(f"Decrypt this Atbash cipher: {encrypted_text}")
        return str(response)
    except Exception as e:
        return f"Error decrypting Atbash cipher: {str(e)}"

@tool
def simple_substitution_decoder(encrypted_text: str) -> str:
    """Decrypt simple substitution cipher using an AI agent"""
    try:
        SUBSTITUTION_AGENT_PROMPT = """
        You are a cryptography expert specializing in simple substitution ciphers.
        
        To decrypt substitution ciphers:
        1. Analyze letter frequency (E, T, A, O, I, N are most common in English)
        2. Look for common patterns (TH, HE, AN, IN, ER)
        3. Identify single-letter words (A, I)
        4. Map encrypted letters to their likely plaintext equivalents
        5. Test mappings and refine until readable text emerges
        
        Always return your answer in the format: "DECRYPTED: [result]"
        """
        
        substitution_agent = Agent(
            system_prompt=SUBSTITUTION_AGENT_PROMPT,
            model=model
        )
        response = substitution_agent(f"Decrypt this simple substitution cipher using frequency analysis: {encrypted_text}")
        return str(response)
    except Exception as e:
        return f"Error decrypting substitution cipher: {str(e)}"

