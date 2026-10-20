from langchain_ollama import ChatOllama as Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.memory import ConversationBufferWindowMemory
from src.utils import load_config
from src.vectorstore import VectorDB

class OllamaChain:
    def __init__(self, chat_memory) -> None:
        config = load_config()
        prompt = PromptTemplate(
            template="""You are an accurate, helpful AI assistant.
Conversation History:
{chat_history}

User Question: {input}
Answer:""",
            input_variables=['chat_history', 'input']
        )
        self.memory = ConversationBufferWindowMemory(
            memory_key='chat_history', chat_memory=chat_memory, k=4, return_messages=True
        )
        llm = Ollama(**config['chat_model'])
        from langchain_classic.chains import LLMChain
        self.llm_chain = LLMChain(prompt=prompt, llm=llm, memory=self.memory, output_parser=StrOutputParser())

    def run(self, user_input):
        return self.llm_chain.invoke({"input": user_input})['text']

class OllamaRAGChain:
    def __init__(self, chat_memory, uploaded_file=None):
        config = load_config()
        self.chat_memory = chat_memory
        self.llm = Ollama(**config['chat_model'])
        self.vector_db = VectorDB('chroma', 'any')
        self.retriever = None

        if uploaded_file:
            self.vector_db.index(uploaded_file)
            self.retriever = self.vector_db.as_retriever()

    def run(self, user_input):
        if not self.retriever:
            return "RAG System ready nahi hai. Kripya PDF file upload karein."

        # 1. Retrieve relevant context
        docs = self.retriever.invoke(user_input)
        context = "\n\n".join([doc.page_content for doc in docs])

        # 2. Build history
        history_text = ""
        for msg in self.chat_memory.messages[-5:]:
            role = "User" if msg.type == "human" else "Assistant"
            history_text += f"{role}: {msg.content}\n"

        # 3. Grounded, intelligent prompt
        prompt = f"""You are an expert AI assistant.
Answer the user's question thoroughly, accurately, and helpfully.
Guidelines:
1. If the Context below contains relevant information from the uploaded document, prioritize and cite it.
2. If the Context contains only watermarks (such as 'Scanned with CamScanner') or is insufficient, provide a comprehensive, accurate answer from your general knowledge and briefly note that the PDF appears to be a scanned image.
3. Be clear, accurate, and concise.

--- CONTEXT START ---
{context}
--- CONTEXT END ---

Conversation History:
{history_text}

User Question: {user_input}
Answer:"""

        # 4. Direct LLM Call
        response = self.llm.invoke(prompt)
        answer = response.content if hasattr(response, 'content') else str(response)

        # 5. Update Memory
        self.chat_memory.add_user_message(user_input)
        self.chat_memory.add_ai_message(answer)

        return answer