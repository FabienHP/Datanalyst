import os
from functools import lru_cache
import httpx
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_openai import OpenAIEmbeddings

os.environ["PROXY_URL"] = os.getenv('PROXY_URL')
os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
os.environ["AZURE_OPENAI_API_BASE"] = os.getenv('AZURE_OPENAI_API_BASE')
os.environ["AZURE_OPENAI_API_VERSION"] = os.getenv('AZURE_OPENAI_API_VERSION')
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv('AZURE_OPENAI_API_KEY')
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
@lru_cache(maxsize=4)
def get_openai_llm(gpt_4: bool = False, azure: bool = False):
    proxy_url = os.environ["PROXY_URL"]
    if proxy_url is not None or proxy_url != "":
        http_client = httpx.AsyncClient(proxies=proxy_url)
    else:
        http_client = None
    if not azure:
        if gpt_4:
            llm = ChatOpenAI(model="gpt-4o", temperature=0)
        else:
            llm = ChatOpenAI(http_client=http_client, model="gpt-3.5-turbo-0125", temperature=0, streaming=True)
    else:
        llm = AzureChatOpenAI(
            http_client=http_client,
            temperature=0,
            deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            openai_api_base=os.environ["AZURE_OPENAI_API_BASE"],
            openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
            streaming=True,
        )
    return llm

def get_embedding_openai():
    embedding = OpenAIEmbeddings(model="text-embedding-3-large")
    return embedding