import os,tempfile,sys
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_mistralai.chat_models import ChatMistralAI
from deep_translator import GoogleTranslator
from cryptography.fernet import Fernet
import warnings
from temptrack import register_temp_dir
from pathlib import Path
warnings.filterwarnings("ignore", category=DeprecationWarning)


def resource_path(relative_path):

        return os.path.abspath(relative_path)

class Model:
    
    def __init__(self):
        os.environ['MISTRAL_API_KEY'] = "VFm7zcXPtANeaSNvMeE6JANXx7Tm0bqC"
        FERNET_KEY = b'oa5gUlGQ1SLRFHrpiYXkjajwYJddETxli4qXjrCjGnQ='  # 32-byte base64-encoded key

        fernet = Fernet(FERNET_KEY)
        with open(resource_path("auth/chroma_encrypted.bin"), "rb") as f:
            decrypted_data = fernet.decrypt(f.read())

        # Save zip to temp and extract
        self.temp_dir = tempfile.mkdtemp()
        
        self.zip_path = os.path.join(self.temp_dir, "chroma.zip")
        with open(self.zip_path, "wb") as f:
            f.write(decrypted_data)

        import zipfile
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        self.database_path = os.path.join(self.temp_dir, 'database_2')
        register_temp_dir(self.database_path)
        register_temp_dir(self.zip_path)
        register_temp_dir(self.temp_dir)
        register_temp_dir(self.database_path)
        self.preprocesspdf()
        self.translator = GoogleTranslator()

    def preprocesspdf(self):
        embeddings = HuggingFaceEmbeddings(model_name=resource_path('huggingface/hub/models--sentence-transformers--all-mpnet-base-v2/snapshots/12e86a3c702fc3c50205a8db88f0ec7c0b6b94a0'))
        print('embedding done')
        vectordb = Chroma(persist_directory=os.path.join(self.temp_dir, 'database_2'), embedding_function=embeddings)
        print("db loaded")
        llm = ChatMistralAI(model="mistral-small-2506", temperature=0.3, max_tokens=1000)
        prompt = ChatPromptTemplate.from_template("""
        Answer the user's question as a veterinary doctor specialized in cattle to the cattle farm owners by using the context and give response without markdown:
        Context: {context}
        Question: {input}""")
        chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
        retriever = vectordb.as_retriever()
        self.retreival_chain = create_retrieval_chain(retriever, chain)
        print("chain initialized")
        return 'PDF process successful'

    def run_retrieval(self, query, lang):
        print("document retrieving")
        try:
            translated_query = GoogleTranslator(source='auto', target='en').translate(query)
            print("query translated")
            response = self.retreival_chain.invoke({"input": translated_query})
            print(response)
            print("response generated")
        except Exception as e:
            print(e)
            return "No Disease"
        
        text = dict(response)
        # print(text)
        response = text['answer']
        if not response:
            return "Sorry, no response."
        if lang != "en":
            response = GoogleTranslator(source='auto', target=lang).translate(response)
            return response
        
        return response
    
# a = Model()
# print(a.run_retrieval("what is lumpy skin disease?","en"))

    
