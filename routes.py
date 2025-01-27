from flask import Blueprint, render_template, request, jsonify
from api import get_groq_response

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
        ai_response = get_groq_response(user_message)
        
        return jsonify({
            'status': 'success',
            'response': ai_response
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
