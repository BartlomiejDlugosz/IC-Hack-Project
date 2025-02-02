import os
import string
import random
import rag.src.llama_index_template as llama

class ds_knowledge_base():
    def __init__(self):
        """Accesses the index for ground-truth database (wikipedia download)"""
        self.index =llama.LlamaIndexManager(main_folder="rag/wikipedia_cs/")
        
    def query(self, prompt):
        """Makes a query while searching the index first;
        If no information starts the response with ***"""
        prompt_text = f"""Instruction: If no information, start the response with *** but still try to respond. . Start the second sentence in new row.
        Prompt: {prompt}"""
        result = self.index.query_index(prompt_text)
        return result
    

class user_knowledge_base():
    def __init__(self, user_id = "000001"):
        """Initialize text based memory of events for a specific user. User ID is alphanumeric"""
        self.users_path = os.path.join("rag/user_databases", user_id)
        self.data_path = os.path.join(self.users_path, "data")
        #Creates the directory if it is not there, otherwise just initializes it.
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)
            with open(os.path.join(self.data_path, "init.txt"), 'w') as file:
                file.write("This database stores information about the user, who is here to learn computer science. The goal is to provide their past interactions for higher prompt relevance")

        self.index = llama.LlamaIndexManager(main_folder=self.users_path)
    
    def query(self, prompt):
        prompt_text = f"""Instruction: If no information, start the response with *** but still try to respond. Start the second sentence in new row.
        Prompt: {prompt}"""
        result = self.index.query_index(prompt_text)
        return result
    
    def update_memory(self, interaction_text):
        """Adds an interaction to user database"""

        def generate_random_path():
            """Updates the user's memory with new text."""
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=13))
            file_path = os.path.join(self.data_path, f"{random_string}.txt")
            return file_path
        
        file_path = generate_random_path()
        with open(file_path, 'w') as file:
            file.write(interaction_text)

        self.index.add_to_index(self.data_path)


if __name__ == "__main__":
    ds_kb = ds_knowledge_base()
    print(ds_kb.query("What is data science?"))

    print(print(ds_kb.query("What are exploding kittens?")))

    user_kb = user_knowledge_base(user_id="000001")
    print(user_kb.query("What does the learner like?"))

    user_kb.update_memory("The user enjoys fishing.")
    print(user_kb.query("What did the learner find difficult?"))