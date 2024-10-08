from flask import Flask, redirect, url_for, session, request, jsonify, render_template
import os
import json
from .models import db, Customer, Order
from authlib.integrations.flask_client import OAuth
from flask_migrate import Migrate
from datetime import datetime

# Initialize OAuth and Migrate instances
oauth = OAuth()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Define the database path dynamically
    db_path = os.path.join(os.path.dirname(__file__), 'customers_orders.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    # Print the database URI for debugging
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = '9RDcyhM8K50jsA8X4ZymxVMdsBkO_VnrpMLbuJuX5YXDXZi0d7pXV5nc1RTuzRdC'

    # Define the path to the JSON file
    json_path = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
    
    # Print the path for debugging
    print(f"Looking for file at: {json_path}")
    
    # Load client secrets
    with open(json_path) as f:
        secrets = json.load(f)
    
    auth0_config = secrets['web']
    app.config['AUTH0_CLIENT_ID'] = auth0_config['client_id']
    app.config['AUTH0_CLIENT_SECRET'] = auth0_config['client_secret']
    app.config['AUTH0_DOMAIN'] = auth0_config['issuer'].replace('https://', '').replace('/', '')
    app.config['AUTH0_CALLBACK_URL'] = auth0_config['redirect_uris'][0]

    # Initialize database and migration
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize OAuth
    oauth.init_app(app)
    auth0 = oauth.register(
        'auth0',
        client_id=app.config['AUTH0_CLIENT_ID'],
        client_secret=app.config['AUTH0_CLIENT_SECRET'],
        server_metadata_url=f"https://{app.config['AUTH0_DOMAIN']}/.well-known/openid-configuration",
        client_kwargs={
            'scope': 'openid profile email',
        },
        authorization_endpoint=auth0_config['auth_uri'],
        token_endpoint=auth0_config['token_uri'],
        issuer=auth0_config['issuer']
    )
    
    # Import routes blueprint
    from .routes import main
    app.register_blueprint(main)
    
    return app
