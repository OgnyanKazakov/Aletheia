import streamlit as st
import ollama
from langchain_community.llms import Ollama

def initialize_model(model_name="llama3.1:8b"):
    "Initialize the code nodel"""

    return Ollama(nodel=model_name)

initialize_model()

st.title("Alethia")

#initialize model

if "model" not in st.session_state:
    st.session_state.model = "llama3.1:8b"

if "messages" not in st.session_state:

    st.session_state.messages = []

for message in st.session_state["messages"]:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

#user input
if user_prompt := st.chat_input("Put your news here:"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown (user_prompt)

    #generate responses
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        for chunk in ollama.chat(
            model=st.session_state.model,
            messages=[
                {"role": ["role"], "content": ["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            token = chunk["message"]["content"]
            if token is not None:
                full_response += token
                message_placeholder.markdown(full_response + " ")

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})