from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from modules.facebook_scraper import analyze_sentiment_from_csv
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Cambia esto a una clave segura
UPLOAD_FOLDER = 'uploads'  # Define la carpeta para subir archivos
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Base de datos de usuarios simulada para la autenticación
users = {
    "admin": {
        "password": bcrypt.generate_password_hash("password").decode('utf-8')
    }
}

global combined_df  # Define combined_df como global

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
def index():
    if request.method == 'POST':
        # Verificar si se subieron archivos
        if 'file' not in request.files:
            flash('No se ha subido ningún archivo.', 'danger')
            return redirect(request.url)

        files = request.files.getlist('file')  # Obtener la lista de archivos

        # Verificar que al menos un archivo fue seleccionado
        if not files:
            flash('No se ha seleccionado ningún archivo.', 'danger')
            return redirect(request.url)

        # Analizar cada archivo CSV
        results = []
        for file in files:
            if file.filename == '':
                flash('Uno o más archivos no tienen nombre.', 'danger')
                continue  # Ignorar archivos sin nombre

            if not file.filename.endswith('.csv'):
                flash(f'El archivo {file.filename} no es un CSV.', 'danger')
                continue  # Ignorar archivos que no son CSV

            # Guardar el archivo
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Analizar el archivo CSV
            try:
                result_df = analyze_sentiment_from_csv(file_path)
                results.append(result_df)  # Guardar el resultado
            except Exception as e:
                flash(f'Ocurrió un error al procesar {file.filename}: {str(e)}', 'danger')
            finally:
                os.remove(file_path)  # Limpiar el archivo después de procesar

        # Combinar todos los resultados en un solo DataFrame, si es necesario
        if results:
            global combined_df  # Define combined_df como global
            combined_df = pd.concat(results, ignore_index=True)
            flash('Análisis realizado con éxito.', 'success')
            return render_template('result.html', tables=[combined_df.to_html(classes='data')])
        else:
            flash('No se procesaron archivos válidos.', 'warning')

    return render_template('index.html')

@app.route('/download_results', methods=['GET'])
@login_required
def download_results():
    # Asumiendo que 'combined_df' es un DataFrame que almacenas globalmente o que puedes recuperar
    global combined_df  # Asegúrate de que combined_df es accesible
    if combined_df is None:
        flash('No hay resultados disponibles para descargar.', 'warning')
        return redirect(url_for('index'))
    
    # Guarda el DataFrame como un archivo CSV
    csv_file_path = 'resultados.csv'
    combined_df.to_csv(csv_file_path, index=False)

    return send_file(csv_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
