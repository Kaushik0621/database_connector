from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/material.db'
db = SQLAlchemy(app)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50), nullable=False)
    material_texture = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Material database created.")
