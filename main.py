from flask import Flask, request, jsonify
from routes import bp
import cv2
import numpy as np
import base64
from PIL import Image
import io
from os import makedirs, path
from models import db, User
from api import app  # Importando a instância do Flask

app.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///app.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY='sua-chave-secreta-aqui'
)

db.init_app(app)

# Criar pasta faces se não existir
makedirs('faces', exist_ok=True)

app.register_blueprint(bp)

def process_image_data(image_data):
    """Processa dados da imagem base64 para formato OpenCV"""
    image_bytes = base64.b64decode(image_data.split(',')[1])
    image = Image.open(io.BytesIO(image_bytes))
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def detect_faces(image):
    """Detecta faces na imagem usando cascade classifier"""
    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return face_classifier.detectMultiScale(gray, 1.3, 5), gray

@app.route('/face_login', methods=['POST'])
def face_login():
    try:
        opencv_image = process_image_data(request.json['image'])
        faces, gray = detect_faces(opencv_image)
        
        if not faces:
            return jsonify({'success': False, 'message': 'Nenhuma face detectada'})
        
        users = User.query.filter(User.face_data.isnot(None)).all()
        if not users:
            return jsonify({'success': False, 'message': 'Nenhum usuário cadastrado'})
        
        training_data, labels = [], []
        for user in users:
            if path.exists(user.face_data):
                face_img = cv2.imread(user.face_data, cv2.IMREAD_GRAYSCALE)
                training_data.append(face_img)
                labels.append(user.id)
        
        if not training_data:
            return jsonify({'success': False, 'message': 'Nenhuma face cadastrada'})
        
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(training_data, np.array(labels))
        
        for (x, y, w, h) in faces:
            face = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            label, confidence = recognizer.predict(face)
            if confidence < 70:
                user = User.query.get(label)
                if user:
                    return jsonify({'success': True, 'user_id': user.id, 'username': user.username})
        
        return jsonify({'success': False, 'message': 'Face não reconhecida'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/register_face', methods=['POST'])
def register_face():
    try:
        opencv_image = process_image_data(request.json['image'])
        user = User.query.filter_by(username=request.json['user_id']).first()
        
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'})
        
        faces, gray = detect_faces(opencv_image)
        
        if not faces:
            return jsonify({'success': False, 'message': 'Nenhuma face detectada'})
        
        x, y, w, h = faces[0]
        face = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
        
        face_path = f'faces/user_{user.id}.jpg'
        cv2.imwrite(face_path, face)
        user.face_data = face_path
        db.session.commit()
        
        return jsonify({'success': True})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)  # Inicia a aplicação Flask 