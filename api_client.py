from dotenv import load_dotenv
import os
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

mensagens = [
    SystemMessage("Traduza o texto para o português do Brasil"),
    HumanMessage("Hello, how are you?")
]

modelo = ChatOpenAI(model="gpt-3.5-turbo")

resposta = modelo.invoke(mensagens)

print(resposta)