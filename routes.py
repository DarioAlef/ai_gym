from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from api import get_groq_response
from models import User, db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login')
def login():
    return render_template('login.html')

@bp.route("/chat", methods=['GET', 'POST'])
def chat():
    return render_template('chat.html')

@bp.route('/planos')
def planos():
    return render_template('planos.html')


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


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        birth_date = request.form.get('birth_date')
        cpf = request.form.get('cpf')
        gender = request.form.get('gender')
        address = request.form.get('address')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Verifica se algum campo está vazio
        if not all([full_name, birth_date, cpf, gender, address, password, confirm_password]):
            return render_template('signup.html', error="Todos os campos são obrigatórios.")

        # Verifica se as senhas coincidem
        if password != confirm_password:
            return render_template('signup.html', error="As senhas não coincidem")

        # Cria um novo usuário
        new_user = User(
            full_name=full_name,
            birth_date=birth_date,
            cpf=cpf,
            gender=gender,
            address=address,
            password=password
        )

        try:
            # Adiciona o usuário ao banco de dados
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Reverte a transação em caso de erro
            return render_template('signup.html', error=f"Erro ao cadastrar o usuário: {str(e)}")

        # Redireciona para a página de pagamento
        return redirect(url_for('main.pagamento'))

    return render_template('signup.html')


@bp.route('/pagamento', methods=['GET', 'POST'])
def pagamento():
    if request.method == 'POST':
        # Here you can implement the payment logic
        # For example, validate payment data and process it.
        # After successful payment, redirect to the chat page.
        return redirect(url_for('main.chat'))  # Redirecting to the existing chat route

    return render_template('pagamento.html')



