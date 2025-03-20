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
from models import db, User, Planet, People, Vehicle, Favorite
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200


@app.route('/users', methods=['POST'])
def new_user():
    data = request.get_json()

    # Validación de datos
    if not data or "email" not in data or "first_name" not in data:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    new_user = User(
        email=data["email"],
        first_name=data["first_name"],
        password=data["password"],

        is_active=data.get("is_active", True)
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.serialize()), 201


@app.route('/favorites', methods=['GET'])
def get_all_favorites():
    favorites = Favorite.query.all()

    if not favorites:
        return jsonify({"message": "No hay favoritos registrados"}), 200

    result = []
    for fav in favorites:
        favorite_data = fav.serialize()

        # Obtener información del usuario que añadió el favorito
        user = User.query.get(fav.user_id)
        favorite_data["user_name"] = user.first_name if user else None
        favorite_data["user_email"] = user.email if user else None

        # Obtener nombres adicionales si existen
        if fav.planet_id:
            planet = Planet.query.get(fav.planet_id)
            favorite_data["planet_name"] = planet.planet_name if planet else None

        if fav.vehicles_id:
            vehicle = Vehicle.query.get(fav.vehicles_id)
            favorite_data["vehicle_model"] = vehicle.model if vehicle else None

        if fav.characters_id:
            character = People.query.get(fav.characters_id)
            favorite_data["character_name"] = character.name if character else None

        result.append(favorite_data)

    return jsonify(result), 200


@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    # Buscar el usuario
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Obtener los favoritos del usuario
    favorites = Favorite.query.filter_by(user_id=user_id).all()

    if not favorites:
        return jsonify({"message": f"{user.first_name} no tiene favoritos"}), 200

    result = []
    for fav in favorites:
        favorite_data = fav.serialize()

        # Agregar información del usuario dueño del favorito
        favorite_data["user_name"] = user.first_name
        favorite_data["user_email"] = user.email

        # Obtener nombres adicionales si existen
        if fav.planet_id:
            planet = Planet.query.get(fav.planet_id)
            favorite_data["planet_name"] = planet.planet_name if planet else None

        if fav.vehicles_id:
            vehicle = Vehicle.query.get(fav.vehicles_id)
            favorite_data["vehicle_model"] = vehicle.model if vehicle else None

        if fav.characters_id:
            character = People.query.get(fav.characters_id)
            favorite_data["character_name"] = character.name if character else None

        result.append(favorite_data)

    return jsonify(result), 200


@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.get_json()

    # Buscar el usuario por ID, nombre o email
    user_id = None
    if "user_id" in data:
        user_id = data["user_id"]
    elif "user_name" in data:
        user = User.query.filter_by(first_name=data["user_name"]).first()
        if not user:
            return jsonify({"error": f"El usuario '{data['user_name']}' no existe"}), 404
        user_id = user.id
    elif "user_email" in data:
        user = User.query.filter_by(email=data["user_email"]).first()
        if not user:
            return jsonify({"error": f"El usuario con email '{data['user_email']}' no existe"}), 404
        user_id = user.id
    else:
        return jsonify({"error": "Debe proporcionar user_id, user_name o user_email"}), 400

    # Buscar los IDs de los elementos favoritos
    planet_id = None
    if "planet_name" in data:
        planet = Planet.query.filter_by(
            planet_name=data["planet_name"]).first()
        if not planet:
            return jsonify({"error": f"El planeta '{data['planet_name']}' no existe"}), 404
        planet_id = planet.id

    vehicle_id = None
    if "vehicle_model" in data:
        vehicle = Vehicle.query.filter_by(model=data["vehicle_model"]).first()
        if not vehicle:
            return jsonify({"error": f"El vehículo '{data['vehicle_model']}' no existe"}), 404
        vehicle_id = vehicle.id

    character_id = None
    if "character_name" in data:
        character = People.query.filter_by(name=data["character_name"]).first()
        if not character:
            return jsonify({"error": f"El personaje '{data['character_name']}' no existe"}), 404
        character_id = character.id

    # Validar que al menos un favorito sea válido
    if not any([planet_id, vehicle_id, character_id]):
        return jsonify({"error": "Debe proporcionar un nombre válido de planeta, vehículo o personaje"}), 400

    # Crear el nuevo favorito
    new_favorite = Favorite(
        user_id=user_id,
        planet_id=planet_id,
        vehicles_id=vehicle_id,
        characters_id=character_id
    )

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite.serialize()), 201


@app.route('/favorites', methods=['DELETE'])
def delete_favorite():
    data = request.get_json()

    # Verifica se il JSON è stato inviato
    if not data:
        return jsonify({"error": "Il corpo della richiesta è vuoto"}), 400

    # Identificare l'utente usando first_name
    user = User.query.filter_by(first_name=data["first_name"]).first()
    if not user:
        return jsonify({"error": f"Utente '{data['first_name']}' non trovato"}), 404

    user_id = user.id  # Otteniamo l'ID dell'utente

    # Identificare il tipo di preferito da eliminare
    favorite = None
    if "planet_name" in data:
        planet = Planet.query.filter_by(
            planet_name=data["planet_name"]).first()
        if not planet:
            return jsonify({"error": f"Pianeta '{data['planet_name']}' non trovato"}), 404
        favorite = Favorite.query.filter_by(
            user_id=user_id, planet_id=planet.id).first()

    elif "vehicle_model" in data:
        vehicle = Vehicle.query.filter_by(model=data["vehicle_model"]).first()
        if not vehicle:
            return jsonify({"error": f"Veicolo '{data['vehicle_model']}' non trovato"}), 404
        favorite = Favorite.query.filter_by(
            user_id=user_id, vehicles_id=vehicle.id).first()

    elif "character_name" in data:
        character = People.query.filter_by(name=data["character_name"]).first()
        if not character:
            return jsonify({"error": f"Personaggio '{data['character_name']}' non trovato"}), 404
        favorite = Favorite.query.filter_by(
            user_id=user_id, characters_id=character.id).first()

    else:
        return jsonify({"error": "Devi specificare planet_name, vehicle_model o character_name"}), 400

    # Se il preferito non è stato trovato
    if not favorite:
        return jsonify({"error": "Il preferito non esiste per questo utente"}), 404

    # Eliminazione del preferito
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Preferito eliminato correttamente"}), 200


# endpoint planet

@app.route('/planets', methods=['GET'])
def gate_all_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200


@app.route('/planet/<int:id>', methods=['GET'])
def get_planet(id):
    planet = Planet.query.get(id)
    if planet is None:
        return jsonify({
            "error": "Planeta no encontrado"
        }), 404
    return jsonify(planet.serialize())


@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()

    # Validación de datos
    if not data or "planet_name" not in data or "periodo_de_rotacion" not in data or "climate" not in data or "poblation" not in data:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    new_planet = Planet(
        planet_name=data["planet_name"],
        periodo_de_rotacion=data["periodo_de_rotacion"],
        climate=data["climate"],
        poblation=data["poblation"]
    )

    db.session.add(new_planet)
    db.session.commit()

    return jsonify(new_planet.serialize()), 201

# endpoint people


@app.route('/people', methods=['GET'])
def get_people():
    peoples = People.query.all()
    return jsonify([peoples.serialize() for peoples in peoples]), 200


@app.route('/people', methods=['POST'])
def create_people():
    data = request.get_json()

    if not data or "name" not in data or "age" not in data or "hair_color" not in data or "birth_year" not in data:
        return jsonify({"error": f"faltan datos estos son los que has enviado"}), 400

    new_people = People(
        name=data['name'],
        age=data['age'],
        hair_color=data['hair_color'],
        birth_year=data['birth_year']
    )

    db.session.add(new_people)
    db.session.commit()

    return jsonify(new_people.serialize()), 201


@app.route('/people/<int:id>', methods=['GET'])
def get_person(id):
    person = People.query.get(id)
    if person is None:
        return jsonify({
            "error": "Usuario no encontrado"
        }), 404
    return jsonify(person.serialize())

# endpoint Vehicles


@app.route('/vehicles', methods=['GET'])
def gate_all_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify([vehicles.serialize() for vehicle in vehicles]), 200


@app.route('/vehicles', methods=['POST'])
def create_vehicle():
    data = request.get_json()

    # Validación de datos
    if not data or "model" not in data or "speed" not in data or "pilot" not in data or "length" not in data:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    new_vehicle = Vehicle(
        model=data["model"],
        speed=data["speed"],
        pilot=data["pilot"],
        length=data["length"]
    )

    db.session.add(new_vehicle)
    db.session.commit()

    return jsonify(new_vehicle.serialize()), 201


@app.route('/vehicle/<int:id>', methods=['GET'])
def get_vehicle(id):
    vehicle = Vehicle.query.get(id)
    if vehicle is None:
        return jsonify({
            "error": "Veiculo no encontrado"
        }), 404
    return jsonify(vehicle.serialize())

# endpoint user


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
