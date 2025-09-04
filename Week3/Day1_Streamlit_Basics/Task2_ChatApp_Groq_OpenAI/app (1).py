import os
import time
import streamlit as st
from typing import List, Dict

# Optional: use OpenAI or Groq (default: OpenAI)
LLM_PROVIDER = st.secrets.get("LLM_PROVIDER", "openai")  # "openai" or "groq"

# Lazy import of openai to avoid failing in environments without it installed until runtime
def get_openai_client():
    try:
        import openai
    except Exception as e:
        raise RuntimeError("openai package is required. Install from requirements.txt") from e
    return openai

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
if "generated" not in st.session_state:
    st.session_state.generated = []
if "user_inputs" not in st.session_state:
    st.session_state.user_inputs = []
if "is_streaming" not in st.session_state:
    st.session_state.is_streaming = False

st.set_page_config(page_title="Streamlit LLM Chat (Streaming)", layout="centered")

st.title("🗨️ Streamlit LLM Chat — Streaming Responses")
st.markdown(
    "This demo uses OpenAI's API (or Groq if configured) to stream assistant responses and stores chat history in `st.session_state`."
)

with st.sidebar:
    st.header("Settings")
    provider = st.selectbox("LLM Provider", options=["openai", "groq"], index=0)
    st.markdown("Make sure to set your API keys in Streamlit Cloud secrets or `st.secrets` when running locally.")
    if provider == "openai":
        st.caption("Set `OPENAI_API_KEY` in Streamlit secrets.")
    else:
        st.caption("Set `GROQ_API_KEY` in Streamlit secrets (not implemented in demo).")

def stream_openai_response(messages: List[Dict[str, str]]):
    """
    Streams response text from OpenAI's ChatCompletion API.
    This assumes the `openai` python package v0.27+.
    """
    openai = get_openai_client()
    openai.api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not openai.api_key:
        st.error("OPENAI_API_KEY not found in st.secrets or environment variables.")
        return ""

    # Create a placeholder for the streaming text
    placeholder = st.empty()
    # We'll accumulate the assistant reply here
    full_reply = ""

    try:
        # Using `stream=True` to get chunks progressively
        response_iter = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # change model as desired and available to your API key
            messages=messages,
            max_tokens=512,
            temperature=0.2,
            stream=True
        )

        for chunk in response_iter:
            # Each chunk is a dict — check for choices and delta
            if "choices" in chunk:
                for choice in chunk["choices"]:
                    delta = choice.get("delta", {})
                    content = delta.get("content")
                    if content:
                        full_reply += content
                        placeholder.markdown(f"**Assistant:** {full_reply}")
    except Exception as e:
        st.exception(e)
        return ""

    return full_reply

def on_send():
    user_input = st.session_state.input_text.strip()
    if not user_input:
        return
    # append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.user_inputs.append(user_input)
    st.session_state.input_text = ""  # clear text box

    st.session_state.is_streaming = True
    with st.spinner("Generating... (streaming)"):
        assistant_reply = stream_openai_response(st.session_state.messages)
    st.session_state.is_streaming = False

    if assistant_reply:
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        st.session_state.generated.append(assistant_reply)

# Chat UI
chat_container = st.container()
with chat_container:
    for i, msg in enumerate(st.session_state.messages):
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            continue
        if role == "user":
            st.markdown(f"**You:** {content}")
        elif role == "assistant":
            st.markdown(f"**Assistant:** {content}")

# Input box at bottom
st.text_input("Type your message", key="input_text", on_change=on_send, placeholder="Ask something...")

# Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Clear Chat"):
        st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
        st.session_state.generated = []
        st.session_state.user_inputs = []
with col2:
    st.write("")  # spacer

st.markdown("---")
st.caption("Tip: Set `OPENAI_API_KEY` in Streamlit secrets before deploying. This demo uses streaming from OpenAI ChatCompletion API.")