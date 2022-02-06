from werkzeug.security import generate_password_hash

from .utils import create_code
from .models import Flight, User


class DataContext:
    def __init__(self, db):
        self.db = db

    def get_all_departure_cities(self):
        flights = Flight.query.all()
        return [(flight.departure_city, flight.departure_city) for flight in flights]

    def get_all_arrival_cities(self):
        flights = Flight.query.all()
        return [(flight.arrival_city, flight.arrival_city) for flight in flights]

    def create_user(self, login, email, password, is_github_account=False, confirmed_email=False):
        if User.query.filter_by(login=login).first():
            return None, "User login exists!"
        elif User.query.filter_by(email=email).first():
            return None, "User email exists!"
        else:
            user = User(login=login, email=email,
                        password=generate_password_hash(password),
                        confirm_code=create_code(64),
                        is_github_account=is_github_account,
                        confirmed_email=confirmed_email)
            self.db.session.add(user)
            self.db.session.commit()
            user = User.query.filter_by(login=login, email=email).first()
            return user, "Account created! Confirm email adress"

    def get_user_by_login(self, login):
        return User.query.filter_by(login=login).first()

    def get_user_by_confirmation_code(self, code):
        return  User.query.filter_by(confirm_code=code).first()

    def get_flight_by_id(self, flight_id):
        return Flight.query.get(flight_id)

    def update_flight(self, flight_id, **kwargs):
        flight = self.get_flight_by_id(flight_id)
        if not flight:
            return
        for field_name, value in kwargs.items():
            setattr(flight, field_name, value)
        self.db.session.commit()


