
import sys
import os
import traceback
sys.path.append(os.getcwd())

from langchain_ollama import ChatOllama as Ollama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from src.vectorstore import VectorDB
from src.utils import load_config
from src.ollama_chain import format_document_list

print("=" * 50)
print("DEBUG STARTUP SCRIPT")
print("=" * 50)

def test_chain_creation():
    try:
        print("\n1. Loading Config...")
        config = load_config()
        print(f"   Config loaded: {config.keys()}")

        print("\n2. Initializing LLM...")
        llm = Ollama(**config['chat_model'])
        print(f"   LLM created: {type(llm)}")

        print("\n3. Initializing VectorDB...")
        db_type = 'chroma'
        if 'vector_database' in config and 'pinecone' in config['vector_database']:
            db_type = 'pinecone'
        vector_db = VectorDB(db_type, 'any')
        print(f"   VectorDB created: {type(vector_db)}")

        print("\n4. Getting Retriever...")
        base_retriever = vector_db.as_retriever()
        print(f"   Base Retriever: {type(base_retriever)}")
        
        if base_retriever is None:
            print("❌ FAIL: base_retriever is None")
            return

        print("\n5. Creating History Aware Retriever...")
        contextual_q_system_prompt = "Test prompt"
        contextual_q_prompt = ChatPromptTemplate.from_messages([
            ('system', contextual_q_system_prompt),
            MessagesPlaceholder('chat_history'),
            ('human', '{input}'),
        ])
        
        history_aware_retriever = create_history_aware_retriever(
            llm, base_retriever, contextual_q_prompt
        )
        print(f"   History Aware Retriever: {type(history_aware_retriever)}")
        
        if history_aware_retriever is None:
            print("❌ FAIL: history_aware_retriever is None")
            return

        print("\n6. Creating Answer Chain components...")
        
        qa_system_prompt = "Test QA prompt"
        qa_prompt = ChatPromptTemplate.from_messages([
            ('system', qa_system_prompt),
            MessagesPlaceholder('chat_history'),
            ('human', '{input}'),
        ])
        print(f"   QA Prompt: {type(qa_prompt)}")
        
        def format_docs_for_prompt(input_dict):
            return "formatted docs"
        
        format_step = RunnableLambda(format_docs_for_prompt)
        print(f"   Format Step: {type(format_step)}")
        
        output_parser = StrOutputParser()
        print(f"   Output Parser: {type(output_parser)}")

        print("\n7. Building Answer Chain...")
        answer_chain = (
            format_step
            | qa_prompt
            | llm
            | output_parser
        )
        print(f"   Answer Chain: {type(answer_chain)}")
        
        if answer_chain is None:
            print("❌ FAIL: answer_chain is None")
            return

        print("\n8. Building Final RAG Chain (The step that fails)...")
        print("   Attempting RunnablePassthrough.assign...")
        
        # Verify history_aware_retriever again
        if history_aware_retriever is None:
             print("❌ FAIL: history_aware_retriever became None!")
             return

        rag_chain = (
            RunnablePassthrough.assign(context=history_aware_retriever)
            | answer_chain
        )
        print(f"   RAG Chain created successfully: {type(rag_chain)}")
        print("\n✅ SUCCESS: Chain built without errors!")

    except Exception:
        print("\n❌ EXCEPTION DURING CHAIN CREATION:")
        traceback.print_exc()

if __name__ == "__main__":
    test_chain_creation()
