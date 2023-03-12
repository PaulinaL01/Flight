from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_dance.contrib.github import make_github_blueprint, github
from flask_mail import Mail
import toml
from werkzeug.security import generate_password_hash

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
app.config.from_file("config.toml", load=toml.load)
app.config['SECRET_KEY'] = '1234'
DB_NAME = "database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://user:password@db/baza"
db = SQLAlchemy()
db.init_app(app)
SQLALCHEMY_TRACK_MODIFICATIONS = False

blueprint = make_github_blueprint(
    client_id="Iv1.2febb8607328c8af",
    client_secret="01976bcddc0f3b9606fd7375cd669682b5d15d64",
)
app.register_blueprint(blueprint, url_prefix="/github_login")

loginManager = LoginManager()
loginManager.login_view = "login"
loginManager.init_app(app)


from .models import User, UserMixin
migration = Migrate(app=app, db=db)
mail = Mail(app=app)

from .views import *

@loginManager.user_loader
def load_user(id):
    from .models import User
    return User.query.get(int(id))

try:
    with app.app_context():
        if not User.query.filter_by(login="admin").first():
            user = User(login="admin", password=generate_password_hash("A1234567"), admin=True)
            db.session.add(user)
            db.session.commit()
        if len(Flight.query.all()) == 0:
            db.session.add(Flight(flight_number=1,
                                  departure_city="Warszawa",
                                  arrival_city="Poznan",
                                  departure_data=datetime(2021, 12, 20, 14, 00),
                                  arrival_data=datetime(2021, 12, 20, 18, 00),
                                  passengers_number=100))
            db.session.commit()

except Exception as e:
    print(f"Cant create SU: {e}")
