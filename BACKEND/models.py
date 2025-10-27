from db import db
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    organization = db.Column(db.String(150))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class FoodPost(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    food = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    quantity = db.Column(db.String(50), nullable=False)
    expiry_time = db.Column(db.String(20))
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    allergens = db.Column(db.String(200))
    status = db.Column(db.String(20), default='available')
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    restaurant_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    claimed_by_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=True)
