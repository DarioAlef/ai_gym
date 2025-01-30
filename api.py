from dotenv import load_dotenv
import requests
import tempfile
import os
from groq import Groq
from flask import Flask, request, jsonify

# Criação da instância do Flask
app = Flask(__name__)

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def get_groq_response(messages):
    # Certifique-se de que o formato das mensagens está correto
    formatted_messages = []
    for message in messages:
        formatted_messages.append({
            "role": message['role'],  # Deve ser 'user' ou 'assistant'
            "content": message['content']
        })

    chat_completion = client.chat.completions.create(
        messages=formatted_messages,  # Use o formato correto
        model="llama-3.3-70b-versatile",
    )
    
    return chat_completion.choices[0].message.content

######################################################################

# Configurações da API
groq_api_key = "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"
groq_api_endpoint = "https://api.groq.com/openai/v1/audio/transcriptions"
headers = {"Authorization": f"Bearer {groq_api_key}"}

# Função para transcrever áudio
def transcribe_audio(file_path, model="whisper-large-v3-turbo", language="pt"):
    file_extension = os.path.splitext(file_path)[1].lower()
    mime_type = 'audio/mp3' if file_extension == '.mp3' else 'audio/wav' if file_extension == '.wav' else None

    if not mime_type:
        print(f"Formato de arquivo não suportado: {file_extension}")
        return ""

    with open(file_path, "rb") as audio_file:
        files = {"file": (file_path, audio_file, mime_type)}
        data = {
            "model": model,
            "language": language,
            "response_format": "json",
        }
        response = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers={"Authorization": f"Bearer {api_key}"}, files=files, data=data)
        
        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            print(f"Erro na API: {response.status_code} - {response.text}")
            return ""

@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio_route():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'Nenhum arquivo enviado.'}), 400

    audio_file = request.files['file']
    file_path = os.path.join(tempfile.gettempdir(), audio_file.filename)
    audio_file.save(file_path)

    transcription = transcribe_audio(file_path)
    if transcription:
        return jsonify({'status': 'success', 'transcription': transcription})
    else:
        return jsonify({'status': 'error', 'message': 'Falha na transcrição.'}), 500