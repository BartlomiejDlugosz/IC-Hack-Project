from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
import os
from llama_index.llms.openai.base import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType
from dotenv import load_dotenv

class LlamaIndexManager:
    def __init__(self, main_folder='rag_template_main/example'):
        load_dotenv()
        self.OPENAI_API_KEY = os.getenv("OPENAI_KEY")
        if self.OPENAI_API_KEY is None:
            raise ValueError("NO open AI key")
        
        self.main_folder = main_folder
        self.PERSIST_DIR = os.path.join(main_folder, "storage")
        self.DATA_DIR = os.path.join(main_folder, "data")
        self.index = self.initialize_index()

    def initialize_index(self, force_rebuild=False):
        if not os.path.exists(self.PERSIST_DIR) or force_rebuild:
            documents = SimpleDirectoryReader(self.DATA_DIR).load_data()
            embed_model = OpenAIEmbedding(model=OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL, api_key=self.OPENAI_API_KEY)
            self.index = VectorStoreIndex.from_documents(documents, show_progress=True, embed_model=embed_model)
            self.index.storage_context.persist(persist_dir=self.PERSIST_DIR)
        else:
            storage_context = StorageContext.from_defaults(persist_dir=self.PERSIST_DIR)
            self.index = load_index_from_storage(storage_context)
        return self.index

    def query_index(self, user_query):
        model = OpenAI(api_key=self.OPENAI_API_KEY, model="gpt-4o-mini")
        query_engine = self.index.as_query_engine(llm=model)
        return query_engine.query(user_query)

    def add_to_index(self, new_documents):
        if not os.path.exists(self.PERSIST_DIR):
            raise ValueError(f"Storage directory {self.PERSIST_DIR} does not exist")
        
        # Ensure new_documents is a list of document objects
        if isinstance(new_documents, str):
            new_documents = SimpleDirectoryReader(new_documents).load_data()
        
        embed_model = OpenAIEmbedding(model=OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL, api_key=self.OPENAI_API_KEY)
        new_index = VectorStoreIndex.from_documents(new_documents, show_progress=True, embed_model=embed_model)
        
        # Merge the new index with the existing one
        self.index = new_index
        
        # Persist the updated index
        self.index.storage_context.persist(persist_dir=self.PERSIST_DIR)


if __name__ == "__main__":
    print("Current working directory:", os.getcwd())
    manager = LlamaIndexManager(main_folder="rag/individual_history")
    file_path = "rag/individual_history/data/"

    # Add the file to the index
    manager.add_to_index(file_path)

    # Verify the file is added by querying the index
    response = manager.query_index("IS the user brave of anything. Add *** sto start of prompt if no information can be found")
    print(response)
