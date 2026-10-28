import re

from agents.base_agent import BaseAgent


class SecurityAgent(BaseAgent):

    async def run(self, input_data):

        email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'

        phone_pattern = r'\b\d{10}\b'

        emails = re.findall(
            email_pattern,
            input_data
        )

        phones = re.findall(
            phone_pattern,
            input_data
        )

        suspicious_phrases = [
            "ignore previous instructions",
            "reveal system prompt",
            "forget your role"
        ]

        prompt_attack = any(
            phrase.lower() in input_data.lower()
            for phrase in suspicious_phrases
        )

        security_score = 100

        if emails:
            security_score -= 10

        if phones:
            security_score -= 10

        if prompt_attack:
            security_score -= 30

        return {
            "security_score": security_score,
            "emails_found": len(emails),
            "phones_found": len(phones),
            "prompt_attack": prompt_attack
        }