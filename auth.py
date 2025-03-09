from flask import Blueprint, render_template, url_for, request, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    access = request.form.get('access')
    secret = request.form.get('secret')

    print(f"Signup Attempt: email={email}, name={name}, password={password}")

    if not email or not name or not password:
        print("Missing required fields!")
        flash("All fields are required!", "error")
        return redirect(url_for("auth.signup"))

    user = User.query.filter_by(email=email).first()
    if user:
        print("User already exists!")
        flash("User already exists!", "error")
        return redirect(url_for("auth.signup"))

    try:
        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            access=access,
            secret=secret
        )
        db.session.add(new_user)
        db.session.commit()
        print("User saved successfully!")
    except Exception as e:
        print(f"Error saving user: {e}")
        db.session.rollback()
        flash("Signup failed. Try again.", "error")
        return redirect(url_for("auth.signup"))

    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])  # ✅ Now handles both GET and POST
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(f"Login Attempt: Email={email}, Password={password}")

        user = User.query.filter_by(email=email).first()
        print(f"User Found: {user}")

        if not user:
            print("User not found!")
            flash("User not found!", "error")
            return redirect(url_for('auth.login'))

        if not check_password_hash(user.password, password):
            print("Incorrect password!")
            flash("Incorrect password!", "error")
            return redirect(url_for('auth.login'))

        print("Login Successful!")
        login_user(user)
        return redirect(url_for('main.profile'))

    return render_template('login.html')

@auth.route('/logout')
@login_required  # ✅ Moved outside function
def logout():
    logout_user()
    return redirect(url_for('main.index'))
