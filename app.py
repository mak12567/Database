from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Configure the database connection using the Render PostgreSQL URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define a model for storing bot users
class BotUser(db.Model):
    __tablename__ = 'bot_users'
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(80))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    language_code = db.Column(db.String(10))

    def __init__(self, telegram_id, username, first_name, last_name, language_code):
        self.telegram_id = telegram_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.language_code = language_code

# Endpoint to create or update a bot user
@app.route('/bot-users/list/', methods=['POST'])
def create_bot_user():
    try:
        user_data = request.json
        
        # Validate that required fields are provided
        if 'telegram_id' not in user_data:
            return jsonify({"error": "telegram_id is required"}), 400
        
        # Check if the user already exists
        user = BotUser.query.filter_by(telegram_id=user_data['telegram_id']).first()

        if user:
            # Update existing user
            user.username = user_data.get('username', user.username)
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.language_code = user_data.get('language_code', user.language_code)
            db.session.commit()
            return jsonify({"message": "User updated successfully", "user": user_data}), 200
        else:
            # Create a new user
            new_user = BotUser(
                telegram_id=user_data['telegram_id'],
                username=user_data.get('username'),
                first_name=user_data.get('first_name'),
                last_name=user_data.get('last_name'),
                language_code=user_data.get('language_code')
            )
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"message": "User added successfully", "user": user_data}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
