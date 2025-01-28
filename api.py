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

client = Groq(api_key=api_key)

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
        return response.json().get("text", "") if response.status_code == 200 else ""

def get_groq_response(user_message):
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": user_message}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content