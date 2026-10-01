
import argparse
import os
from typing import Optional
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

try:
    from triage_agent import TriageAgent
    from knowledge_agent import KnowledgeAgent
    from response_agent import ResponseAgent
    from critic_agent import CriticAgent
except ImportError as e:
    print(f"Warning: Could not import agents: {e}")
    print("Make sure all agent files are in the current directory")


config_list = [
    {
        "model": "mistral",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
    }
]


TRIAGE_SYSTEM = """You are an IT Support Triage Specialist. Your job is to:
1. Analyze the incoming support ticket
2. Classify it into one of: Network, App, Access, Hardware
3. Assign a priority: P1 (critical), P2 (high), P3 (medium)
4. Summarize the issue in one sentence

Be concise and precise. Respond with your classification and brief summary."""

KNOWLEDGE_SYSTEM = """You are an IT Support Knowledge Base Expert. Your job is to:
1. Receive the ticket classification from the Triage Agent
2. Search the knowledge base for relevant resolution steps
3. Extract and present: resolution steps, SLA, and escalation contact
4. Highlight any missing information that needs escalation

Be specific and cite exact steps from the KB."""

RESPONSE_SYSTEM = """You are a Professional Support Response Composer. Your job is to:
1. Receive ticket details and KB information
2. Draft a professional, empathetic email response
3. Include: issue acknowledgment, resolution steps, SLA, next steps
4. Keep tone warm but professional, language simple

Draft responses that are ready to send to users."""

CRITIC_SYSTEM = """You are a Quality Assurance Expert for Support Responses. Your job is to:
1. Review the drafted response email
2. Check: accuracy, tone, completeness, clarity
3. Approve if ready, or request revisions
4. Score the response 1-10 and explain

Be critical but constructive. Approve only if response is polished."""


def process_ticket_with_groupchat(ticket_description: str) -> dict:
    admin = UserProxyAgent(
        name="Admin",
        human_input_mode="NEVER",
        code_execution_config={"use_docker": False},
        is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
    )
    
    triage_agent = AssistantAgent(
        name="Triage",
        system_message=TRIAGE_SYSTEM,
        llm_config={"config_list": config_list, "temperature": 0},
    )
    
    knowledge_agent = AssistantAgent(
        name="Knowledge",
        system_message=KNOWLEDGE_SYSTEM,
        llm_config={"config_list": config_list, "temperature": 0},
    )
    
    response_agent = AssistantAgent(
        name="Response",
        system_message=RESPONSE_SYSTEM,
        llm_config={"config_list": config_list, "temperature": 0.5},
    )
    
    critic_agent = AssistantAgent(
        name="Critic",
        system_message=CRITIC_SYSTEM,
        llm_config={"config_list": config_list, "temperature": 0},
    )
    
    groupchat = GroupChat(
        agents=[admin, triage_agent, knowledge_agent, response_agent, critic_agent],
        messages=[],
        max_round=25,
        speaker_selection_method="auto",
    )
    
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config={"config_list": config_list},
    )
    
    print("-" * 70)
    print(f"\n Ticket: {ticket_description[:100]}...")
    print("\n" + "-" * 70)
    
    admin.initiate_chat(
        manager,
        message=f"""Process this IT support ticket through the entire workflow:

TICKET: {ticket_description}

Workflow:
1. Triage Agent: Classify ticket (category, priority, summary)
2. Knowledge Agent: Search KB for relevant resolution steps
3. Response Agent: Draft professional response email
4. Critic Agent: Review response for quality and accuracy

Final output should be a ready-to-send response email.

When complete, say "TERMINATE" to finish.""",
        max_turns=25,
    )
    
    print("\n" + "-" * 70)
    print(" Ticket processing complete")
    print("-" * 70)
    
    return {"status": "completed", "ticket": ticket_description}


def process_ticket_stepwise(ticket_description: str) -> dict:
    
    print("-" * 70)
    print("\nTriage Agent")
    print("-" * 70)
    triage = TriageAgent()
    triage_result = triage.classify_ticket(ticket_description)
    print(f"Category: {triage_result['category']}")
    print(f"Priority: {triage_result['priority']}")
    print(f"Summary: {triage_result['summary']}")
    
    print("\nKnowledge Agent")
    print("-" * 70)
    kb_agent = KnowledgeAgent("kb_documents.txt")
    kb_result = kb_agent.get_resolution(ticket_description, triage_result['category'])
    print(f"KB Match: {kb_result['kb_match']}")
    print(f"SLA: {kb_result['sla']}")
    print(f"Escalation: {kb_result['escalation']}")
    print(f"Steps: {len(kb_result['resolution_steps'])} provided")
    
    print("\nResponse Agent")
    print("-" * 70)
    response_agent = ResponseAgent()
    ticket_dict = {
        "description": ticket_description,
        "category": triage_result['category'],
        "priority": triage_result['priority'],
        "summary": triage_result['summary'],
    }
    response_result = response_agent.draft_response(ticket_dict, kb_result)
    print(f"Subject: {response_result['subject']}")
    print(f"Greeting: {response_result['greeting']}")
    print(f"Body: {response_result['body'][:500]}...")
    print("\nCritic Agent")
    print("-" * 70)
    critic = CriticAgent()
    critic_result = critic.review_response(ticket_dict, response_result, kb_result)
    print(f"Status: {critic_result['status']}")
    print(f"Score: {critic_result['quality_score']}/10")
    print(f"Recommendation: {critic_result['recommendation']}")
    print(f"Feedback: {critic_result['feedback']}")
    
    print("\n" + "-" * 70)
    
    return {
        "triage": triage_result,
        "kb": kb_result,
        "response": response_result,
        "critic": critic_result,
    }

SAMPLE_TICKETS = [
    "My VPN keeps disconnecting after the latest update. This is impacting JPMC transmission work.",
    "I can't access the shared drive \\\\server\\project_files. Getting permission denied error.",
    "Word document won't open. Getting error 0xc0000428. Urgent presentation today.",
    "Computer is running very slow. Task Manager shows 95% CPU usage. Office files won't load.",
    "Cannot connect to network. No internet. Ethernet cable is connected. Red X icon showing.",
]

def main():
    parser = argparse.ArgumentParser(description="IT Support Ticket Resolver - 4 Agent System")
    parser.add_argument("--ticket", type=str, help="Process a single ticket")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode - enter tickets manually")
    parser.add_argument("--demo", action="store_true", help="Run demo with sample tickets")
    parser.add_argument("--stepwise", action="store_true", help="Process with step-by-step output (testing)")
    
    args = parser.parse_args()
    
    print("\n" + "-" * 70)
    print("IT SUPPORT TICKET RESOLVER")
    print("4-Agent Multi-Stage Processing System")
    print("-" * 70)
    
    if args.ticket:
        if args.stepwise:
            process_ticket_stepwise(args.ticket)
        else:
            process_ticket_with_groupchat(args.ticket)
    
    elif args.demo:
        print("\n DEMO MODE: Processing 2 sample tickets\n")
        for i, ticket in enumerate(SAMPLE_TICKETS[:2], 1):
            print(f"\n{'-'*70}")
            print(f"TICKET {i}/2")
            print(f"{'-'*70}")
            if args.stepwise:
                process_ticket_stepwise(ticket)
            else:
                process_ticket_with_groupchat(ticket)
    
    elif args.interactive:
        print("\n INTERACTIVE MODE")
        print("Enter support tickets (type 'quit' to exit)\n")
        
        while True:
            print("\n" + "-" * 70)
            ticket = input("Enter ticket description (or 'sample' for examples): ").strip()
            
            if ticket.lower() == "quit":
                print("Goodbye!")
                break
            
            if ticket.lower() == "sample":
                print("\nSample tickets:")
                for i, t in enumerate(SAMPLE_TICKETS, 1):
                    print(f"  {i}. {t}")
                continue
            
            if not ticket:
                continue
            
            if args.stepwise:
                process_ticket_stepwise(ticket)
            else:
                process_ticket_with_groupchat(ticket)
    
    else:
        print("\nUsage:")
        print("  python main.py --ticket \"Your ticket description\"")
        print("  python main.py --demo                    # Run demo with 3 sample tickets")
        print("  python main.py --interactive             # Enter tickets interactively")
        print("  python main.py --ticket \"...\" --stepwise # Show step-by-step processing")
        print("\nExample:")
        print("  python main.py --ticket \"VPN keeps disconnecting\"")
        print("  python main.py --demo --stepwise")


if __name__ == "__main__":
    main()