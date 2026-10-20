from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_classic.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser

from src.utils import load_config


class LlamaChain:
    def __init__(self, chat_memory) -> None:
        prompt = PromptTemplate(
            template="""<|begin_of_text|>
            <|start_header_id|>system<|end_header_id|>
            You are a helpful and knowledgeable AI assistant.
            <|eot_id|>
            <|start_header_id|>user<|end_header_id|>
            Previous conversation={chat_history}
            Question: {input} 
            Answer: <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
            input_variables=['chat_history', 'input']
        )

        self.memory = ConversationBufferWindowMemory(
            memory_key='chat_history',
            chat_memory=chat_memory,
            k=3,
            return_messages=True
        )

        config = load_config()
        llm = LlamaCpp(**config['chat_model'])

        self.llm_chain = LLMChain(prompt=prompt, llm=llm, memory=self.memory, output_parser=StrOutputParser())

    def run(self, user_input):
        response = self.llm_chain.invoke(user_input)
        return response['text']

    def update_chain(self, uploaded_pdf):
        pass