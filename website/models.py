from . import db
from sqlalchemy import func
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    nationality = db.Column(db.String(100))
    passport_number = db.Column(db.Integer)
    date_of_birth = db.Column(db.DateTime(timezone=True))
    place_of_birth = db.Column(db.String(100))
    admin = db.Column(db.Boolean, default=False)
    is_github_account = db.Column(db.Boolean, default=False)
    confirmed_email = db.Column(db.Boolean, default=False)
    confirm_code = db.Column(db.String(65))
    cart_items = db.relationship("Cart")

    def get_flights_from_open_cart(self):
        flights = []

        for item in self.cart_items:
            if item.bought:
                continue
            orders = Order.query.filter_by(cart_id=item.id)
            for order in orders:
                fl = Flight.query.filter_by(id=order.flight_id).first()
                if fl:
                    item_dict = (fl,  order.amount)
                    flights.append(item_dict)
        return flights


class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.Integer)
    departure_city = db.Column(db.String(100))
    arrival_city = db.Column(db.String(100))
    departure_date = db.Column(db.DateTime(timezone=True))
    arrival_date = db.Column(db.DateTime(timezone=True))
    passengers_number = db.Column(db.Integer)
    max_weight = db.Column(db.Integer)
    crew_number = db.Column(db.Integer)
    airport_id = db.Column(db.Integer)
    plane_id = db.Column(db.Integer)
    flight_id = db.Column(db.Integer)
    pilot_id = db.Column(db.Integer)

class Airport(db.Model):
    id = db.Column(db.String, primary_key=True)
    IATACode = db.Column(db.Integer)
    max_plane_number = db.Column(db.Integer)
    country = db.Column(db.String(100))

class Plane(db.Model):
    id = db.Column(db.String, primary_key=True)
    plane_name = db.Column(db.String(100))
    max_range = db.Column(db.String(100))
    max_speed = db.Column(db.Integer)
    max_passenger_number = db.Column(db.Integer)
    tech_chceck_date = db.Column(db.DateTime(timezone=True),default=func.now())
    expire_date = db.Column(db.DateTime(timezone=True),default=func.now())

class Luggage(db.Model):
    id = db.Column(db.String, primary_key=True)
    flight_id = db.Column(db.Integer)
    weight = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Booking(db.Model):
    id = db.Column(db.String, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey("flight.flight_id"))
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Pilot(db.Model):
    id = db.Column(db.String, primary_key=True)


class Admin(db.Model):
    id = db.Column(db.String, primary_key=True)


class Customer(db.Model):
    id = db.Column(db.String, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("booking.id"))


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    bought = db.Column(db.Boolean, default=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    amount = db.Column(db.Integer, default=1)
    flight_id = db.Column(db.Integer, db.ForeignKey("flight.flight_id"))
    cart_id = db.Column(db.Integer, db.ForeignKey("cart.id"))

