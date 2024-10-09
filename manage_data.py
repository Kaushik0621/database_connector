from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_BINDS'] = {
    'material': 'sqlite:///../instance/material.db',
    'color': 'sqlite:///../instance/color.db'
}
db = SQLAlchemy(app)

class Material(db.Model):
    __bind_key__ = 'material'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50), nullable=False)
    material_texture = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Color(db.Model):
    __bind_key__ = 'color'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    return render_template('index_manage.html')

@app.route('/add_material', methods=['GET', 'POST'])
def add_material():
    if request.method == 'POST':
        company_name = request.form['company_name']
        material_texture = request.form['material_texture']
        price = float(request.form['price'])
        unit = request.form['unit']
        price_per_sq_meter = convert_to_sq_meter(price, unit)
        
        new_material = Material(company_name=company_name, material_texture=material_texture, price=price_per_sq_meter)
        db.session.add(new_material)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_material.html')

@app.route('/add_color', methods=['GET', 'POST'])
def add_color():
    if request.method == 'POST':
        company_name = request.form['company_name']
        color = request.form['color']
        price = float(request.form['price'])
        unit = request.form['unit']
        price_per_sq_meter = convert_to_sq_meter(price, unit)
        
        new_color = Color(company_name=company_name, color=color, price=price_per_sq_meter)
        db.session.add(new_color)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_color.html')

@app.route('/view_materials', methods=['GET', 'POST'])
def view_materials():
    if request.method == 'POST':
        selected_ids = request.form.getlist('selected')
        for id in selected_ids:
            material = Material.query.get(id)
            db.session.delete(material)
        db.session.commit()
        return redirect(url_for('view_materials'))
    materials = Material.query.all()
    return render_template('view_materials.html', materials=materials)

@app.route('/view_colors', methods=['GET', 'POST'])
def view_colors():
    if request.method == 'POST':
        selected_ids = request.form.getlist('selected')
        for id in selected_ids:
            color = Color.query.get(id)
            db.session.delete(color)
        db.session.commit()
        return redirect(url_for('view_colors'))
    colors = Color.query.all()
    return render_template('view_colors.html', colors=colors)

def convert_to_sq_meter(price, unit):
    if unit == 'sq_inch':
        return price * 1550.003
    elif unit == 'sq_cm':
        return price * 10000
    return price

if __name__ == '__main__':
    app.run(debug=True)
