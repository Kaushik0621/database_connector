from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coating_systems.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Association table for many-to-many relationship with extra data (ratio)
system_materials = db.Table('system_materials',
    db.Column('system_id', db.Integer, db.ForeignKey('system.id')),
    db.Column('material_id', db.Integer, db.ForeignKey('material.id')),
    db.Column('ratio', db.Float)
)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price_per_unit = db.Column(db.Float)
    systems = db.relationship('System', secondary=system_materials, backref='materials')

class System(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    total_price = db.Column(db.Float)  # Stores the total price

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/materials')
def materials():
    materials = Material.query.all()
    return render_template('materials.html', materials=materials)

@app.route('/add_material', methods=['GET', 'POST'])
def add_material():
    if request.method == 'POST':
        name = request.form['name']
        price_per_unit = float(request.form['price_per_unit'])
        new_material = Material(name=name, price_per_unit=price_per_unit)
        db.session.add(new_material)
        db.session.commit()
        return redirect(url_for('materials'))
    return render_template('add_material.html')

@app.route('/delete_material', methods=['POST'])
def delete_material():
    ids = request.form.getlist('delete_ids')
    for id in ids:
        material = Material.query.get(int(id))
        db.session.delete(material)
    db.session.commit()
    return redirect(url_for('materials'))

@app.route('/systems')
def systems():
    systems_data = []
    systems = System.query.all()
    
    for system in systems:
        materials_with_ratios = []
        total_price = 0.0
        total_ratio = 0.0
        for material in system.materials:
            ratio = db.session.execute(
                text("SELECT ratio FROM system_materials WHERE system_id=:sid AND material_id=:mid"),
                {'sid': system.id, 'mid': material.id}
            ).fetchone()[0]
            total_ratio += ratio
            total_price += material.price_per_unit * ratio
            materials_with_ratios.append({'material': material.name, 'ratio': ratio})
        
        # Calculate price per unit (weighted average based on ratio)
        price_per_unit = total_price / total_ratio if total_ratio else 0
        
        systems_data.append({
            'id': system.id,
            'name': system.name,
            'price_per_unit': price_per_unit,
            'materials': materials_with_ratios
        })

    return render_template('systems.html', systems=systems_data)

@app.route('/add_system', methods=['GET', 'POST'])
def add_system():
    materials = Material.query.all()
    if request.method == 'POST':
        name = request.form['name']
        ratios = {}
        total_price = 0.0
        for material in materials:
            ratio = request.form.get(f'ratio_{material.id}')
            if ratio:
                ratio = float(ratio)
                ratios[material] = ratio
                total_price += material.price_per_unit * ratio
        new_system = System(name=name, total_price=total_price)
        db.session.add(new_system)
        db.session.commit()
        for material, ratio in ratios.items():
            db.session.execute(system_materials.insert().values(
                system_id=new_system.id,
                material_id=material.id,
                ratio=ratio
            ))
        db.session.commit()
        return redirect(url_for('systems'))
    return render_template('add_system.html', materials=materials)

@app.route('/delete_system', methods=['POST'])
def delete_system():
    ids = request.form.getlist('delete_ids')
    for id in ids:
        system = System.query.get(int(id))
        db.session.delete(system)
    db.session.commit()
    return redirect(url_for('systems'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
