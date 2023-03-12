from flask import Flask, render_template, request, url_for, redirect, flash, session, send_from_directory,render_template_string
from flask_login import login_required, login_user, logout_user, current_user
from . import app, db, User,mail
from .forms import LoginForm, SignUpForm, SearchFlightForm, CreateFlight
from flask_mail import Message
from .models import db, User, Flight, Cart, Order
from datetime import datetime
from .data import DataContext

from flask_dance.contrib.github import github

data_context = DataContext(db)


@app.route("/", methods=['GET', 'POST'])
@login_required
def home():
    form = SearchFlightForm()
    form.departure_city.choices = data_context.get_all_departure_cities()
    form.arrival_city.choices = data_context.get_all_arrival_cities()

    if form.validate_on_submit():
        print(form.departure_city.data, form.arrival_city.data, form.date_from.data, form.date_to.data)
        return redirect(f"/search/{form.departure_city.data}/{form.arrival_city.data}/{form.date_from.data}/{form.date_to.data}")

    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            flash(err, category="warning")

    return render_template("home.html", form=form)


@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        user, message_text = data_context.create_user(form.login.data, form.email.data, form.password1.data)
        if user:
            msg = Message("Email confirmation", sender=("Flask Project", "flaskproject2@gmail.com"),
                          recipients=[user.email])
            with open("website/templates/email_confirmation.html", "r", encoding="utf-8") as f:
                msg.html = render_template_string(f.read(), code=user.confirm_code)
                mail.send(msg)
            flash(message_text, category="success")
            return redirect(url_for("login"))
        else:
            flash(message_text, category="warning")
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(err, category="warning")

    return render_template("sign_up.html", current_user=current_user, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = data_context.get_user_by_login(form.login.data)
        if not user:
            flash("Nie ma takiego uzytkownika", category="danger")
        elif not user.confirmed_email:
            flash("Nie potwierdzono adresu email", category="danger")
        else:
            login_user(user, remember=True)
            flash("Zalogowano!", category="success")
            return redirect(url_for("home"))
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(err, category="warning")

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
    user = data_context.get_user_by_confirmation_code(code)
    if not user:
        return "Bad request", 400
    user.confirmed_email = True
    user.confirm_code = None
    db.session.commit()
    flash("Email confirmed", category="success")
    return redirect(url_for("login"))


@app.route("/acceptcookies")
def cookies():
    session["cookies"] = True
    return redirect(url_for("home"))


@app.route("/github_login")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    else:
        resp = github.get("/user")
        login = resp.json()["login"]
        email = resp.json()["email"]
        user = data_context.get_user_by_login(login)
        if not user:
            user, message_text = data_context.create_user(login, email, "1234567", is_github_account=True, confirmed_email=True)
            #TODO: obsluzyc sytuacje gdy ktos na githubie ma taki sam mail jak inna osoba w bazie
        login_user(user)

        if not user.is_github_account:
            flash("Konto po podanej nazwie juz istnieje i nie jest powiazane z github-em", category="warning")
            return redirect(url_for("login"))

        return redirect(url_for("home"))


@app.route("/admin_flight_edit/<int:id>", methods=["GET", "POST"])
def admin_flight_edit(id):
    form= CreateFlight()
    flight = data_context.get_flight_by_id(id)
    if form.validate_on_submit() and flight:
        data_context.update_flight(flight_id=id,
                                   arrival_city=form.create_arrival_city.data,
                                   departure_city=form.create_departure_city.data,
                                   flight_number=form.create_flight_number.data)

    return render_template("admin_flight_edit.html", flight=flight, form=form, datetime=datetime, str=str)


@app.route("/delete_from_cart/<int:flight_id>", methods=["GET", "POST"])
def delete_from_cart(flight_id):
    _cart = Cart.query.filter_by(customer_id=current_user.id, bought=False).first()
    if not _cart:
        return 'Cart not found', 404

    order = Order.query.filter_by(cart_id=_cart.id, flight_id=flight_id).first()
    if not order:
        return "Order not found", 404
    if order.amount == 1:
        db.session.delete(order)
    else:
        order.amount -= 1
    db.session.commit()
    flash("Deleted from cart")

    return redirect(url_for("cart"))


@app.route("/add_to_cart/<int:flight_id>", methods=["GET", "POST"])
def add_to_cart(flight_id):

    _cart = Cart.query.filter_by(customer_id=current_user.id, bought=False).first()
    if not _cart:
        _cart = Cart(customer_id=current_user.id)
        db.session.add(_cart)
        db.session.commit()

    order = Order.query.filter_by(flight_id=flight_id, cart_id=_cart.id).first()
    if not order:
        order = Order(flight_id=flight_id, cart_id=_cart.id)
        db.session.add(order)
    else:
        order.amount += 1
    db.session.commit()

    flash("Added to cart", category="success")

    return redirect(url_for("flights_list"))


@app.route("/cart", methods=["GET", "POST"])
def cart():
    return render_template("cart.html",  flights=current_user.get_flights_from_open_cart())


@app.route("/flights_list")
def flights_list():
    flights = Flight.query.all()

    return render_template("flights_list.html", flights=flights)


@app.route("/create_flight_admin", methods=["GET", "POST"])
def create_flight_admin():

    form = CreateFlight()

    if form.validate_on_submit():
        print(form.create_departure_city.data, form.create_arrival_city.data, form.create_date_from.data, form.create_date_to.data)

        dateFrom = datetime.strptime(form.create_date_from.data, "%Y-%m-%dT%H:%M")
        dateTo = datetime.strptime(form.create_date_to.data, "%Y-%m-%dT%H:%M")

        flight = Flight(departure_city=form.create_departure_city.data, arrival_city=form.create_arrival_city.data,
                        departure_date=dateFrom, arrival_date=dateTo,
                        flight_number=form.create_flight_number.data,
                        passengers_number=form.create_passengers_number.data,
                        max_weight=form.create_max_weight.data,
                        crew_number=form.create_crew_number.data)

        db.session.add(flight)
        db.session.commit()
        flash("Dodano")

        #TODO: tutaj trzeba wykonac redirect do innego endpointu z wynikami wyszukiwania

    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            print(fieldName, err)

    return render_template("create_flight_admin.html", form=form)


@app.route("/admin_search", methods=["GET", "POST"])
def admin_search():
    form = SearchFlightForm()
    flights = Flight.query.all()
    form.departure_city.choices = [(flight.departure_city, flight.departure_city) for flight in flights]
    form.arrival_city.choices = [(flight.arrival_city, flight.arrival_city) for flight in flights]

    if form.validate_on_submit():
        print(form.departure_city.data, form.arrival_city.data, form.date_from.data, form.date_to.data)
        dateFrom = datetime.strptime(form.date_from.data, "%Y-%m-%dT%H:%M")
        dateTo = datetime.strptime(form.date_to.data, "%Y-%m-%dT%H:%M")
        flights = Flight.query.filter(Flight.arrival_city == form.arrival_city.data
                                      and Flight.departure_city == form.departure_city.data
                                      and Flight.departure_date >= dateFrom
                                      and Flight.arrival_date <= dateTo)
        flights = list(flights)
        #TODO: tutaj trzeba wykonac redirect do innego endpointu z wynikami wyszukiwania

    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            print(fieldName, err)

    return render_template("admin_search.html", form=form)

@app.route("/admin_flights_list")
def admin_flights_list():
    flights = Flight.query.all()
    return render_template("admin_flights_list.html", flights=flights)


@app.route("/search", methods=["GET", "POST"])
@app.route("/search/<departure>/<arrival>/<date_from>/<date_to>")
def search(departure="", arrival="", date_from=None, date_to=None):
    form = SearchFlightForm()
    form.departure_city.choices = data_context.get_all_departure_cities()
    form.arrival_city.choices = data_context.get_all_arrival_cities()

    flights = []

    if form.validate_on_submit():
        print(form.departure_city.data, form.arrival_city.data, form.date_from.data, form.date_to.data)
        return redirect(f"/search/{form.departure_city.data}/{form.arrival_city.data}/{form.date_from.data}/{form.date_to.data}")
    else:
        if date_from and date_to:
            dateFrom = datetime.strptime(date_from, "%Y-%m-%dT%H:%M")
            dateTo = datetime.strptime(date_to, "%Y-%m-%dT%H:%M")
            flights = Flight.query.filter_by(arrival_city=arrival, departure_city=departure)

            flights = [flight for flight in flights if flight.departure_date.date() == dateFrom.date()]

    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            print(fieldName, err)

    form.departure_city.data = departure
    form.arrival_city.data = arrival
    form.date_from.data = date_from
    form.date_to.data = date_to
    return render_template("search.html", flights=flights, form=form)
