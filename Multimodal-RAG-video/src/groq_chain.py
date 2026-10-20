from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.memory import ConversationBufferWindowMemory
from src.utils import load_config
from src.vectorstore import VectorDB

import os

class GroqChain:
    """Simple chat chain using Groq API — high accuracy, low latency."""
    def __init__(self, chat_memory) -> None:
        config = load_config()
        groq_config = config.get('groq_model', {})
        
        prompt = PromptTemplate(
            template="""You are an accurate, helpful AI assistant. Answer clearly and factually.
Conversation History:
{chat_history}

User Question: {input}
Answer:""",
            input_variables=['chat_history', 'input']
        )
        self.memory = ConversationBufferWindowMemory(
            memory_key='chat_history', chat_memory=chat_memory, k=4, return_messages=True
        )
        
        llm = ChatGroq(
            model=groq_config.get('model', 'openai/gpt-oss-20b'),
            temperature=groq_config.get('temperature', 0.2),
            api_key=os.environ.get('GROQ_API_KEY')
        )
        
        from langchain_classic.chains import LLMChain
        self.llm_chain = LLMChain(prompt=prompt, llm=llm, memory=self.memory, output_parser=StrOutputParser())
        self.chat_memory = chat_memory

    def run(self, user_input):
        try:
            return self.llm_chain.invoke({"input": user_input})['text']
        except Exception as e:
            # Fallback to local Ollama if offline or Groq times out
            from src.ollama_chain import OllamaChain
            print(f"[Fallback] Groq failed ({e}), switching to local Ollama...")
            fallback = OllamaChain(self.chat_memory)
            return fallback.run(user_input)


class GroqRAGChain:
    """RAG chain using Groq API tuned for maximum factual retrieval accuracy."""
    def __init__(self, chat_memory, uploaded_file=None):
        config = load_config()
        groq_config = config.get('groq_model', {})
        
        self.chat_memory = chat_memory
        self.llm = ChatGroq(
            model=groq_config.get('model', 'openai/gpt-oss-20b'),
            temperature=groq_config.get('temperature', 0.2),
            api_key=os.environ.get('GROQ_API_KEY')
        )
        self.vector_db = VectorDB('chroma', 'any')
        self.retriever = None

        if uploaded_file:
            self.vector_db.index(uploaded_file)
            self.retriever = self.vector_db.as_retriever()

    def run(self, user_input):
        if not self.retriever:
            return "RAG System ready nahi hai. Kripya PDF file upload karein."

        # 1. Retrieve most relevant context chunks
        docs = self.retriever.invoke(user_input)
        context = "\n\n".join([doc.page_content for doc in docs])

        # 2. Build conversational history
        history_text = ""
        for msg in self.chat_memory.messages[-5:]:
            role = "User" if msg.type == "human" else "Assistant"
            history_text += f"{role}: {msg.content}\n"

        # 3. High-accuracy intelligent prompt
        prompt = f"""You are an expert AI assistant.
Answer the user's question thoroughly, accurately, and helpfully.
Guidelines:
1. If the Context below contains relevant information from the uploaded document, prioritize and cite it.
2. If the Context contains only watermarks (such as 'Scanned with CamScanner') or is insufficient, provide a comprehensive, accurate answer from your general knowledge and briefly note that the PDF appears to be a scanned image.
3. Be clear, professional, and well-structured.

--- CONTEXT START ---
{context}
--- CONTEXT END ---

Conversation History:
{history_text}

User Question: {user_input}
Answer:"""

        # 4. Direct LLM Call with local fallback
        try:
            response = self.llm.invoke(prompt)
            answer = response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            from src.ollama_chain import Ollama
            from src.utils import load_config
            cfg = load_config()
            local_llm = Ollama(**cfg['chat_model'])
            response = local_llm.invoke(prompt)
            answer = response.content if hasattr(response, 'content') else str(response)

        # 5. Update Memory
        self.chat_memory.add_user_message(user_input)
        self.chat_memory.add_ai_message(answer)

        return answer
