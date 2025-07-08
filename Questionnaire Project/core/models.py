import os
import logging
import traceback
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

load_dotenv(dotenv_path=".env", override=True)

logger = logging.getLogger(__name__)

AZUREOPENAI_API_KEY = os.getenv("AZUREOPENAI_API_KEY")
AZUREOPENAI_ENDPOINT = os.getenv("AZUREOPENAI_ENDPOINT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.0))


class Model:
    def llm(self):
        try:
            return AzureChatOpenAI(
                azure_endpoint=AZUREOPENAI_ENDPOINT,
                api_key=AZUREOPENAI_API_KEY,
                model=AZURE_DEPLOYMENT,
                api_version=API_VERSION,
                temperature=TEMPERATURE,
                streaming=True

                
            )
        except Exception as e:
            raise Exception(f"LLM Init Error: {e}\n{traceback.format_exc()}")

    def embedding(self):
        try:
            return AzureOpenAIEmbeddings(
                azure_endpoint=AZUREOPENAI_ENDPOINT,
                api_key=AZUREOPENAI_API_KEY,
                azure_deployment=AZURE_EMBEDDING_DEPLOYMENT,
                api_version=API_VERSION
            )
        except Exception as e:
            raise Exception(f"Embedding Init Error: {e}\n{traceback.format_exc()}")


mode_instance = Model()
llm_instance = mode_instance.llm()
embeddings_instance = mode_instance.embedding()
