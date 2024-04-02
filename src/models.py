from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=True)
    password = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username
        }
    
class Planet(db.Model):
    __tablename__ = "planet"
    planet_id = db.Column(db.Integer, primary_key=True)
    climate = db.Column(db.String(200))
    name = db.Column(db.String(40), nullable=False)
    resident_id = db.Column(db.Integer ,nullable=False)
    film_id = db.Column(db.Integer,nullable=False) 

    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "planet_id": self.planet_id,
            "name": self.name,
            "climate": self.climate,
            "film_id" : self.film_id,
            "resident_id": self.resident_id,
        }
        
class Character(db.Model):
    __tablename__ = "character"
    character_id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(40))
    name = db.Column(db.String(40), unique=True, nullable=False)
    film_id = db.Column(db.Integer, nullable=False)
    homeworld_id = db.Column(db.Integer,db.ForeignKey('planet.planet_id'), nullable=False)
    planet = db.relationship(Planet)

    def __repr__(self):
        return '<Character %r>' % self.name

    def serialize(self):
        return {
            "character_id": self.character_id,
            "name": self.name,
            "gender": self.gender,
            "film_id" : self.film_id,
            "homeworld_id": self.homeworld_id,
        }

class Film(db.Model):
    __tablename__ = "film"
    film_id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer,db.ForeignKey('character.character_id') ,nullable=False)
    character = db.relationship(Character)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.planet_id') ,nullable=False)
    planet = db.relationship(Planet)
    director = db.Column(db.String(40), nullable=False)
    title = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Film %r>' % self.title

    def serialize(self):
        return {
            "film_id": self.film_id,
            "title": self.title,
            "director" : self.director,
            "character_id": self.character_id,
            "planet_id": self.planet_id,
        }
    
class Favorite(db.Model):
    __tablename__ = "favorite"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User)
    character_id = db.Column(db.Integer, db.ForeignKey('character.character_id'), nullable=True)
    character = db.relationship(Character)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.planet_id'), nullable=True)
    planet = db.relationship(Planet)

    def __repr__(self):
        return '<Favorite %r>' % self.id

    def serialize(self):
        if self.character_id is not None:
            fav_type = "character"
            fav_id = self.character_id
        elif self.planet_id is not None:
            fav_type = "planet"
            fav_id = self.planet_id
        else:
            fav_type = "unknown"
            fav_id = None    
        return {
            "id": self.id,
            "user_id": self.user_id,
            "fav_type": fav_type,
            "fav_id": fav_id,
        }