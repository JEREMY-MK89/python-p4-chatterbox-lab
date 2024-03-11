from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message
from datetime import datetime
from sqlalchemy_serializer import SerializerMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

class Message(db.Model, SerializerMixin):
    __tablename__ = 'messages'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def serialize(self):
        return {
            'id': self.id,
            'body': self.body,
            'username': self.username,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

@app.route('/messages', methods=['POST'])
def create_message():
    try:
        data = request.get_json()
        body = data.get('body')
        username = data.get('username')

        if not body or not username:
            return jsonify({'error': 'Missing required data: body or username'}), 400

        new_message = Message(body=body, username=username)
        db.session.add(new_message)
        db.session.commit()

        # Return the serialized message in the response
        return jsonify(new_message.serialize()), 201

    except Exception as e:
        error_message = f"Error creating message: {str(e)}"
        return jsonify({'error': error_message}), 500

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    try:
        data = request.get_json()
        new_body = data.get('body')

        if not new_body:
            return jsonify({'error': 'Missing required data: body'}), 400

        message = Message.query.get(id)

        if not message:
            return jsonify({'error': 'Message not found'}), 404

        # Update the message's body
        message.body = new_body
        db.session.commit()

        # Return the serialized updated message in the response
        return jsonify(message.serialize()), 200

    except Exception as e:
        error_message = f"Error updating message: {str(e)}"
        return jsonify({'error': error_message}), 500

# ... (other routes)

if __name__ == '__main__':
    app.run(port=5555)
