# 🔐 Cipher Quest Implementation Plan

## Mission Objective
Complete TODOs in cipher agent files to create a working multi-agent system that decrypts various cipher types, then deploy to AWS AgentCore to obtain an ARN for GameDay scoring.

---

## Phase 1: Complete Agent Tool Implementations

### 1.1 Fix `cipher_rookie_agent.py` (3 TODOs)

**File:** `cipher_rookie_agent.py`

**TODO 1: Caesar Cipher Decoder**
- Location: Line ~18 in `caesar_cipher_decoder` function
- Add instructions: Try all 26 possible shifts (ROT1-ROT25), identify readable English text
- Format: Clear step-by-step decryption process

**TODO 2: Atbash Cipher Decoder**
- Location: Line ~40 in `atbash_cipher_decoder` function  
- Add instructions: A↔Z, B↔Y, C↔X mapping (reverse alphabet substitution)
- Format: Explain the substitution pattern

**TODO 3: Simple Substitution Decoder**
- Location: Line ~60 in `simple_substitution_decoder` function
- Add instructions: Use frequency analysis to identify letter mappings
- Format: Explain frequency analysis method

---

### 1.2 Fix `pattern_detective_agent.py` (3 TODOs)

**File:** `pattern_detective_agent.py`

**TODO 1: Morse Code Decoder**
- Location: Line ~20 in `morse_code_decoder` function
- Add: Complete Morse code mapping table (A=.-, B=-..., C=-.-., etc.)
- Format: Provide full alphabet mapping

**TODO 2: Rail Fence Decoder**
- Location: Line ~40 in `rail_fence_decoder` function
- Add: Rail Fence cipher algorithm explanation (zigzag pattern, rail reconstruction)
- Format: Step-by-step decoding process (5 steps mentioned in comment)

**TODO 3: Polybius Square Decoder**
- Location: Line ~65 in `polybius_square_decoder` function
- Add: 5x5 grid layout and coordinate-to-letter conversion process
- Format: Grid structure and decoding algorithm

---

### 1.3 Fix `steganography_hunter_agent.py` (2 TODOs)

**File:** `steganography_hunter_agent.py`

**TODO 1: Acrostic Detector**
- Location: Line ~18 in `acrostic_detector` function
- Add: Instructions for extracting first letters of lines/words/sentences
- Format: Detection method explanation

**TODO 2: Numeric Encoding Decoder**
- Location: Line ~35 in `numeric_encoding_decoder` function
- Add: Examples of numeric encoding schemes:
  - A1Z26 (A=1, B=2, ..., Z=26)
  - ASCII codes
  - Phone keypad mapping (2=ABC, 3=DEF, etc.)
- Format: List common encoding methods with examples

---

### 1.4 Fix `cipher_master_agent.py` (2 TODOs)

**File:** `cipher_master_agent.py`

**TODO 1: Multi-Layer Decoder Tools**
- Location: Line ~45 in `multi_layer_decoder` function
- Add: `tools=[atbash_cipher, caesar_cipher]` to Agent initialization
- Purpose: Give agent access to actual cipher algorithms from common_algos

**TODO 2: Cipher Type Identifier Tools**
- Location: Line ~85 in `cipher_type_identifier` function
- Add: `tools=[]` (empty array, or optionally same tools as above)
- Purpose: Agent uses pattern analysis, may not need tools

---

### 1.5 Fix `cipher_command_agent.py` (5 TODOs)

**File:** `cipher_command_agent.py`

**TODO 1: Cipher Rookie Tools**
- Location: Line ~48
- Add: `[caesar_cipher_decoder, atbash_cipher_decoder, simple_substitution_decoder, cipher_type_identifier]`

**TODO 2: Pattern Detective Tools**
- Location: Line ~60
- Add: `[morse_code_decoder, rail_fence_decoder, polybius_square_decoder, cipher_type_identifier]`

**TODO 3: Steganography Hunter Tools**
- Location: Line ~72
- Add: `[acrostic_detector, numeric_encoding_decoder, cipher_type_identifier]`

**TODO 4: Cipher Master Tools**
- Location: Line ~84
- Add: `[multi_layer_decoder, cipher_type_identifier]`

**TODO 5: Intelligence Analyst Tools**
- Location: Line ~116
- Add: `[cipher_type_identifier]`

**TODO 6: Swarm Agents List**
- Location: Line ~120
- Add: `[cipher_rookie, pattern_detective, steganography_hunter, cipher_master, intelligence_analyst]`

---

## Phase 2: Optional - Implement `common_algos.py`

**File:** `common_algos.py`

**Status:** OPTIONAL - Skip unless testing shows it's needed

All functions are marked with "# Todo, if you need it" comments. The AI agents can handle decryption through their system prompts without hardcoded algorithms.

**If needed, implement:**
- `atbash_cipher()` - A↔Z substitution
- `caesar_cipher()` - Shift cipher with configurable offset
- Other helper functions as required

---

## Phase 3: Deploy Agent to AWS

### 3.1 Navigate to Project Directory
```bash
cd /home/ubuntu/environment/GameDay/cipher-quest
```

### 3.2 Install Dependencies
```bash
pip install -r requirements.txt
```

### 3.3 Verify IAM Role Exists
The deployment script expects `CipherQuestExecutionRole` to exist. If not:
```bash
./create_role.sh
```

### 3.4 Run Deployment Script
```bash
./deploy_cipher_agents.sh
```

**What it does:**
- Creates Python virtual environment
- Installs all dependencies (boto3, bedrock-agentcore, strands-agents, etc.)
- Configures agentcore with entrypoint `cipher_command_agent.py`
- Launches agent to AWS
- Saves ARN to `cipher_quest_agent_arn.txt`

### 3.5 Test Agent (Optional)
```bash
# Test Caesar cipher
agentcore invoke '{"prompt": "Decrypt this: WKH TXLFN EURZQ IRA"}'

# Test Morse code
agentcore invoke '{"prompt": "Decode this: .... . .-.. .-.. ---"}'

# Test A1Z26
agentcore invoke '{"prompt": "Decode these numbers: 8 5 12 12 15"}'
```

### 3.6 Retrieve ARN for Scoring
```bash
# Option 1: Read from saved file
cat cipher_quest_agent_arn.txt

# Option 2: Describe agent
agentcore describe
```

### 3.7 Submit ARN
- Copy ARN from output
- Paste into GameDay quest interface
- Click "Ready for scoring"

---

## Success Criteria

✅ All TODOs completed in 5 agent files  
✅ No syntax errors in Python files  
✅ Agent deploys successfully via `agentcore launch`  
✅ ARN obtained from deployment  
✅ ARN submitted to GameDay interface  

---

## Key Implementation Notes

1. **Focus on System Prompts**: The AI agents use Bedrock Nova Pro model - clear instructions in system prompts are more important than hardcoded algorithms

2. **Tool Imports**: All tools are already imported at the top of `cipher_command_agent.py` - just need to assign them to correct agents

3. **Swarm Architecture**: cipher_master is the entry point, routes to specialists based on cipher type identification

4. **Agent Coordination**: Max 5 handoffs, 5 iterations, 3-minute timeout - designed for quick cipher resolution

5. **Testing Strategy**: Start with simple ciphers (Caesar, Morse) before complex multi-layer

---

## Estimated Timeline

| Phase | Task | Time |
|-------|------|------|
| 1.1-1.3 | Complete agent system prompts | 10 min |
| 1.4-1.5 | Add tools to agents | 5 min |
| 2 | Skip common_algos (optional) | 0 min |
| 3.1-3.4 | Deploy to AWS | 5 min |
| 3.5 | Test (optional) | 5 min |
| 3.6-3.7 | Get ARN and submit | 2 min |
| **TOTAL** | | **~25 min** |

---

## Troubleshooting

**If deployment fails:**
- Check AWS credentials: `aws sts get-caller-identity`
- Verify IAM role exists: `aws iam get-role --role-name CipherQuestExecutionRole`
- Check CloudWatch logs: Look for log group with 'agentcore' in name
- Review error messages in deployment script output

**If agent doesn't decrypt correctly:**
- Check CloudWatch logs for agent execution errors
- Verify system prompts have clear instructions
- Test with simple ciphers first
- Ensure tools are properly assigned to agents

---

## Ready to Proceed?

Once you approve this plan, I will:
1. Complete all TODOs in phases 1.1-1.5
2. Skip phase 2 (optional algorithms)
3. Prepare for phase 3 deployment

**Next Step:** Await your approval to begin implementation.
