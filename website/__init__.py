from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_dance.contrib.github import make_github_blueprint, github
from flask_mail import Mail
import toml

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
app.config.from_file("config.toml", load=toml.load)
app.config['SECRET_KEY'] = '1234'
DB_NAME = "database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
db = SQLAlchemy()
db.init_app(app)

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

except:
    print("Cant create SU")