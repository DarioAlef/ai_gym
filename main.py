from flask import Flask, url_for
from routes import bp  # importando o blueprint das rotas

app = Flask(__name__, static_folder='static')
app.register_blueprint(bp)  # registrando o blueprint

if __name__ == '__main__':
    app.run(debug=True)
