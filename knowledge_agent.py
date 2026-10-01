
from langchain_ollama import OllamaLLM

try:
    from rag_retriever import build_retriever, search_kb
except ImportError:
    from rag_retriever import build_retriever, search_kb


class KnowledgeAgent:
    
    def __init__(self, kb_path: str):
        print(f"\n Initializing Knowledge Agent...")
        self.retriever = build_retriever(kb_path)
        self.llm = OllamaLLM(model="mistral", temperature=0)
    
    def get_resolution(self, ticket_description: str, category: str) -> dict:
        kb_results = search_kb(self.retriever, ticket_description)
        
        prompt = f"""You are an IT Support specialist. Based on the KB articles below, provide resolution guidance.

TICKET CATEGORY: {category}
TICKET DESCRIPTION: {ticket_description}

RELEVANT KB ARTICLES:
{kb_results}

Based on the KB articles, provide:
1. IS_MATCH (Yes/No): Do the KB articles match this ticket?
2. RESOLUTION_STEPS (numbered list): Specific steps to resolve
3. SLA (estimated time): How long resolution should take
4. ESCALATION: If unresolved, who to contact

Format your response as:
IS_MATCH: [Yes/No]
RESOLUTION_STEPS:
1. [Step 1]
2. [Step 2]
...
SLA: [timeframe]
ESCALATION: [Team/Contact]"""
        
        response = self.llm.invoke(prompt)
        result = self._parse_resolution(response, kb_results)
        
        return result
    
    def _parse_resolution(self, response: str, kb_context: str) -> dict:
        result = {
            "kb_match": "Unknown",
            "resolution_steps": [],
            "sla": "4-8 hours",
            "escalation": "Support Team",
            "kb_context": kb_context,
        }
        
        lines = response.strip().split("\n")
        in_steps = False
        
        for line in lines:
            if line.startswith("IS_MATCH:"):
                result["kb_match"] = line.replace("IS_MATCH:", "").strip()
            elif line.startswith("RESOLUTION_STEPS:"):
                in_steps = True
            elif line.startswith("SLA:"):
                result["sla"] = line.replace("SLA:", "").strip()
                in_steps = False
            elif line.startswith("ESCALATION:"):
                result["escalation"] = line.replace("ESCALATION:", "").strip()
            elif in_steps and line.strip() and line[0].isdigit():
                result["resolution_steps"].append(line.strip())
        
        return result


if __name__ == "__main__":
    print("\n" + "-" * 70)
    print("Knowledge Agent Test")
    print("-" * 70)
    
    kb_agent = KnowledgeAgent("kb_documents.txt")
    
    test_cases = [
        ("VPN keeps disconnecting after update", "Network"),
        ("Can't access shared folder, permission denied", "Access"),
        ("Excel file won't open", "App"),
    ]
    
    for description, category in test_cases:
        print(f"\n Ticket: {description}")
        print(f"   Category: {category}")
        print("-" * 70)
        result = kb_agent.get_resolution(description, category)
        print(f"KB Match: {result['kb_match']}")
        print(f"SLA: {result['sla']}")
        print(f"Escalation: {result['escalation']}")
        print(f"Steps: {len(result['resolution_steps'])} steps provided")
        print()