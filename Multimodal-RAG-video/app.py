import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

from src.ollama_chain import OllamaChain, OllamaRAGChain
from src.groq_chain import GroqChain, GroqRAGChain
from src.pdf_handler import extract_pdf
from src.vqa import answer_visual_question
from src.audio_processor import AudioProcessor
audio_processor = AudioProcessor()

from langchain_community.chat_message_histories import StreamlitChatMessageHistory

def load_chain(_chat_memory):
    use_groq = st.session_state.get('use_groq', False)
    
    # If PDF mode is active AND file is uploaded
    if st.session_state.get('pdf_chat') and st.session_state.get('uploaded_file'):
        if 'rag_chain' not in st.session_state or st.session_state.get('knowledge_change') or st.session_state.get('model_changed'):
            try:
                if use_groq:
                    st.session_state.rag_chain = GroqRAGChain(_chat_memory, st.session_state.uploaded_file)
                else:
                    st.session_state.rag_chain = OllamaRAGChain(_chat_memory, st.session_state.uploaded_file)
                st.session_state.knowledge_change = False
                st.session_state.model_changed = False
            except Exception as e:
                st.error(f"RAG Initialization Error: {e}")
                if use_groq:
                    return GroqChain(_chat_memory)
                return OllamaChain(_chat_memory)
        return st.session_state.rag_chain
    
    # Default direct chat
    if use_groq:
        return GroqChain(_chat_memory)
    return OllamaChain(_chat_memory)

def file_uploader_change():
    if 'rag_chain' in st.session_state:
        del st.session_state.rag_chain
    st.session_state.knowledge_change = True
    if st.session_state.uploaded_file:
        st.session_state.pdf_chat = True
    clear_cache()

def toggle_pdf_chat_change():
    clear_cache()
    st.session_state.knowledge_change = True

def toggle_model_change():
    if 'rag_chain' in st.session_state:
        del st.session_state.rag_chain
    st.session_state.model_changed = True
    clear_cache()

def clear_cache():
    st.cache_resource.clear()

def initial_session_state():
    if 'knowledge_change' not in st.session_state:
        st.session_state.knowledge_change = False
    if 'pdf_chat' not in st.session_state:
        st.session_state.pdf_chat = False
    if 'use_groq' not in st.session_state:
        st.session_state.use_groq = True  # Default to Groq for fast cloud inference
    if 'model_changed' not in st.session_state:
        st.session_state.model_changed = False
    if 'pending_query' not in st.session_state:
        st.session_state.pending_query = None
    os.makedirs('./.cache/temp_files', exist_ok=True)

def main():
    st.set_page_config(page_title="Multimodal RAG", page_icon="🤖", layout="wide")
    st.title('🤖 Multimodal RAG')
    st.markdown("Upload **PDF documents**, **images**, or **audio files** and chat with your multimodal AI assistant.")
    
    initial_session_state()
    chat_container = st.container()

    # Sidebar setup
    st.sidebar.title("🛠️ Settings & Uploads")
    
    # Model selector toggle
    st.sidebar.toggle('⚡ Use Groq Cloud (Fast & Accurate)', key='use_groq', on_change=toggle_model_change)
    st.sidebar.checkbox('🔊 Voice Output (Audio TTS)', value=False, key='enable_tts')
    
    model_name = "Groq (gpt-oss-20b)" if st.session_state.use_groq else "Ollama (llama3.1)"
    if st.session_state.pdf_chat and st.session_state.uploaded_file:
        st.sidebar.success(f"✅ RAG Active: {model_name}")
    else:
        st.sidebar.info(f"💬 Chat Mode: {model_name}")

    st.sidebar.toggle('📄 PDF Document Chat Mode', key='pdf_chat', on_change=toggle_pdf_chat_change)
    
    with st.sidebar.expander("📄 Document Upload (PDF)", expanded=True):
        st.file_uploader(
            'Upload PDF files',
            type='pdf',
            accept_multiple_files=True,
            key='uploaded_file',
            on_change=file_uploader_change
        )

    with st.sidebar.expander("🖼️ & 🎵 Media Upload", expanded=True):
        image_tab, audio_tab = st.tabs(["🖼️ Image / Camera", "🎵 Audio"])
        
        with image_tab:
            uploaded_image = st.file_uploader('Upload Image File', type=['jpg', 'jpeg', 'png'], key='uploaded_image')
            camera_image = st.camera_input('📷 Or Capture Live Photo', key='camera_image')
            
            # Active image is whichever was provided
            active_image = camera_image if camera_image is not None else uploaded_image
            
            if active_image:
                st.image(active_image, caption="Active Image (Auto-Enhanced for Clarity)", use_container_width=True)
                if st.button("🔍 Analyze Image", key="btn_analyze", use_container_width=True):
                    st.session_state.pending_query = "Describe this image in detail, extract any visible text or labels, and identify all key elements."

        with audio_tab:
            uploaded_audio = st.file_uploader('Upload Audio', type=['wav', 'mp3', 'm4a'], key='uploaded_audio')
            if uploaded_audio:
                st.audio(uploaded_audio)
                if st.button("🎙️ Transcribe & Ask Audio", key="btn_audio_ask", use_container_width=True):
                    st.session_state.pending_audio_ask = True

    chat_history = StreamlitChatMessageHistory(key='history')
    llm_chain = load_chain(chat_history)

    # Render previous messages
    with chat_container:
        for msg in chat_history.messages:
            st.chat_message(msg.type).write(msg.content)

    # Chat input
    chat_input_text = st.chat_input('Message Multimodal RAG...')

    # Determine what query needs to be processed
    user_query = None
    is_audio_query = False

    if chat_input_text:
        user_query = chat_input_text
    elif st.session_state.get('pending_query'):
        user_query = st.session_state.pop('pending_query')
    elif st.session_state.get('pending_audio_ask') and uploaded_audio:
        st.session_state.pending_audio_ask = False
        is_audio_query = True

    # Process query
    if user_query or is_audio_query:
        with chat_container:
            # Handle audio transcription if audio triggered
            if is_audio_query:
                audio_path = os.path.join('./.cache/temp_files', uploaded_audio.name)
                with open(audio_path, 'wb') as f:
                    f.write(uploaded_audio.getvalue())
                with st.spinner("🎙️ Transcribing audio with Groq Whisper..."):
                    transcribed_text = audio_processor.audio_to_text(audio_path)
                st.info(f"🎙️ **Transcribed Audio:** *\"{transcribed_text}\"*")
                user_query = transcribed_text

            st.chat_message('user').write(user_query)
            
            with st.spinner("Thinking..."):
                # If image is present and not an audio query
                if active_image and not is_audio_query:
                    image_filename = getattr(active_image, 'name', 'camera_capture.jpg')
                    image_path = os.path.join('./.cache/temp_files', image_filename)
                    with open(image_path, 'wb') as f:
                        f.write(active_image.getvalue())
                    
                    llm_response = answer_visual_question(image_path, user_query)
                    chat_history.add_user_message(user_query)
                    chat_history.add_ai_message(llm_response)
                else:
                    # Text or audio query passed to RAG / LLM chain
                    llm_response = llm_chain.run(user_input=user_query)
            
            st.chat_message('ai').write(llm_response)

            # Optional Text-to-Speech playback (disabled by default for instant text speed)
            if st.session_state.get('enable_tts', False):
                try:
                    with st.spinner("🔊 Generating voice audio..."):
                        audio_file = audio_processor.text_to_speech(llm_response)
                        if audio_file and os.path.exists(audio_file):
                            with open(audio_file, 'rb') as f:
                                st.audio(f.read(), format='audio/mp3')
                except Exception:
                    pass

if __name__ == '__main__':
    main()