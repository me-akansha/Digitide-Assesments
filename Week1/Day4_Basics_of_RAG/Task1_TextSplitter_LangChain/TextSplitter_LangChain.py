import streamlit as st
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tempfile
import os
import pandas as pd
import time

# Streamlit Page Config
st.set_page_config(
    page_title="📄 AI Document Chunker",
    page_icon="✂️",
    layout="centered",
)

# Title and subtitle
st.title("✂️ Chunkify – AI-Ready Document Splitter")
st.markdown("Upload a `.txt` or `.pdf` file, and I’ll split it into AI-friendly chunks.")

# File uploader
uploaded_file = st.file_uploader("📂 Upload your file", type=["txt", "pdf"])

# Chunk size controls
chunk_size = st.slider("📏 Chunk Size (characters)", 500, 3000, 1000, 100)
chunk_overlap = st.slider("🔄 Chunk Overlap (characters)", 0, 500, 200, 50)

if uploaded_file:
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name

    # Load the file
    if uploaded_file.name.endswith(".txt"):
        loader = TextLoader(temp_path, encoding="utf-8")
    elif uploaded_file.name.endswith(".pdf"):
        loader = PyPDFLoader(temp_path)
    else:
        st.error("❌ Unsupported file type")
        st.stop()

    st.info("⏳ Loading document...")
    documents = loader.load()

    # Progress bar
    progress = st.progress(0)
    time.sleep(0.5)  # Small delay for smooth animation

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    st.info("✂️ Splitting document into chunks...")
    docs = splitter.split_documents(documents)

    # Simulate progress bar filling
    for i in range(100):
        time.sleep(0.005)
        progress.progress(i + 1)

    st.success(f"✅ Document split successfully into **{len(docs)}** chunks!")

    # Convert chunks to DataFrame
    chunk_data = [{"Chunk #": i + 1, "Content": chunk.page_content} for i, chunk in enumerate(docs)]
    df_chunks = pd.DataFrame(chunk_data)

    # Preview first few chunks
    with st.expander("📜 Preview First Few Chunks"):
        for i, row in df_chunks.head(5).iterrows():
            st.markdown(f"**Chunk {row['Chunk #']}**")
            st.write(row["Content"])
            st.markdown("---")

    # Download buttons
    st.download_button(
        label="💾 Download as CSV",
        data=df_chunks.to_csv(index=False).encode("utf-8"),
        file_name="document_chunks.csv",
        mime="text/csv",
    )

    st.download_button(
        label="💾 Download as JSON",
        data=df_chunks.to_json(orient="records", indent=2).encode("utf-8"),
        file_name="document_chunks.json",
        mime="application/json",
    )

    # Cleanup temp file
    os.remove(temp_path)
