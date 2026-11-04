import streamlit as st
import asyncio

from e_commerce.MCPAdapter.agent import Agent


# Create a single event loop
if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()

# Create the agent only once
if "agent" not in st.session_state:
    st.session_state.agent = (
        st.session_state.loop.run_until_complete(
            Agent.create()
        )
    )

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User prompt
if prompt := st.chat_input("Ask your agent"):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = (
            st.session_state.loop.run_until_complete(
                st.session_state.agent.ask(prompt)
            )
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        with st.chat_message("assistant"):
            st.markdown(response)

    except Exception as e:
        st.exception(e)