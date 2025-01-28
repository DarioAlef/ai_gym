from flask import Blueprint, render_template, request, jsonify, redirect, url_for
# from api import get_groq_response
from models import User, db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route("/chat")
def chat():
    return render_template('chat.html')

@bp.route("/send_message", methods=['POST'])
def send_message():
    user_message = request.form.get('message')
    
    try:
        # Usa a função importada do main.py
        # ai_response = get_groq_response(user_message)
        
        return jsonify({
            'status': 'success',
            'response': user_message
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verifica se usuário já existe
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Usuário já existe'}), 400
            
        # Cria novo usuário
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('bp.login'))
    return render_template('signup.html')
