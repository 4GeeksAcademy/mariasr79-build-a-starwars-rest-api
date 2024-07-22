"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Character_fav, Planet, Planet_fav

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

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }
    return jsonify(response_body), 200

@app.route('/user/favorites', methods=['GET'])
def get_user_fav():
    users = User.query.all()
    user_favorites = []
    for user in users:
        user_favorites.append({
            "user_id": user.id,
            "username": user.username,
            "character_favorites": [character_fav.character.serialize() for character_fav in user.character_fav],
            "planet_favorites": [planet_fav.planet.serialize() for planet_fav in user.planet_fav]
        })
    return jsonify(user_favorites), 200

@app.route('/character', methods=['GET', 'POST'])
def handle_character():
    if request.method == 'POST':
        data = request.get_json()
        new_character = Character(
            name=data['name'],
            height=data['height'],
            mass=data['mass'],
            hair_color=data['hair_color'],
            skin_color=data['skin_color']
        )
        db.session.add(new_character)
        db.session.commit()
        return jsonify(new_character.serialize()), 201

    characters = Character.query.all()
    results = [character.serialize() for character in characters]
    if not characters:
        return jsonify(message="No se han encontrado characters"), 404
    return jsonify(results), 200

@app.route('/character/<int:character_id>', methods=['GET', 'DELETE'])
def handle_character_detail(character_id):
    character = Character.query.get(character_id)
    if character is None:
        return jsonify(message="Personaje no encontrado"), 404

    if request.method == 'DELETE':
        db.session.delete(character)
        db.session.commit()
        return jsonify(message="Character eliminado"), 200

    return jsonify(character.serialize()), 200

@app.route('/character_fav', methods=['GET', 'POST'])
def handle_character_fav():
    if request.method == 'POST':
        data = request.get_json()
        new_character_fav = Character_fav(
            user_id=data['user_id'],
            character_id=data['character_id']
        )
        db.session.add(new_character_fav)
        db.session.commit()
        return jsonify(new_character_fav.serialize()), 201

    characters_fav = Character_fav.query.all()
    results = [character_fav.serialize() for character_fav in characters_fav]
    if not characters_fav:
        return jsonify(message="No se han encontrado character favorites"), 404
    return jsonify(results), 200

@app.route('/planet', methods=['GET', 'POST'])
def handle_planet():
    if request.method == 'POST':
        data = request.get_json()
        new_planet = Planet(
            name=data['name'],
            population=data['population'],
            terrain=data['terrain'],
            climate=data['climate']
        )
        db.session.add(new_planet)
        db.session.commit()
        return jsonify(new_planet.serialize()), 201

    planets = Planet.query.all()
    results = [planet.serialize() for planet in planets]
    if not planets:
        return jsonify(message="No se han encontrado planets"), 404
    return jsonify(results), 200

@app.route('/planet/<int:planet_id>', methods=['GET', 'DELETE'])
def handle_planet_detail(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify(message="Planeta no encontrado"), 404

    if request.method == 'DELETE':
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message="Planet eliminado"), 200

    return jsonify(planet.serialize()), 200

@app.route('/planet_fav', methods=['GET', 'POST'])
def handle_planet_fav():
    if request.method == 'POST':
        data = request.get_json()
        new_planet_fav = Planet_fav(
            user_id=data['user_id'],
            planet_id=data['planet_id']
        )
        db.session.add(new_planet_fav)
        db.session.commit()
        return jsonify(new_planet_fav.serialize()), 201

    planets_fav = Planet_fav.query.all()
    results = [planet_fav.serialize() for planet_fav in planets_fav]
    if not planets_fav:
        return jsonify(message="No se han encontrado planet favorites"), 404
    return jsonify(results), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
