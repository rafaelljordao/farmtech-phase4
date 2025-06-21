from flask import Flask
from routes.auth import auth_blueprint  # Importa o blueprint definido em routes/auth.py

app = Flask(__name__)

# Registra o blueprint com o prefixo /auth
app.register_blueprint(auth_blueprint, url_prefix='/auth')

@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(debug=True)
