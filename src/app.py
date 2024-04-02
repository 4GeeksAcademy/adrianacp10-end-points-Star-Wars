import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Film, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def get_users():
    all_users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), all_users))
    
    return jsonify(all_users), 200


@app.route('/user/favorites/', methods=['GET'])
def get_user_favs():
    id = 1
    current_user = User.query.get(id)
    
    if not current_user:
        return jsonify({"message": "User not found"}), 404
    user_favorites = Favorite.query.filter_by(user=current_user).all()
    user_favorites = list(map(lambda x: x.serialize(), user_favorites))
    
    return jsonify(user_favorites), 200


@app.route('/characters', methods=['GET'])
def get_characters():
    all_characters = Character.query.all()
    all_characters = list(map(lambda x: x.serialize(), all_characters))
    
    return jsonify(all_characters), 200


@app.route('/characters/<int:character_id>', methods=['GET'])
def handle_character_id(character_id):
    character = Character.query.get(character_id)
    if character:
        character_info = {
            "character_id": character.character_id,
            "name": character.name,
            "gender": character.gender,
            "film_id": character.film_id,
            "homeworld_id": character.homeworld_id,
        }
        return jsonify(character_info), 200
    else:
        return jsonify({"msg": "This character doesn't exist"}), 404
      

@app.route('/characters', methods=['POST'])
def add_characters():
    body = request.get_json()
    gender = body.get('gender')
    name = body.get('name')
    homeworld_id = body.get('homeworld_id')
    film_id = body.get('film_id')

    required_fields = [gender, name, homeworld_id, film_id]

    if any(field is None for field in required_fields):
        return jsonify({'error': 'Gender, name, homeworld_id and film_id are required fields'}), 400
    
    try:
        new_character = Character(gender=gender, name=name,homeworld_id = homeworld_id, film_id = film_id )
        db.session.add(new_character)
        db.session.commit()
        return jsonify({'response': 'Success! Character added.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/planets', methods=['GET'])
def get_planets():
    all_planets = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), all_planets))

    return jsonify(all_planets), 200


@app.route('/planets', methods=['POST'])
def add_planet():
    body = request.get_json()
    climate = body.get('climate')
    name = body.get('name')
    resident_id = body.get('resident_id')
    film_id = body.get('film_id')
    
    required_fields = [climate, name, resident_id, film_id]

    if any(field is None for field in required_fields):
        return jsonify({'error': 'Climate, name, resident_id and film_id are required fields'}), 400
    
    try:
        new_planet = Planet(climate=climate, name=name,resident_id = resident_id, film_id = film_id )
        db.session.add(new_planet)
        db.session.commit()
        return jsonify({'response': 'Success! Planet added.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@app.route('/planets/<int:planet_id>', methods=['GET'])
def handle_planet_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        planet_info = {
            "planet_id": planet.planet_id,
            "name": planet.name,
            "climate": planet.climate,
            "film_id" : planet.film_id,
            "resident_id": planet.resident_id,
        }
        return jsonify(planet_info), 200
    else:
        return jsonify({"msg": "This planet doesn't exist."}), 404


@app.route('/films', methods=['GET'])
def get_films():
    all_films = Film.query.all()
    all_films = list(map(lambda x: x.serialize(), all_films))

    return jsonify(all_films), 200


@app.route('/favorites', methods=['GET'])
def get_favorites():
    all_favorites = Favorite.query.all()
    all_favorites = list(map(lambda x: x.serialize(), all_favorites))

    return jsonify(all_favorites), 200


@app.route('/favorites', methods=['POST'])
def add_favorites():
    body = request.get_json()
    user_id = 1
    character_id = body.get('character_id')
    planet_id = body.get('planet_id')
    
    if character_id is None and planet_id is None:
        return jsonify({'error': 'You must provide either character_id or planet_id'}), 400
    
    try:
        new_favorite = Favorite(user_id=user_id, character_id=character_id, planet_id=planet_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({'response': 'Success! Favorite added.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    

@app.route('/favorites/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = 1
    requested_planet_id = Planet.query.get(planet_id)
    
    if requested_planet_id is None:
        return jsonify({'error': 'The planet_id field is required.'}), 400
    
    try:
        new_favorite_planet = Favorite(user_id=user_id, planet_id=requested_planet_id.planet_id)
        db.session.add(new_favorite_planet)
        db.session.commit()
        return jsonify({'response': 'Sucess! Favorite planet added.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    

@app.route('/favorites/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = 1
    requested_planet = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    
    if requested_planet is None:
        return jsonify({'error': 'You must provide a planet_id'}), 400
    
    try:
        db.session.delete(requested_planet)
        db.session.commit()
        return jsonify({'response': 'Deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400    
    

@app.route('/favorites/chaaracter/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):
    user_id = 1
    requested_character = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()
    
    if requested_character is None:
        return jsonify({'error': 'You must provide a character_id'}), 400
    
    try:
        db.session.delete(requested_character)
        db.session.commit()
        return jsonify({'response': 'Deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400       


@app.route('/favorites/characters/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    user_id = 1
    requested_character_id = Character.query.get(character_id)
    
    if requested_character_id is None:
        return jsonify({'error': 'You must provide a character_id'}), 400
    
    try:
        new_favorite_character = Favorite(user_id=user_id, character_id=requested_character_id.character_id)
        db.session.add(new_favorite_character)
        db.session.commit()
        return jsonify({'response': 'Deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400  



if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)