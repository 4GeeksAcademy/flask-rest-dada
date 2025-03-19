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


@app.route('/user/favorite', methods=['GET'])
def get_favorite_user():
    pass

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
    if not data or "model" not in data or "speed" not in data or "pilot" not in data or "lenght" not in data:
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
