from flask import Flask
from BACKEND.db import db
from BACKEND.routes import auth, food, delivery
from BACKEND.recommendation import bp as rec_bp
from flask_cors import CORS

app = Flask(__name__)

# --- CORS CONFIG ---
#CORS(app, origins="*", supports_credentials=True)
CORS(
    app,
    origins=["https://willowy-medovik-cae1cb.netlify.app", "http://localhost:3000"],
    supports_credentials=True
)

# --- SESSION CONFIG ---
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = False  # False for local dev
app.config.from_object('BACKEND.config.Config')
db.init_app(app)

# --- REGISTER BLUEPRINTS ---
app.register_blueprint(auth.bp, url_prefix='/api/auth')
app.register_blueprint(food.bp, url_prefix='/api/food')
app.register_blueprint(delivery.bp, url_prefix='/api/delivery')
app.register_blueprint(rec_bp, url_prefix="/api/recommendation")  # endpoint: /api/recommendation  # final endpoint: /api/chat

@app.route('/')
def index():
    return {'message': 'Surplus2Serve Backend API'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
