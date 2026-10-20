import os

from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
try:
    from langchain_core.documents import Document
except Exception:
    try:
        from langchain.schema.document import Document
    except Exception:
        # minimal fallback
        from dataclasses import dataclass
        @dataclass
        class Document:
            page_content: str
            id: str | None = None
            metadata: dict = None


def create_cache_dir(directory=None):
    if not directory:
        directory = './.cache'

    os.makedirs('./.cache', exist_ok=True)
    return directory


def load_pdf(file_path):
    loader = PyPDFLoader(file_path)

    return loader.load()


def load_pdf_directory(directory):
    loader = PyPDFDirectoryLoader(directory)
    documents = loader.load()

    return documents


def split_pdf(pdfs: list[Document]):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False
    )

    return splitter.split_documents(pdfs)


def extract_pdf(uploaded_pdf):
    cache_dir = create_cache_dir()
    cache_dir = os.path.join(cache_dir, 'temp_files')
    os.makedirs(cache_dir, exist_ok=True)

    for file in uploaded_pdf:
        file_path = os.path.join(cache_dir, file.name)

        with open(file_path, 'wb') as w:
            w.write(file.getvalue())

    return cache_dir
