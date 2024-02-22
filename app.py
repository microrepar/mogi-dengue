import datetime
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import (DateField, DecimalField, IntegerField, RadioField,
                     SubmitField, ValidationError)
from wtforms.validators import InputRequired, NumberRange

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'mySecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI') or 'sqlite:///dados.db'

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

db.init_app(app)
migrate.init_app(app, db)
csrf.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CalculoForm()
    if form.validate_on_submit():
        # Criar um novo usuario com os dados do formulário
        usuario = Usuario(
            gender=form.gender.data,
            age=form.age.data,
            weight=form.weight.data,
            date=form.date_input.data
        )
        usuario.calcular()
        # Adicionar o usuario ao banco de dados
        db.session.add(usuario)
        db.session.commit()
        return render_template('resultado.html', context=usuario)
    return render_template('index.html', form=form)


@app.route('/api/usuarios')
def get_usuarios():
    usuarios = Usuario.query.all()
    usuarios_json = []
    for usuario in usuarios:
        usuarios_json.append({
            'id': usuario.id,
            'gender': usuario.gender,
            'age': usuario.age,
            'weight': usuario.weight,
            'date': usuario.date.isoformat(),
            'created_at': usuario.created_at.isoformat(),
        })
    return jsonify(usuarios_json)


class CalculoForm(FlaskForm):
    gender = RadioField('Sexo', choices=[('male', 'Masculino'), ('female', 'Feminino')], validators=[InputRequired(message="Este campo é obrigatório.")])
    age = IntegerField('Idade', validators=[InputRequired(message="Este campo é obrigatório."),
                                            NumberRange(min=1)])
    weight = DecimalField('Peso(kg)', validators=[InputRequired(message="Este campo é obrigatório."),
                                                  NumberRange(min=1)])
    date_input = DateField('Data de início dos sintomas', validators=[InputRequired(message="Este campo é obrigatório.")])
    submit = SubmitField('Calcular')

    def validate_date_input(form, field):
        if field.data.year != 2024 or field.data > datetime.date.today():
            raise ValidationError('A data deve ser em 2024 e não pode ser maior que a data atual.')

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    PROPORCAO = '1/3 de solução de reidratação oral e 2/3 de outros liquídos.'

    def __str__(self):
        return (
            f'Usuario('
            f'genero={self.gender}, '
            f'idade={self.age}, '
            f'altura={self.weight}, '
            f'data={self.date}, '
            f'criado_em={self.created_at}'
            f')'
        )
    
    def calcular(self) :
        if self.weight <= 10:
            self.total_liquido_ml = self.weight * 100
            self.formula = '100ml/kg/dia'
        elif self.weight <= 20:
            self.total_liquido_ml = 1000 + (self.weight - 10) * 50  
            self.formula = '1.000ml + 50ml/Kg/dia para cada kg acima de 10kg'
        elif self.weight <= 30:
            self.total_liquido_ml = 1500 + (self.weight - 20) * 20  
            self.formula = '1.500ml + 20ml/Kg/dia para cada kg acima de 20kg'
        else:
            self.total_liquido_ml = 60 * self.weight
            self.formula = '60ml/Kg/dia'

    def  get_qtde_liquido(self):
        return f'{round(self.total_liquido_ml,0)}ml'


if __name__ == '__main__':
    # Criar uma instância do contexto da aplicação Flask
    with app.app_context():
        # Criar as tabelas no banco de dados
        db.create_all()
    # Iniciar o aplicativo Flask
    app.run(host='0.0.0.0', port=5000, debug=True)

