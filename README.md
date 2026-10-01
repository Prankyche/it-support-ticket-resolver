README.md

# IT Support Ticket Resolver
## Multi-Agent AI System for Automated Support Ticket Processing

### Overview

This is a **4-agent multi-stage system** that automates IT support ticket resolution. It demonstrates enterprise-grade multi-agent AI orchestration using AutoGen, LangChain RAG, and local LLMs (Ollama).

**Architecture:**
```
Incoming Ticket
    → Triage Agent (classify + prioritize)
    → Knowledge Agent (retrieve resolution from KB via RAG)
    → Response Agent (draft professional response)
    → Critic Agent (quality review)
    → Final Response (ready to send)
```

### What It Does

1. **Triage Agent** — Classifies tickets into categories (Network, App, Access, Hardware) and assigns priority (P1-P3)
2. **Knowledge Agent** — Searches internal KB using RAG (FAISS embeddings) to find relevant resolution steps
3. **Response Agent** — Drafts professional email responses with step-by-step guidance and SLA
4. **Critic Agent** — Reviews responses for accuracy, tone, and completeness before sending

### Tech Stack

- **LLM:** Ollama (Mistral) — running locally at `localhost:11434`
- **Multi-agent orchestration:** AutoGen (GroupChat + GroupChatManager)
- **RAG:** LangChain + FAISS + HuggingFace embeddings
- **Language:** Python 3.10+

### Project Structure

```
ticket_resolver/
├── kb_documents.txt          # 15 IT issues + resolution steps
├── rag_retriever.py          # Load KB, embed, retrieve
├── triage_agent.py           # Classify + prioritize tickets
├── knowledge_agent.py        # RAG-powered KB search
├── response_agent.py         # Draft responses
├── critic_agent.py           # Quality review
├── main.py                   # AutoGen GroupChat orchestration
├── requirements.txt          # Python dependencies
├── sample_tickets.txt        # 5 test cases
└── README.md                 # This file
```

### Setup & Installation

#### 1. Prerequisites

- Python 3.10+
- Ollama installed and running (`ollama serve` at `localhost:11434`)
- Mistral model pulled: `ollama pull mistral`

#### 2. Install Dependencies

```bash
cd ticket_resolver
pip install -r requirements.txt
```

Dependencies:
```
langchain>=0.1.0
langchain-community>=0.0.10
langchain-ollama>=0.1.0
langchain-huggingface>=0.0.30
faiss-cpu>=1.7.4
pyautogen>=0.2.0
pypdf>=4.0.0
```

#### 3. Ensure Ollama is Running

In a separate terminal:
```bash
ollama serve
```

You should see:
```
Ollama is running at http://localhost:11434
```

### Usage

#### Option 1: Process a Single Ticket

```bash
python main.py --ticket "My VPN keeps disconnecting"
```

Output shows the complete GroupChat conversation between all 4 agents.

#### Option 2: Demo Mode (3 Sample Tickets)

```bash
python main.py --demo
```

Processes 3 representative tickets end-to-end.

#### Option 3: Step-by-Step Processing (Testing/Debugging)

```bash
python main.py --ticket "VPN disconnecting" --stepwise
```

Shows output from each agent individually:
- [1/4] Triage: Category, Priority, Summary
- [2/4] Knowledge: KB Match, SLA, Resolution Steps
- [3/4] Response: Draft email
- [4/4] Critic: Quality score + feedback

#### Option 4: Interactive Mode

```bash
python main.py --interactive
```

Prompts you to enter tickets one by one. Type `sample` to see examples, `quit` to exit.

### How It Works

#### Full GroupChat Flow (GroupChat Mode)

When you run with `--demo` or `--ticket`, the system uses **AutoGen's GroupChatManager** to orchestrate agents:

```
Admin (UserProxyAgent) initiates with ticket
    ↓
GroupChatManager selects next speaker using LLM
    ↓
Triage Agent analyzes ticket, responds
    ↓
Manager selects next speaker
    ↓
Knowledge Agent retrieves KB articles, responds
    ↓
Manager selects next speaker
    ↓
Response Agent drafts email, responds
    ↓
Manager selects next speaker
    ↓
Critic Agent reviews and approves/requests revisions
    ↓
Manager detects "TERMINATE" message, ends chat
```

Each agent sees the full conversation history and builds on previous agents' outputs.

#### Step-Wise Flow (Stepwise Mode)

When you run with `--stepwise`, agents are called individually in sequence:

```python
triage_result = triage.classify_ticket(ticket)
kb_result = kb_agent.get_resolution(ticket, triage_result['category'])
response_result = response_agent.draft_response(ticket_dict, kb_result)
critic_result = critic.review_response(ticket_dict, response_result, kb_result)
```

Better for testing/debugging because output is clearer and faster.

### Sample Output

**Input:**
```
"My VPN keeps disconnecting after the latest update"
```

**Output:**

```
[Triage Agent]
Category: Network
Priority: P1
Summary: VPN connection drops frequently after software update

[Knowledge Agent]
KB Match: Yes
Found: VPN Connection Drops Frequently
Resolution Steps: 3 steps
  1. Check VPN client version - update to latest
  2. Clear VPN cache: C:\ProgramData\Cisco\...
  3. Restart VPN service
SLA: 4 hours
Escalation: Network Team (ext. 5555)

[Response Agent]
Subject: Re: VPN Connection Issue - Immediate Resolution
Greeting: Dear Valued Employee,

Body: We've received your report about VPN disconnections following the recent update...

Steps:
1. Update your VPN client to the latest version
2. Clear the VPN cache folder
3. Restart the VPN service
4. Test your connection

SLA: We aim to resolve this within 4 hours.

[Critic Agent]
Status: APPROVED
Score: 9/10
Recommendation: ✓ APPROVED - Response is ready to send
Feedback: Clear instructions, professional tone, appropriate SLA
```

### Testing

#### Test Individual Agents

```bash
# Test Triage Agent
python triage_agent.py

# Test Knowledge Agent
python knowledge_agent.py

# Test RAG Retriever
python rag_retriever.py

# Test Response Agent
python response_agent.py

# Test Critic Agent
python critic_agent.py
```

#### Test with Sample Tickets

All sample tickets are in `sample_tickets.txt`:

```
1. VPN keeps disconnecting
2. Cannot access shared drive
3. Excel file won't open
4. Computer running slow
5. No network connection
```

Run demo:
```bash
python main.py --demo
```

### Architecture Details

#### Triage Agent

- **Input:** Raw ticket text
- **LLM:** Mistral (temperature=0, deterministic)
- **Output:** Category (Network/App/Access/Hardware), Priority (P1/P2/P3), Summary
- **No dependencies**

#### Knowledge Agent

- **Input:** Ticket text + category
- **LLM:** Mistral (temperature=0)
- **RAG:** FAISS vector store over KB documents
- **Embeddings:** HuggingFace all-MiniLM-L6-v2 (384-dim)
- **Output:** Resolution steps, SLA, escalation contact, KB context
- **Dependencies:** RAG Retriever

#### Response Agent

- **Input:** Ticket dict + KB results
- **LLM:** Mistral (temperature=0.5, creative but grounded)
- **Output:** Professional email with subject, greeting, body, steps, SLA, signature
- **Dependencies:** None

#### Critic Agent

- **Input:** Ticket dict + draft response + KB info
- **LLM:** Mistral (temperature=0)
- **Output:** Status (APPROVED/NEEDS_REVISION), quality score, feedback
- **Dependencies:** None

#### Main Orchestrator

- **Framework:** AutoGen
- **Pattern:** GroupChat + GroupChatManager
- **Speaker selection:** Auto (LLM decides who speaks next)
- **Termination:** When TERMINATE message detected
- **Max rounds:** 25 (safety limit)

### Key Design Decisions

1. **Why AutoGen over LangGraph?**
   - AutoGen is conversation-first, natural for multi-agent dialogue
   - LangGraph is state-first, better for strict workflows
   - This is agent collaboration → AutoGen

2. **Why local Ollama + Mistral?**
   - Zero OpenAI quota issues
   - Runs offline
   - Fast iteration
   - Production would use GPT-4

3. **Why FAISS + HuggingFace embeddings?**
   - Fast local embeddings (no API calls)
   - FAISS is extremely fast retrieval
   - Tradeoff: lower accuracy than OpenAI embeddings, but acceptable for demo

4. **Why GroupChat mode?**
   - Agents see each other's outputs
   - Emergent behavior (Response Agent knows what Triage decided)
   - More realistic multi-agent coordination

### Known Limitations

1. **Mistral reasoning:** Smaller model, occasionally hallucinates. Production would use GPT-4
2. **KB size:** Only 15 sample issues. Real systems have thousands
3. **Error handling:** Basic fallback for no KB match
4. **No persistent storage:** Responses not saved to database
5. **No email integration:** Responses are drafted but not sent

### Future Enhancements

- [ ] Integrate with real email API (send drafted responses)
- [ ] Add database storage for ticket history
- [ ] Build web UI (Streamlit/FastAPI)
- [ ] Add more KB articles (50+ issues)
- [ ] Use GPT-4 for production quality
- [ ] Add feedback loop (user rates response, improves KB)
- [ ] Implement ticket escalation workflow
- [ ] Add metrics dashboard (avg resolution time, satisfaction score)

### Running the Demo for Presentation

```bash
# Window 1: Start Ollama
ollama serve

# Window 2: Run demo
python main.py --demo

# Or interactive
python main.py --interactive
```

### Troubleshooting

**"Connection refused at localhost:11434"**
- Ensure Ollama is running: `ollama serve`

**"Module not found: langchain_..."**
- Install dependencies: `pip install -r requirements.txt`

**"No matching KB articles found"**
- Normal behavior if ticket doesn't match KB
- Agent will escalate to appropriate team

**Slow responses**
- Mistral model is downloading embeddings first time
- Subsequent queries are faster (cached)

**Agent loops forever**
- Increase max_round limit in main.py (line ~180)
- Or set lower max_round if you want faster demos

### Project Statistics

- **Lines of code:** ~1500 (6 agents + orchestrator)
- **KB articles:** 15 common IT issues
- **Agents:** 4 specialized roles
- **Processing stages:** 5 (triage → knowledge → response → critic → output)
- **Integration time:** ~2 weeks (Days 8-10)
- **Setup time:** ~5 minutes

### Credits & Learning

This system demonstrates:
- ✅ Week 1 LangChain fundamentals (LCEL chains, RAG)
- ✅ Week 1 LangGraph (state management, routing)
- ✅ Week 1 AutoGen (multi-agent conversations)
- ✅ Enterprise patterns (agent orchestration, quality gates)

Built as a capstone project for AI internship program.

### Contact & Questions

For questions or improvements, refer to inline code comments or the documentation in each agent module.

---

**Ready to go?** Run: `python main.py --demo`
