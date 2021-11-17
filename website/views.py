from flask import Flask, render_template, request, url_for, redirect, flash, session, send_from_directory,render_template_string
from flask_login import login_required, login_user, logout_user, current_user
from . import app, db, User,mail
from werkzeug.security import generate_password_hash
from .forms import LoginForm, SignUpForm
from .utils import create_code
from flask_mail import Message
from .decorator import superuser

from flask_dance.contrib.github import github


@app.route("/")
@login_required
def home():
    flash('duuuupa', category='success')
    return render_template("home.html", uzytkownik=current_user.login, current_user=current_user)

@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(login=form.login.data,
                    email=form.email.data,
                    password=generate_password_hash(form.password1.data),
                    confirm_code=create_code(64))
        db.session.add(user)
        db.session.commit()
        msg = Message("Email confirmation", sender=("Flask Project", "flaskproject2@gmail.com"), recipients=[user.email])
        with open("website/templates/email_confirmation.html", "r", encoding="utf-8") as f:
            msg.html = render_template_string(f.read(), code=user.confirm_code)
            mail.send(msg)
        flash("Account created! Confirm email adress", category="success")
        return redirect(url_for("login"))
    else:
        for error in form.login.errors:
            flash(error, category="warning")
        for error in form.email.errors:
            flash(error, category="warning")
        for error in form.password1.errors:
            flash(error, category="warning")

    return render_template("sign_up.html", current_user=current_user, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit(): #jesli formularz udalo sie poprawnie wypelnic
        user = User.query.filter_by(login=form.login.data).first()
        if not user:
            flash("Nie ma takiego uzytkownika", category="danger")
        elif not user.confirmed_email:
            flash("Nie potwierdzono adresu email", category="danger")
        else:
            login_user(user, remember=True)
            flash("Zalogowano!", category="success")
            return redirect(url_for("home"))
    else:
        for error in form.login.errors:
            flash(error, category="warning")
        for error in form.password.errors:
            flash(error, category="warning")

    return render_template("login.html", current_user=current_user, form=form)


@login_required
@app.route("/logout")
def logout():
    logout_user()
    flash("Wylogowano!", category="success")
    return redirect(url_for("login"))

@app.route("/register/<code>")
def confirm_email(code):
    user = User.query.filter_by(confirm_code=code).first()
    if not user:
        return "Bad request", 400
    user.confirmed_email = True
    user.confirm_code = None
    db.session.commit()
    flash("Email confirmed", category="success")
    return redirect(url_for("login"))

@app.route("/acceptcookies")
def cookies():
    session["cookies"] = True #zapisuje w sesji przegladarki pare "cookies" i True
    return redirect(url_for("home"))