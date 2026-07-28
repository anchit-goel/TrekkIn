from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from flask_cors import CORS 
from flask_jwt_extended import JWTManager
from config import Config


db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    from app.api.auth_routes import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.api.admin_routes import admin_bp
    app.register_blueprint(admin_bp)
    
    return app

