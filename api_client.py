import os
from dotenv import load_dotenv
import openai
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Limpa qualquer variável OPENAI_API_KEY existente
if "OPENAI_API_KEY" in os.environ:
    del os.environ["OPENAI_API_KEY"]

# Carrega o .env
load_dotenv(override=True)

# Obtém a chave da API das variáveis de ambiente
api_key = os.getenv("OPENAI_API_KEY")

# Configura a chave da API
openai.api_key = api_key

# Verifica a chave que está sendo usada
print(f"API Key carregada: {api_key[:8]}...") # Mostra apenas os primeiros 8 caracteres
if not api_key:
    raise ValueError("API Key não encontrada nas variáveis de ambiente")



mensagens = [
    SystemMessage("Traduza o texto para o português do Brasil"),
    HumanMessage("Hello, how are you?")
]

modelo = ChatOpenAI(model="gpt-3.5-turbo")
parser = StrOutputParser()
chain = modelo | parser

template_mensagens = ChatPromptTemplate.from_messages[
    
]


resposta = chain.invoke(mensagens)

print(resposta)