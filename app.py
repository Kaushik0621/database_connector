from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session management

# Define the absolute paths for both databases in the instance folder
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_BINDS'] = {
    'material': f'sqlite:///{os.path.join(basedir, "instance", "material.db")}',
    'color': f'sqlite:///{os.path.join(basedir, "instance", "color.db")}'
}
db = SQLAlchemy(app)

# Define the Material model for material.db
class Material(db.Model):
    __bind_key__ = 'material'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50), nullable=False)
    material_texture = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)

# Define the Color model for color.db
class Color(db.Model):
    __bind_key__ = 'color'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    material_companies = db.session.query(Material.company_name).distinct()
    color_companies = db.session.query(Color.company_name).distinct()
    combinations = session.get('combinations', [])
    return render_template('index.html', material_companies=material_companies, color_companies=color_companies, combinations=combinations)

@app.route('/add_combination', methods=['POST'])
def add_combination():
    material_id = request.form['material']
    color_id = request.form['color']
    material = db.session.get(Material, material_id)
    color = db.session.get(Color, color_id)
    if 'combinations' not in session:
        session['combinations'] = []
    session['combinations'].append({
        'material_company': material.company_name,
        'material_texture': material.material_texture,
        'material_price': material.price,
        'color_company': color.company_name,
        'color': color.color,
        'color_price': color.price
    })
    session.modified = True
    return redirect(url_for('index'))

@app.route('/delete_combination/<int:index>', methods=['POST'])
def delete_combination(index):
    combinations = session.get('combinations', [])
    if 0 <= index < len(combinations):
        combinations.pop(index)
    session['combinations'] = combinations
    session.modified = True
    return redirect(url_for('index'))

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'POST':
        areas = request.form.getlist('area')
        if 'total_costs' not in session:
            session['total_costs'] = []
        for i, combo in enumerate(session['combinations']):
            material_cost = combo['material_price'] * float(areas[i])
            color_cost = combo['color_price'] * float(areas[i])
            total_cost = material_cost + color_cost
            session['total_costs'].append({
                'material_company': combo['material_company'],
                'color_company': combo['color_company'],
                'material_texture': combo['material_texture'],
                'color': combo['color'],
                'area': areas[i],
                'total_cost': total_cost
            })
        session.modified = True
        return redirect(url_for('calculate'))
    total_costs = session.get('total_costs', [])
    return render_template('calculate.html', combinations=session['combinations'], total_costs=total_costs)

@app.route('/delete_calculation/<int:index>', methods=['POST'])
def delete_calculation(index):
    total_costs = session.get('total_costs', [])
    if 0 <= index < len(total_costs):
        total_costs.pop(index)
    session['total_costs'] = total_costs
    session.modified = True
    return redirect(url_for('calculate'))

@app.route('/get_materials/<company_name>')
def get_materials(company_name):
    materials = Material.query.filter_by(company_name=company_name).all()
    return jsonify(materials=[{'id': m.id, 'texture': m.material_texture, 'price': m.price} for m in materials])

@app.route('/get_colors/<company_name>')
def get_colors(company_name):
    colors = Color.query.filter_by(company_name=company_name).all()
    return jsonify(colors=[{'id': c.id, 'color': c.color, 'price': c.price} for c in colors])

if __name__ == '__main__':
    app.run(debug=True)
