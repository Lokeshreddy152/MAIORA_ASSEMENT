from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import requests

app = Flask(__name__)

# Configuring PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2677@localhost/Joker_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initializing Postgres_database to app
db = SQLAlchemy(app)

# Database model to store jokes
class Joke(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(100))
    type = db.Column(db.String(50))
    joke = db.Column(db.Text)
    setup = db.Column(db.Text)
    delivery = db.Column(db.Text)
    nsfw = db.Column(db.Boolean)
    political = db.Column(db.Boolean)
    sexist = db.Column(db.Boolean)
    safe = db.Column(db.Boolean)
    lang = db.Column(db.String(10))


@app.route('/fetch_jokes', methods=['GET'])
def fetch_jokes():
    try:
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if 'Joker' not in tables:
            db.create_all()
        
        # Fetch 100 jokes from JokeAPI
        url = 'https://v2.jokeapi.dev/joke/Any?amount=100'
        response = requests.get(url)

        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch jokes from external API'}), 500

        jokes_data = response.json().get('jokes', [])


        for joke in jokes_data:
            # Extract relevant data
            category = joke.get('category')
            type_ = joke.get('type')
            nsfw = joke['flags'].get('nsfw')
            political = joke['flags'].get('political')
            sexist = joke['flags'].get('sexist')
            safe = joke.get('safe')
            lang = joke.get('lang')

            if type_ == 'single':
                joke_text = joke.get('joke')
                setup, delivery = None, None
            else:
                setup = joke.get('setup')
                delivery = joke.get('delivery')
                joke_text = None

            # Create Joke object and store in the database
            new_joke = Joke(
                category=category,
                type=type_,
                joke=joke_text,
                setup=setup,
                delivery=delivery,
                nsfw=nsfw,
                political=political,
                sexist=sexist,
                safe=safe,
                lang=lang
            )

            db.session.add(new_joke)

        # Commit the transaction
        db.session.commit()

        return jsonify({'message': 'Jokes fetched and stored in the database successfully!'}), 201

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
