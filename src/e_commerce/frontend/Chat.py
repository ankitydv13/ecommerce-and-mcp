import streamlit as st
import asyncio

from e_commerce.MCPAdapter.agent import Agent

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = asyncio.run(Agent.create())

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask your agent"):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    response = asyncio.run(
        st.session_state.agent.ask(prompt)
    )

    # depends on what ask() returns
    if isinstance(response, dict):
        ai_response = response["messages"][-1].content
    else:
        ai_response = response

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_response
        }
    )

    with st.chat_message("assistant"):
        st.markdown(ai_response)
