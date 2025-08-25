# Streamlit LLM Chat (Streaming)

A minimal Streamlit chat app that demonstrates:
- Storing conversation in `st.session_state`.
- Streaming assistant responses from OpenAI's ChatCompletion API.
- Simple UI with a message input and chat history.

## Files
- `app.py` - main Streamlit app
- `requirements.txt` - Python dependencies

## Run locally (recommended)
1. Create a virtual environment and activate it.
2. Install requirements:
```bash
pip install -r requirements.txt
```
3. Set your OpenAI API key in environment:
```bash
export OPENAI_API_KEY="sk-..."
```
Or create a `.streamlit/secrets.toml` with:
```toml
OPENAI_API_KEY = "sk-..."
```

4. Run:
```bash
streamlit run app.py
```

## Deploy to Streamlit Cloud
1. Push this repository to GitHub.
2. On Streamlit Cloud, create a new app and connect your GitHub repo.
3. In the app settings, set the `OPENAI_API_KEY` in the Secrets section.
4. Deploy.

## Google Colab
This repo can be downloaded from GitHub or uploaded to Colab. To run Streamlit inside Colab, you can use `ngrok` or `localtunnel`. For production use, deploy on Streamlit Cloud.

## Notes & Limitations
- This example uses OpenAI's streaming API via `stream=True`. Make sure your API key has access to the chosen model.
- The `groq` provider is mentioned as an option but not implemented in streaming here.