from langchain_ollama import OllamaLLM


class CriticAgent:
    
    def __init__(self):
        self.llm = OllamaLLM(model="mistral", temperature=0)
    
    def review_response(self, ticket: dict, draft_response: dict, kb_info: dict) -> dict:
        prompt = f"""You are a quality assurance expert for IT support responses. Review this draft response.

ORIGINAL TICKET:
{ticket.get('description', '')}

CATEGORY: {ticket.get('category', '')}
PRIORITY: {ticket.get('priority', '')}

DRAFT RESPONSE:
Subject: {draft_response.get('subject', '')}
Body: {draft_response.get('body', '')}
Steps: {draft_response.get('resolution_steps_formatted', '')}
SLA: {draft_response.get('sla_statement', '')}

KB INFORMATION USED:
{kb_info.get('kb_context', 'No KB articles')}

EVALUATION CRITERIA:
1. Accuracy: Are the steps technically correct based on KB?
2. Tone: Is it professional, empathetic, and helpful?
3. Completeness: Does it address the original issue?
4. Clarity: Is it easy to follow?
5. SLA: Is the timeframe appropriate for the priority?

Provide:
1. OVERALL_STATUS: APPROVED or NEEDS_REVISION
2. QUALITY_SCORE: 1-10
3. STRENGTHS: What's good about this response
4. FEEDBACK: Any issues or concerns
5. IMPROVEMENTS: Specific suggestions if revision needed

Format exactly as shown above."""
        
        response = self.llm.invoke(prompt)
        
        result = self._parse_review(response)
        
        return result
    
    def _parse_review(self, response: str) -> dict:
        result = {
            "status": "APPROVED",
            "quality_score": 8,
            "strengths": "",
            "feedback": "",
            "improvements": "",
            "recommendation": "Response is ready to send.",
        }
        
        lines = response.split("\n")
        
        for line in lines:
            if "OVERALL_STATUS:" in line:
                status = line.split("OVERALL_STATUS:")[-1].strip().upper()
                result["status"] = "APPROVED" if "APPROV" in status else "NEEDS_REVISION"
            
            elif "QUALITY_SCORE:" in line:
                try:
                    score_text = line.split("QUALITY_SCORE:")[-1].strip()
                    score = int(score_text.split()[0])
                    result["quality_score"] = min(10, max(1, score))
                except:
                    pass
            
            elif "STRENGTHS:" in line:
                result["strengths"] = line.split("STRENGTHS:")[-1].strip()
            
            elif "FEEDBACK:" in line:
                result["feedback"] = line.split("FEEDBACK:")[-1].strip()
            
            elif "IMPROVEMENTS:" in line:
                result["improvements"] = line.split("IMPROVEMENTS:")[-1].strip()
        
        if result["status"] == "APPROVED":
            result["recommendation"] = f"APPROVED (Score: {result['quality_score']}/10) - Ready to send"
        else:
            result["recommendation"] = f"NEEDS_REVISION (Score: {result['quality_score']}/10) - See feedback above"
        
        return result


if __name__ == "__main__":
    print("\n" + "-" * 70)
    print("Critic Agent Test")
    print("-" * 70)
    
    critic = CriticAgent()
    test_ticket = {
        "category": "Network",
        "priority": "P1",
        "description": "VPN keeps disconnecting after latest update",
    }
    
    test_draft = {
        "subject": "Re: VPN Disconnection Issue",
        "body": "We've received your report about VPN disconnections. This is likely due to a cache issue with the latest update.",
        "resolution_steps_formatted": "1. Update VPN client\n2. Clear VPN cache\n3. Restart VPN service\n4. Restart computer",
        "sla_statement": "We aim to resolve this within 2 hours.",
    }
    
    test_kb = {
        "kb_context": "VPN update causes cache corruption. Standard fix: clear cache, restart service.",
    }
    
    print(f"\n Reviewing response for: {test_ticket['category']} issue (Priority: {test_ticket['priority']})")
    print("-" * 70)
    
    result = critic.review_response(test_ticket, test_draft, test_kb)
    
    print(f"\n{result['recommendation']}")
    print(f"\nStrengths: {result['strengths']}")
    print(f"Feedback: {result['feedback']}")
    if result['improvements']:
        print(f"Improvements: {result['improvements']}")
