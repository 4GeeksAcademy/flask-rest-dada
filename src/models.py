from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Planet(db.Model):

    __tablename__ = 'planet'

    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    planet_name = Column(String(100), nullable=False)
    periodo_de_rotacion = Column(Integer, nullable=False)
    climate = Column(String(100), nullable=False)
    poblation = Column(Integer, nullable=False)

    favorites = relationship('Favorite', backref="planet")

    def serialize(self):
        return {
            "id": self.id,
            "planet_name": self.planet_name,
            "periodo_de_rotacion": self.periodo_de_rotacion,
            "climate": self.climate,
            "poblation": self.poblation,
        }


class People(db.Model):

    __tablename__ = 'people'

    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    hair_color = Column(String(100), nullable=False)
    birth_year = Column(Integer, nullable=False)

    favorites = relationship('Favorite', backref="people")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "hair_color": self.hair_color,
            "birth_year": self.birth_year,
        }


class Vehicle(db.Model):

    __tablename__ = 'vehicle'

    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    model = Column(String(100), nullable=False)
    speed = Column(Integer, nullable=False)
    pilot = Column(String(100), nullable=False)
    lenght = Column(Integer, nullable=False)

    favorites = relationship('Favorite', backref="vehicles")

    def serialize(self):
        return {
            "id": self.id,
            "model": self.model,
            "speed": self.speed,
            "pilot": self.pilot,
            "lenght": self.lenght,
        }


class Favorite(db.Model):
    __tablename__ = 'favorite'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    planet_id = Column(Integer, ForeignKey('planet.id'))
    vehicles_id = Column(Integer, ForeignKey('vehicle.id'))
    characters_id = Column(Integer, ForeignKey('people.id'))

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "vehicles_id": self.vehicles_id,
            "characters_id": self.characters_id,
        }
