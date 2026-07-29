import json
from openai import OpenAI
from google import genai
import streamlit as st
import os

API_KEY=os.getenv("GCP_API_KEY")

with open("optimization_results.json","r") as f:
    classical_optimization_results=json.load(f)

with open("quantum_optimization_results.json","r") as f:
    quantum_optimization_results=json.load(f)

client = genai.Client(api_key=API_KEY)

def portfolio_copilot(question,classical_optimization_results,quantum_optmization_results):
    """
    AI Portfolio Chatbot

    Parameters
    ----------
    question : str
        User's question.

    classical_results : dict
        Classical optimizer output.

    quantum_results : dict
        Quantum optimizer output.

    Returns
    -------
    str
        AI-generated answer.
    """

    system_prompt = """
    You are an AI Financial Portfolio Assistant.

    Your responsibilities are:
    - Explain portfolio optimization results.
    - Compare classical and quantum optimization.
    - Explain financial metrics clearly.
    - Never invent values.
    - Use only the supplied portfolio data.
    - If information is unavailable, say so.
    """

    user_prompt = f"""
    Classical Portfolio
    -------------------
    {classical_optimization_results}

    Quantum Portfolio
    -----------------
    {quantum_optimization_results}

    User Question
    -------------
    {question}
    """

    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=user_prompt
    )

    return response.text

def ai_copilot():

    if "copilot_open" not in st.session_state:
        st.session_state.copilot_open = False

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # -----------------------
    # Toggle Button
    # -----------------------

    st.markdown(
        """
        <style>

        .toggle-btn{
            position:fixed;
            top:90px;
            right:20px;
            z-index:999999;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([8, 1])

    with col2:

        if st.button("🤖 AI"):
            st.session_state.copilot_open = (
                not st.session_state.copilot_open
            )

    # -----------------------
    # Chat Window
    # -----------------------

    if st.session_state.copilot_open:

        st.markdown(
            '<div class="chat-panel">',
            unsafe_allow_html=True,
        )

        st.header("🤖 AI Copilot")

        st.divider()

        for msg in st.session_state.messages:

            with st.chat_message(msg["role"]):

                st.write(msg["content"])

        question = st.chat_input("Ask anything...")

        if question:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            classical_results = {}

            quantum_results = {}

            if "portfolio_data" in st.session_state:

                data = st.session_state["portfolio_data"]

                classical_results = data

                quantum_results = data

            answer = portfolio_copilot(
                question,
                classical_results,
                quantum_results
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

            st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )
