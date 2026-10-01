
from langchain_ollama import OllamaLLM


class ResponseAgent:
    
    def __init__(self):
        self.llm = OllamaLLM(model="mistral", temperature=0.5)
    
    def draft_response(self, ticket: dict, kb_info: dict) -> dict:
        """
        Draft a professional response email.
        
        Args:
            ticket: Dict with keys: description, category, priority, summary
            kb_info: Dict with keys: kb_context, resolution_steps, sla, escalation
        
        Returns:
            Dict with keys: subject, greeting, body, resolution_steps_formatted, sla_statement, signature
        """
        priority_map = {
            "P1": "within 2 hours",
            "P2": "within 4 hours",
            "P3": "within 8 hours",
        }
        
        sla_time = priority_map.get(ticket.get("priority", "P2"), "within 4 hours")
        
        prompt = f"""You are a professional IT support email composer. Draft a response to this support ticket.

TICKET INFORMATION:
- Category: {ticket.get('category', 'General')}
- Priority: {ticket.get('priority', 'P2')}
- Summary: {ticket.get('summary', '')}
- Description: {ticket.get('description', '')}

RESOLUTION INFORMATION FROM KB:
{kb_info.get('kb_context', 'No specific KB articles found.')}

Resolution Steps:
{kb_info.get('sla', '4 hours')}

Escalation Path:
{kb_info.get('escalation', 'Support Team')}

TASK: Compose a professional, warm support response email with:
1. Personalized greeting
2. Acknowledgment of the issue
3. Step-by-step resolution (numbered list)
4. Expected timeframe/SLA
5. Escalation information if needed
6. Professional closing

Keep it under 200 words. Use clear, non-technical language. Be empathetic and solution-focused.

Format as:
SUBJECT: [email subject line]
GREETING: [Dear customer greeting]
BODY: [main response]
STEPS: [numbered resolution steps]
SLA: [timeframe statement]
SIGNATURE: [professional closing]"""
        
        response = self.llm.invoke(prompt)
        
        result = self._parse_response(response, sla_time)
        
        return result
    
    def _parse_response(self, response: str, sla_time: str) -> dict:
        result = {
            "subject": "Re: Your IT Support Request",
            "greeting": "Dear Valued Customer,",
            "body": "",
            "resolution_steps_formatted": "",
            "sla_statement": f"We aim to resolve this {sla_time}.",
            "signature": "Best regards,\nIT Support Team\nExt. 4444",
        }
        
        sections = {
            "SUBJECT": "subject",
            "GREETING": "greeting",
            "BODY": "body",
            "STEPS": "resolution_steps_formatted",
            "SLA": "sla_statement",
            "SIGNATURE": "signature",
        }
        
        lines = response.split("\n")
        current_section = None
        current_content = []
        
        for line in lines:
            section_found = False
            for section_key, result_key in sections.items():
                if line.startswith(section_key + ":"):
                    if current_section and current_content:
                        result[sections[current_section]] = "\n".join(current_content).strip()
                    current_section = section_key
                    current_content = [line.replace(section_key + ":", "").strip()]
                    section_found = True
                    break
            
            if not section_found and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            result[sections[current_section]] = "\n".join(current_content).strip()
        
        return result


if __name__ == "__main__":
    print("\n" + "-" * 70)
    print("Response Agent Test")
    print("-" * 70)
    
    response_agent = ResponseAgent()
    
    
    test_ticket = {
        "category": "Network",
        "priority": "P1",
        "summary": "VPN connection dropping frequently",
        "description": "My VPN keeps disconnecting after the latest update. This is impacting work.",
    }
    
    test_kb = {
        "kb_context": "VPN client version should be updated. Clear VPN cache. Restart VPN service.",
        "sla": "2 hours",
        "escalation": "Network Team (ext. 5555)",
    }
    
    print(f"\n Drafting response for: {test_ticket['summary']}")
    print("-" * 70)
    
    result = response_agent.draft_response(test_ticket, test_kb)
    
    print(f"Subject: {result['subject']}")
    print(f"\n{result['greeting']}\n")
    print(result['body'])
    print(f"\nResolution Steps:\n{result['resolution_steps_formatted']}")
    print(f"\n{result['sla_statement']}")
    print(f"\n{result['signature']}")
