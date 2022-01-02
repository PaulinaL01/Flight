from flask import Flask, render_template, request, url_for, redirect, flash, session, send_from_directory,render_template_string
from flask_login import login_required, login_user, logout_user, current_user
from . import app, db, User,mail
from werkzeug.security import generate_password_hash
from .forms import LoginForm, SignUpForm, SearchFlightForm, CreateFlight
from .utils import create_code
from flask_mail import Message
from .decorator import superuser
from .models import db, User, Flight
from datetime import datetime

from flask_dance.contrib.github import github


@app.route("/",methods=['GET', 'POST'])
@login_required
def home():
    form = SearchFlightForm()
    flights = Flight.query.all()
    form.departure_city.choices = [(flight.departure_city, flight.departure_city) for flight in flights]
    form.arrival_city.choices = [(flight.arrival_city, flight.arrival_city) for flight in flights]

    if form.validate_on_submit():
        print(form.departure_city.data, form.arrival_city.data, form.date_from.data, form.date_to.data)
        return redirect(f"/search/{form.departure_city.data}/{form.arrival_city.data}/{form.date_from.data}/{form.date_to.data}")

    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            print(fieldName, err)

    return render_template("home.html", form=form)



    # if request.method == "POST":
    #     departure_city = request.form.get("departure_city")
    #     flash("Wybralas: " + departure_city, category="success")
    #     print(request.form.get("dateFrom"))
    #     dateFrom = datetime.strptime(request.form.get("dateFrom"), "%Y-%m-%dT%H:%M")
    #     print(dateFrom)
    # flights = Flight.query.all()
    # departure_citys = [flight.departure_city for flight in flights]
    #
    # if request.method == "POST":
    #     arrival_city = request.form.get("arrival_city")
    #     flash("Wybralas: " + arrival_city, category="success")
    # flights = Flight.query.all()
    # arrival_citys = [flight.arrival_city for flight in flights]
    # if request.method == "POST":
    #     arrival_data = request.form.get("arrival_data")
    #     flash("Wybrałaś:" + arrival_data,category="success")
    # flights = Flight.query.all()
    # arrival_datas = [flight.arrival_data for flight in flights]
    # return render_template("home.html", uzytkownik=current_user.login, current_user=current_user, departure_citys=departure_citys, arrival_citys=arrival_citys, arrival_datas=arrival_datas)

@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        if User.query.filter_by(login=form.login.data).first():
            flash("Podany uzytkownik juz istnieje", category="warning")
        elif User.query.filter_by(email=form.email.data).first():
            flash("Użytkownik o podanym adresie email już istnieje!", category="warning")
        else:
            flash("Utworzono uzytkownika", category="success")
            user = User(login=form.login.data, email=form.email.data,
                        password=generate_password_hash(form.password1.data),
                        confirm_code=create_code(64))
            db.session.add(user)
            db.session.commit()
            msg = Message("Email confirmation", sender=("Flask Project", "flaskproject2@gmail.com"),
                          recipients=[user.email])
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
    session.clear()
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

@app.route("/github_login")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    else:
        resp = github.get("/user")
        print(resp)
        print(resp.json())
        name = resp.json()["login"]
        email = resp.json()["email"]
        user = User.query.filter_by(login=name).first()
        if not user:
            user = User(login=name, email=email,
                        password=generate_password_hash("1234567"),
                        is_github_account=True,
                        confirmed_email=True)
            db.session.add(user)
            db.session.commit()
            user = User.query.filter_by(login=name).first()
        login_user(user)

        if not user.is_github_account:
            flash("Konto po podanej nazwie juz istnieje i nie jest powiazane z github-em", category="warning")
            return redirect(url_for("login"))

        return redirect(url_for("home"))



@app.route("/create_flight")
@superuser
def create():
    pass
@app.route("/booking")
def booking():
    pass

@app.route("/flights_list")
def flights_list():
    return render_template("flight_list.html")

@app.route("/create_flight_admin")
def create_flight_admin():
    # language = SelectField(u'Programming Language', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])
    form = CreateFlight


    if form.validate_on_submit():
        print(form.departure_city.data, form.arrival_city.data, form.date_from.data, form.date_to.data)
        dateFrom = datetime.strptime(form.date_from.data, "%Y-%m-%dT%H:%M")
        dateTo = datetime.strptime(form.date_to.data, "%Y-%m-%dT%H:%M")
        flights = Flight.query.filter(Flight.arrival_city == form.arrival_city.data
                                      and Flight.departure_city == form.departure_city.data
                                      and Flight.departure_data >= dateFrom
                                      and Flight.arrival_data <= dateTo)
        flights = list(flights)
        # tutaj trzeba wykonac redirect do innego endpointu z wynikami wyszukiwania

    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            print(fieldName, err)
    return render_template("create_flight_admin.html", form=form)


@app.route("/admin_search", methods=["GET", "POST"])
def admin_search():
    #language = SelectField(u'Programming Language', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])
    form = SearchFlightForm()
    flights = Flight.query.all()
    form.departure_city.choices = [(flight.departure_city, flight.departure_city) for flight in flights]
    form.arrival_city.choices = [(flight.arrival_city, flight.arrival_city) for flight in flights]

    if form.validate_on_submit():
        print(form.departure_city.data, form.arrival_city.data, form.date_from.data, form.date_to.data)
        dateFrom = datetime.strptime(form.date_from.data, "%Y-%m-%dT%H:%M")
        dateTo = datetime.strptime(form.date_to.data, "%Y-%m-%dT%H:%M")
        flights = Flight.query.filter(Flight.arrival_city==form.arrival_city.data
                                      and Flight.departure_city==form.departure_city.data
                                      and Flight.departure_data >= dateFrom
                                      and Flight.arrival_data <= dateTo)
        flights = list(flights)
        #tutaj trzeba wykonac redirect do innego endpointu z wynikami wyszukiwania

    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            print(fieldName, err)

    return render_template("admin_search.html", form=form)

@app.route("/admin_flights_list")
#@login_required
def admin_flights_list():
    flights = Flight.query.all()
    return render_template("admin_flights_list.html", flights=flights)


@app.route("/search", methods=["GET", "POST"])
@app.route("/search/<departure>/<arrival>/<date_from>/<date_to>")
#@login_required
def search(departure="", arrival="", date_from=None, date_to=None):
    form = SearchFlightForm()
    flights = Flight.query.all()
    form.departure_city.choices = [(flight.departure_city, flight.departure_city) for flight in flights]
    form.arrival_city.choices = [(flight.arrival_city, flight.arrival_city) for flight in flights]

    flights = []

    if form.validate_on_submit():
        print(form.departure_city.data, form.arrival_city.data, form.date_from.data, form.date_to.data)
        return redirect(f"/search/{form.departure_city.data}/{form.arrival_city.data}/{form.date_from.data}/{form.date_to.data}")
    else:
        if date_from and date_to:
            dateFrom = datetime.strptime(date_from, "%Y-%m-%dT%H:%M")
            dateTo = datetime.strptime(date_to, "%Y-%m-%dT%H:%M")
            flights = Flight.query.filter(Flight.arrival_city == arrival
                                          and Flight.departure_city == departure
                                          and Flight.departure_data >= dateFrom
                                          and Flight.arrival_data <= dateTo)
    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            print(fieldName, err)

    form.departure_city.data = departure
    form.arrival_city.data = arrival
    form.date_from.data = date_from
    form.date_to.data = date_to
    return render_template("search.html", flights=flights, form=form)