import google.generativeai as genai
import os
from typing import List, Dict
import json

class PFBot:
    def __init__(self, api_key: str):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
        
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')
        self.conversation_history: List[Dict] = []
        self.user_profile = {
            "pf_contribution": None,
            "service_years": None,
            "withdrawal_type": None,
            "previous_withdrawals": None,
            "current_balance": None
        }
        self.conversation_state = "initial"  # Track conversation flow
        self.pending_questions = []  # Questions to ask user
        self.system_prompt = """You are a friendly and knowledgeable Personal Finance (PF) Bot that helps users with their Provident Fund queries. 
        
        Your personality:
        - Be warm, conversational, and empathetic
        - Use "you" and "your" to make responses personal
        - Show understanding of their financial situation
        - Be encouraging and supportive
        - Use simple, clear language without jargon
        - Ask intelligent follow-up questions to gather missing information
        
        You should:
        1. Provide accurate and helpful financial advice based on EPFO rules
        2. Be clear and concise in your responses
        3. Consider the user's context and previous questions
        4. Maintain a professional yet friendly tone
        5. When unsure, ask for clarification rather than making assumptions
        6. Personalize responses based on their specific situation
        7. Proactively ask relevant questions to gather missing information
        
        Remember to:
        - Focus on personal finance topics, especially PF withdrawals
        - Provide practical and actionable advice
        - Consider different financial situations and contexts
        - Be mindful of financial regulations and best practices
        - Always mention specific amounts and eligibility criteria when possible
        - Ask one question at a time to avoid overwhelming the user
        """
        
    def _format_conversation_history(self) -> str:
        """Format conversation history for context."""
        formatted_history = ""
        for message in self.conversation_history:
            role = message["role"]
            content = message["content"]
            formatted_history += f"{role}: {content}\n"
        return formatted_history

    def _update_user_profile(self, user_input: str):
        """Update user profile based on conversation context."""
        # Extract PF contribution status
        if "contributing" in user_input.lower() or "employed" in user_input.lower():
            if "yes" in user_input.lower() or "still" in user_input.lower() or "active" in user_input.lower():
                self.user_profile["pf_contribution"] = "active"
            elif "no" in user_input.lower() or "not" in user_input.lower() or "unemployed" in user_input.lower():
                self.user_profile["pf_contribution"] = "inactive"
        
        # Extract years of service
        import re
        years_match = re.search(r'(\d+)\s*years?', user_input.lower())
        if years_match:
            self.user_profile["service_years"] = int(years_match.group(1))
        
        # Extract withdrawal type
        withdrawal_keywords = {
            "home loan": "home_loan_repayment",
            "house": "house_purchase",
            "medical": "medical_emergency",
            "education": "education",
            "marriage": "marriage",
            "unemployment": "unemployment",
            "renovation": "home_renovation",
            "retirement": "retirement"
        }
        
        for keyword, withdrawal_type in withdrawal_keywords.items():
            if keyword in user_input.lower():
                self.user_profile["withdrawal_type"] = withdrawal_type
                break
        
        # Extract previous withdrawals
        if "withdrawn" in user_input.lower() or "earlier" in user_input.lower():
            if "no" in user_input.lower() or "never" in user_input.lower():
                self.user_profile["previous_withdrawals"] = "none"
            else:
                self.user_profile["previous_withdrawals"] = "yes"

    def _determine_next_question(self) -> str:
        """Determine what question to ask next based on missing information."""
        missing_info = []
        
        if not self.user_profile["pf_contribution"]:
            missing_info.append("pf_contribution")
        if not self.user_profile["service_years"]:
            missing_info.append("service_years")
        if not self.user_profile["withdrawal_type"]:
            missing_info.append("withdrawal_type")
        
        if missing_info:
            if "pf_contribution" in missing_info:
                return "Are you currently employed and actively contributing to your PF?"
            elif "service_years" in missing_info:
                return "How long have you been contributing to your PF? (e.g., 5 years, 10 years)"
            elif "withdrawal_type" in missing_info:
                return "What's the purpose of your PF withdrawal? (e.g., home loan, medical emergency, education, etc.)"
        
        return None

    def get_response(self, user_input: str) -> str:
        # Update user profile based on input
        self._update_user_profile(user_input)
        
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Create a personalized prompt based on user profile
        profile_context = ""
        if self.user_profile["pf_contribution"]:
            profile_context += f"\n- PF Contribution Status: {self.user_profile['pf_contribution']}"
        if self.user_profile["service_years"]:
            profile_context += f"\n- Years of Service: {self.user_profile['service_years']} years"
        if self.user_profile["withdrawal_type"]:
            profile_context += f"\n- Withdrawal Type: {self.user_profile['withdrawal_type']}"
        if self.user_profile["previous_withdrawals"]:
            profile_context += f"\n- Previous Withdrawals: {self.user_profile['previous_withdrawals']}"
        
        # Determine if we have enough information for a complete answer
        has_sufficient_info = all([
            self.user_profile["pf_contribution"],
            self.user_profile["service_years"],
            self.user_profile["withdrawal_type"]
        ])
        
        next_question = self._determine_next_question()
        
        prompt = f"""
        You are a friendly and knowledgeable PF withdrawal assistant. The user is asking: "{user_input}"
        
        User Profile Context:{profile_context}
        
        Previous conversation context:
        {self._format_conversation_history()}
        
        Current Situation:
        - Has sufficient information for complete answer: {has_sufficient_info}
        - Next question to ask: {next_question if next_question else "None"}
        
        Instructions:
        1. Respond in a warm, conversational tone using "you" and "your"
        2. If you have enough information, provide a complete, personalized answer about their PF withdrawal eligibility
        3. If you need more information, ask the next question naturally in the conversation
        4. Always mention specific EPFO rules and eligibility criteria when possible
        5. Be encouraging and supportive in your tone
        6. Use bullet points or numbered lists for clarity when appropriate
        7. If mentioning amounts, use realistic examples (e.g., "up to ₹2-3 lakhs" for home loan withdrawal)
        8. If asking a question, make it feel natural and conversational, not like an interrogation
        
        Response Guidelines:
        - If you have sufficient info: Provide complete eligibility analysis with specific rules and amounts
        - If missing info: Acknowledge what you understand, then ask the next question naturally
        - Always be helpful and encouraging, regardless of their situation
        
        Remember: You're helping someone with their personal finances, so be empathetic and clear. Make them feel confident about their financial decisions.
        """
        
        try:
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            
            # Add bot response to history
            bot_response = response.text
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
            return bot_response
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

    def get_personalized_withdrawal_advice(self, user_answers: Dict) -> str:
        """Get personalized withdrawal advice based on user answers."""
        self.user_profile.update(user_answers)
        
        # Extract service years from the answer
        service_years = None
        if user_answers.get('service_years'):
            import re
            years_match = re.search(r'(\d+)\s*years?', user_answers['service_years'].lower())
            if years_match:
                service_years = int(years_match.group(1))
        
        # Determine withdrawal type
        withdrawal_type = user_answers.get('withdrawal_type', '').lower()
        is_home_loan = 'home loan' in withdrawal_type or 'loan' in withdrawal_type
        is_partial = 'partial' in withdrawal_type
        
        prompt = f"""
        Please answer in a short, friendly, and conversational tone (3-5 sentences max).
        Start with a clear eligibility statement based on the user's details.
        Briefly mention the specific EPFO rule that applies.
        End with a friendly nudge for the user to provide more details or ask a follow-up question.
        
        User's Profile:
        - PF Contribution: {user_answers.get('pf_contribution', 'Not specified')}
        - Service Years: {user_answers.get('service_years', 'Not specified')} ({service_years} years if specified)
        - Withdrawal Type: {user_answers.get('withdrawal_type', 'Not specified')}
        - Previous Withdrawals: {user_answers.get('previous_withdrawals', 'Not specified')}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        self.user_profile = {
            "pf_contribution": None,
            "service_years": None,
            "withdrawal_type": None,
            "previous_withdrawals": None,
            "current_balance": None
        }
        self.conversation_state = "initial"
        self.pending_questions = []

def main():
    # Get API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyCRnlynKAW40RS5AyfSC4G54q5ePufO3ec")
    if not api_key:
        print("Please set the GEMINI_API_KEY environment variable")
        return

    # Initialize the bot
    bot = PFBot(api_key)
    
    print("Welcome to the PF Bot! Type 'quit' to exit or 'clear' to clear conversation history.")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'clear':
            bot.clear_history()
            print("Conversation history cleared.")
            continue
            
        response = bot.get_response(user_input)
        print(f"\nPF Bot: {response}")

if __name__ == "__main__":
    main()
