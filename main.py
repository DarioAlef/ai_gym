from flask import Flask, url_for, request, jsonify
from routes import bp  # importando o blueprint das rotas
import cv2
import numpy as np
import base64
from PIL import Image
import io
from os import listdir, makedirs, path
from os.path import isfile, join, exists
from models import db, User

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'

db.init_app(app)

# Criar pasta faces se não existir
if not exists('faces'):
    makedirs('faces')

app.register_blueprint(bp)  # registrando o blueprint

@app.route('/face_login', methods=['POST'])
def face_login():
    try:
        image_data = request.json['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        image = Image.open(io.BytesIO(image_bytes))
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detecta face
        face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return jsonify({'success': False, 'message': 'Nenhuma face detectada'})
            
        # Prepara reconhecedor LBPH
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Carrega faces cadastradas
        training_data = []
        labels = []
        users = User.query.filter(User.face_data.isnot(None)).all()
        
        if not users:
            return jsonify({'success': False, 'message': 'Nenhum usuário cadastrado'})
            
        for user in users:
            if path.exists(user.face_data):
                face_img = cv2.imread(user.face_data, cv2.IMREAD_GRAYSCALE)
                training_data.append(face_img)
                labels.append(user.id)
        
        if not training_data:
            return jsonify({'success': False, 'message': 'Nenhuma face cadastrada'})
            
        # Treina o reconhecedor
        recognizer.train(training_data, np.array(labels))
        
        # Tenta reconhecer a face
        for (x,y,w,h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (200, 200))
            
            try:
                label, confidence = recognizer.predict(face)
                
                if confidence < 70:  # Menor confiança = maior certeza
                    user = User.query.get(label)
                    if user:
                        return jsonify({
                            'success': True,
                            'user_id': user.id,
                            'username': user.username
                        })
            except Exception as e:
                print(f"Erro na predição: {str(e)}")
                continue
                
        return jsonify({'success': False, 'message': 'Face não reconhecida'})
        
    except Exception as e:
        print(f"Erro no login facial: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/register_face', methods=['POST'])
def register_face():
    try:
        image_data = request.json['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        user_id = request.json['user_id']
        
        # Verifica se o usuário existe
        user = User.query.filter_by(username=user_id).first()
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'})
        
        image = Image.open(io.BytesIO(image_bytes))
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detecta face usando cascade classifier
        face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return jsonify({'success': False, 'message': 'Nenhuma face detectada'})
            
        for (x,y,w,h) in faces:
            cropped_face = gray[y:y+h, x:x+w]
            cropped_face = cv2.resize(cropped_face, (200, 200))
            
            # Salva a face
            face_path = f'faces/user_{user.id}.jpg'
            cv2.imwrite(face_path, cropped_face)
            user.face_data = face_path
            db.session.commit()
            
            return jsonify({'success': True})
            
    except Exception as e:
        print(f"Erro no registro facial: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 