# Multimodal RAG Streamlit Demo with Modern UI/UX
import streamlit as st

# ------------------------------------------------------------
# Page configuration – dark theme and wide layout
# ------------------------------------------------------------
st.set_page_config(
    page_title="Multimodal RAG Demo",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# Inject custom CSS for a premium look (glassmorphism, gradient, fonts)
# ------------------------------------------------------------
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        /* Global styling */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #e0e0e0;
        }
        .card {
            background: rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            backdrop-filter: blur(8px);
            box-shadow: 0 4px 30px rgba(0,0,0,0.5);
        }
        .card h4 {
            margin-top: 0;
            color: #fff;
        }
        .stButton > button {
            background: linear-gradient(90deg, #ff8a00, #e52e71);
            border: none;
            color: #fff;
            font-weight: 600;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: transform 0.2s;
        }
        .stButton > button:hover {
            transform: scale(1.03);
        }
        /* Chat bubbles */
        .chat-container {display: flex; flex-direction: column;}
        .chat-bubble {border-radius: 12px; padding: 0.8rem 1rem; margin: 0.5rem 0; max-width: 70%;}
        .user {background: #4e5d78; color: #fff; align-self: flex-end;}
        .assistant {background: #2c3e50; color: #e0e0e0; align-self: flex-start;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------
st.markdown("""<h1 style='text-align: center; font-weight: 700;'>🎬 Multimodal RAG Demo</h1>""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Sidebar – file upload area with a card style
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='card'><h4>Upload Inputs</h4>", unsafe_allow_html=True)
    pdf_file = st.file_uploader("📄 PDF", type=["pdf"])
    audio_file = st.file_uploader("🎧 Audio (wav/mp3)", type=["wav", "mp3"])
    img_file = st.file_uploader("🖼️ Image for VQA", type=["png", "jpg", "jpeg"])
    if st.button("Process"):
        st.session_state.process = True
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Main content – show uploaded files using the card component
# ------------------------------------------------------------
if st.session_state.get("process"):
    st.markdown("<div class='card'><h4>🗂️ Uploaded Files</h4>", unsafe_allow_html=True)
    if pdf_file:
        st.success(f"PDF: {pdf_file.name} ({len(pdf_file.getvalue())/1024:.1f} KB)")
    if audio_file:
        st.success(f"Audio: {audio_file.name} ({len(audio_file.getvalue())/1024:.1f} KB)")
    if img_file:
        st.success(f"Image: {img_file.name} ({len(img_file.getvalue())/1024:.1f} KB)")
    st.info("🛠️ Here you would invoke the backend processing functions (PDF extraction, transcription, VQA, etc.)")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Chat interface – styled bubbles
# ------------------------------------------------------------
st.markdown("<div class='card'><h4>💬 Chat with AI</h4>", unsafe_allow_html=True)
if "messages" not in st.session_state:
    st.session_state.messages = []

prompt = st.chat_input("Ask a question about your documents …")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Placeholder – replace with real LLM call
    response = f"(Mock) Answer to: {prompt}"
    st.session_state.messages.append({"role": "assistant", "content": response})

# Render chat history with custom HTML bubbles
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    bubble_class = "user" if role == "user" else "assistant"
    st.markdown(
        f"""
        <div class='chat-bubble {bubble_class}'>
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

