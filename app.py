import streamlit as st
from Work import PFBot
import os

st.set_page_config(page_title="PF Bot", page_icon="💬", layout="wide")

quick_answers = {
    "Unemployment": "**Unemployment**\n\n- **Eligibility:** After 1 month of unemployment.\n- **Amount:** 75% of the PF balance after 1 month. 100% after 2 months.\n- **Condition:** Must have worked for more than 1 month in the previous job.",
    "Education (Self or Children)": "**Education (Self or Children)**\n\n- **Eligibility:** 7 years of contribution to EPF.\n- **Amount:** 50% of the employee's contribution for higher education or children's education after Class 10.\n- **Condition:** Must provide institution certificate for course details.",
    "Marriage (Self, Son, Daughter, Sibling)": "**Marriage (Self, Son, Daughter, Sibling)**\n\n- **Eligibility:** 7 years of contribution to EPF.\n- **Amount:** 50% of the employee's contribution for marriage expenses.\n- **Condition:** For self, son, daughter, brother, sister only.",
    "Medical Emergency (Self or Family)": "**Medical Emergency (Self or Family)**\n\n- **Eligibility:** No minimum service period required.\n- **Amount:** 6 months of basic wages or employee share with interest (whichever is lesser).\n- **Condition:** Applicable for both self and family treatment.",
    "Specially-abled Individuals": "**Specially-abled Individuals**\n\n- **Eligibility:** No minimum service period required.\n- **Amount:** 6 months of basic wages or employee share with interest (whichever is lesser) for purchasing equipment for disability.\n- **Condition:** Requires doctor's certificate for eligibility.",
    "Home Loan Repayment": "**Home Loan Repayment**\n\n- **Eligibility:** 10 years of contribution to EPF.\n- **Amount:** 36 months of basic wages + DA or total of employee and employer share (whichever is lesser) for paying home loan EMIs.\n- **Condition:** Available only after 10 years of service.",
    "Purchase of House/Flat or Land Plot": "**Purchase of House/Flat or Land Plot**\n\n- **Eligibility:** 5 years of contribution to EPF.\n- **Amount:** 24 months of basic wages and DA for site purchase or 36 months of basic wages and DA for house purchase/flat cost/property or total contribution.\n- **Condition:** The amount withdrawn should be the lesser of employee + employer share, property cost, or total contribution.",
    "Home Renovation": "**Home Renovation**\n\n- **Eligibility:** 5 years of contribution to EPF.\n- **Amount:** 12 months of basic wages and DA, or employee share with interest (whichever is lesser) for home renovation/expansion.\n- **Condition:** Available 2 times: once after 5 years of property completion and again after 10 years.",
    "Retirement (Within 1 Year of Retirement)": "**Retirement (Within 1 Year of Retirement)**\n\n- **Eligibility:** 54 years of age and within 1 year of retirement/superannuation.\n- **Amount:** 90% of the PF balance (whichever is lesser).\n- **Condition:** Can be done within 1 year before retirement.",
    "Death of Employee (Nominee)": "**Death of Employee (Nominee)**\n\n- **Eligibility:** No minimum service period required.\n- **Amount:** Full PF balance transferred to nominee.\n- **Condition:** Form 20 for settlement, Form 10D for monthly pension.",
    "Other Emergencies (Natural Calamities, etc.)": "**Other Emergencies (Natural Calamities, etc.)**\n\n- **Eligibility:** NA\n- **Amount:** Full Employee share with interest for calamity-related emergencies.\n- **Condition:** Affected by natural disasters like earthquakes, floods."
}

quick_cards = list(quick_answers.keys())
all_cards = quick_cards

greeting = (
    "Hi there! 👋 I'm your personal PF assistant. Please answer a few questions to get a personalized answer."
)

if 'bot' not in st.session_state:
    api_key = os.getenv("GEMINI_API_KEY", "")
    st.session_state.bot = PFBot(api_key)
if 'history' not in st.session_state:
    st.session_state.history = []
if 'personalized_done' not in st.session_state:
    st.session_state.personalized_done = False
if 'chat_input' not in st.session_state:
    st.session_state.chat_input = ""
if 'last_card_clicked' not in st.session_state:
    st.session_state['last_card_clicked'] = None

def send_message():
    user_input = st.session_state.chat_input.strip()
    if user_input:
        st.session_state.history.append({'role': 'user', 'content': user_input})
        response = st.session_state.bot.get_response(user_input)
        st.session_state.history.append({'role': 'assistant', 'content': response})
        st.session_state.chat_input = ""

st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif !important;
        background: #181a20 !important;
    }
    .pf-section-title {
        font-size: 1.12em;
        font-weight: 700;
        margin: 10px 0 8px 0;
        color: #90caf9;
        letter-spacing: 0.01em;
    }
    .pf-chat-outer {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        margin-bottom: 0;
    }
    .pf-chat-area {
        width: 100%;
        max-width: 540px;
        min-height: 80px;
        max-height: 320px;
        overflow-y: auto;
        background: transparent;
        border-radius: 0;
        border: none;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .pf-chat-user {
        display: flex;
        justify-content: flex-end;
        margin: 0.2em 0;
    }
    .pf-chat-bot {
        display: flex;
        justify-content: flex-start;
        margin: 0.2em 0;
    }
    .pf-bubble-user {
        background: #1976d2;
        color: #fff;
        padding: 10px 16px;
        border-radius: 18px 18px 6px 18px;
        max-width: 80%;
        min-width: 40px;
        box-shadow: 0 1px 4px rgba(25,118,210,0.10);
        font-size: 1em;
        font-weight: 500;
        word-break: break-word;
        white-space: pre-line;
        display: inline-block;
    }
    .pf-bubble-bot {
        background: #23272f;
        color: #fff;
        padding: 10px 16px;
        border-radius: 18px 18px 18px 6px;
        max-width: 80%;
        min-width: 40px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.10);
        font-size: 1em;
        font-weight: 500;
        word-break: break-word;
        white-space: pre-line;
        display: inline-block;
        border: 1px solid #23272f;
    }
    .pf-chat-input-bar {
        background: #23272f;
        border-radius: 18px;
        padding: 6px 10px;
        border: 1.5px solid #23272f;
        width: 100%;
        max-width: 540px;
        display: flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.10);
        margin-top: 0.5em;
    }
    .pf-chat-input {
        border: none;
        outline: none;
        flex: 1;
        font-size: 1em;
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
        background: transparent;
        color: #fff;
    }
    input.pf-chat-input::placeholder {
        color: #b0b8c1;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Welcome 👋")

# --- Personalization Form (always at the top) ---
if not st.session_state.personalized_done:
    st.markdown(f"<div class='pf-section-title'>🤖 {greeting}</div>", unsafe_allow_html=True)
    with st.expander("Answer a few questions to get a personalized PF withdrawal answer:", expanded=True):
        q1 = st.selectbox("Are you actively contributing to your PF?", ["Yes, I'm still employed and contributing to my PF.", "No, I'm not contributing currently."])
        q2 = st.text_input("What's your service history? How long have you been contributing to your PF?", "")
        q3 = st.text_input("What do you want to withdraw from your Provident Fund? (Full or Partial Withdrawal)", "")
        q4 = st.text_input("Have you ever withdrawn PF earlier? If yes, under which category?", "")
        submitted = st.button("Get my personalized answer", key="submit_personal")
        if submitted:
            user_answers = {
                'pf_contribution': q1,
                'service_years': q2,
                'withdrawal_type': q3,
                'previous_withdrawals': q4
            }
            st.session_state.history = []
            response = st.session_state.bot.get_personalized_withdrawal_advice(user_answers)
            st.session_state.history.append({'role': 'assistant', 'content': response})
            st.session_state.personalized_done = True
            st.rerun()

# --- Chat Area (only after personalized answer) ---
if st.session_state.personalized_done:
    st.markdown("<div class='pf-chat-outer'>", unsafe_allow_html=True)
    st.markdown("<div class='pf-chat-area'>", unsafe_allow_html=True)
    for entry in st.session_state.history:
        if entry['role'] == 'user':
            st.markdown(f"<div class='pf-chat-user'><div class='pf-bubble-user'>🧑 {entry['content']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='pf-chat-bot'><div class='pf-bubble-bot'>🤖 {entry['content']}</div></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Chat Input Bar (no send button, Enter to send) ---
    st.markdown("<div class='pf-chat-input-bar'>", unsafe_allow_html=True)
    st.text_input(
        "Ask me anything about your PF withdrawal...",
        key="chat_input",
        placeholder="Type your question here...",
        label_visibility="collapsed",
        on_change=send_message
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Clear Chat Button ---
    if st.button("Clear Chat History", key="clear_chat"):
        st.session_state.history = []
        st.session_state.bot.clear_history()
        st.session_state.personalized_done = False
        st.rerun()

# --- Quick Reference Section ---
with st.expander("📋 Quick Reference - PF Withdrawal Types", expanded=False):
    st.markdown("<div class='pf-section-title'>Quick Actions</div>", unsafe_allow_html=True)
    num_cols = 3
    rows = [all_cards[i:i+num_cols] for i in range(0, len(all_cards), num_cols)]
    card_clicked = None
    for row in rows:
        cols = st.columns(num_cols, gap="small")
        for i, card in enumerate(row):
            with cols[i]:
                if st.button(card, key=f"purpose_{card}", help=card):
                    card_clicked = card
                    st.session_state['last_card_clicked'] = card
                    st.rerun()
if st.session_state.get('last_card_clicked'):
    card_clicked = st.session_state['last_card_clicked']
    st.session_state.history.append({'role': 'user', 'content': f"Tell me about {card_clicked}"})
    st.session_state.history.append({'role': 'assistant', 'content': quick_answers[card_clicked]})
    st.session_state['last_card_clicked'] = None
    st.rerun()