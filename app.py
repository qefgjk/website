from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import random
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # База данных
app.config['SECRET_KEY'] = 'supersecretkey'  # Ключ для безопасности сессий
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# 📌 Модель пользователя
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 📌 Главная страница
@app.route("/")
def home():
    return render_template("index.html")

# 📌 Регистрация
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Вы успешно зарегистрировались! Теперь войдите.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# 📌 Вход в систему
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("profile"))
        else:
            flash("Неверный логин или пароль", "danger")

    return render_template("login.html")

# 📌 Профиль (только для авторизованных)
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", username=current_user.username)

# 📌 Выход
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

# Основная страница
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route('/random_page')
def random_page():
    return render_template('random.html')




if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Создаёт таблицы в базе данных

    port = int(os.environ.get("PORT", 5000))  # Railway использует переменную PORT
    app.run(host="0.0.0.0", port=port)