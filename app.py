from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from modules.facebook_scraper import run_scraper_and_analysis
import io
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_muy_segura'  # Cambia esto por una clave secreta real
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Base de datos de usuarios simulada para la autenticación
users = {
    "admin": {
        "password": bcrypt.generate_password_hash("password").decode('utf-8')
    }
}

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return
    user = User()
    user.id = username
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and bcrypt.check_password_hash(users[username]['password'], password):
            user = User()
            user.id = username
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # Ejecutar el scraper y análisis de sentimientos
        results = run_scraper_and_analysis()

        # Convertir el DataFrame a CSV y guardarlo en memoria
        csv_buffer = io.StringIO()
        results.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)  # Ir al principio del archivo en memoria

        # Preparar el archivo CSV para descarga
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='facebook_posts_sentiment_analysis.csv'  # Cambiado a download_name
        )

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)