
from langchain_ollama import OllamaLLM


class TriageAgent:
    
    def __init__(self):
        self.llm = OllamaLLM(model="mistral", temperature=0)
        self.categories = ["Network", "App", "Access", "Hardware"]
        self.priorities = ["P1", "P2", "P3"]
    
    def classify_ticket(self, ticket_description: str) -> dict:
        prompt = f"""You are an IT Support triage specialist. Analyze this ticket and classify it.

TICKET:
{ticket_description}

INSTRUCTIONS:
1. Determine the CATEGORY (must be one of: Network, App, Access, Hardware)
2. Assign PRIORITY:
   - P1: Critical/Urgent (affects business operations immediately)
   - P2: High (significant impact, can wait 1-4 hours)
   - P3: Medium (low impact, can wait up to 8 hours)
3. Write a brief SUMMARY (one sentence)

Respond in this EXACT format (no extra text):
CATEGORY: [Network|App|Access|Hardware]
PRIORITY: [P1|P2|P3]
SUMMARY: [One sentence summary]"""
        
        response = self.llm.invoke(prompt)
        
        result = self._parse_response(response)
        
        return result
    
    def _parse_response(self, response: str) -> dict:
        lines = response.strip().split("\n")
        
        category = "Hardware" 
        priority = "P2"  
        summary = ""
        
        for line in lines:
            if line.startswith("CATEGORY:"):
                cat = line.replace("CATEGORY:", "").strip()
                if cat in self.categories:
                    category = cat
            elif line.startswith("PRIORITY:"):
                pri = line.replace("PRIORITY:", "").strip()
                if pri in self.priorities:
                    priority = pri
            elif line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
        
        return {
            "category": category,
            "priority": priority,
            "summary": summary,
        }


if __name__ == "__main__":
    print("\n" + "-" * 70)
    print("Triage Agent Test")
    print("-" * 70)
    
    triage = TriageAgent()
    
    test_tickets = [
        "My VPN keeps disconnecting after the latest update. This is impacting JPMC transmission work.",
        "I can't access the shared drive \\\\server\\project_files. Getting permission denied error.",
        "Word document won't open. Getting error 0xc0000428. Urgent presentation today.",
    ]
    
    for ticket in test_tickets:
        print(f"\n Ticket: {ticket}")
        print("-" * 70)
        result = triage.classify_ticket(ticket)
        print(f"Category: {result['category']}")
        print(f"Priority: {result['priority']}")
        print(f"Summary: {result['summary']}")
        print()
