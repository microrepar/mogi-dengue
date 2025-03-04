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
app.config['WTF_CSRF_ENABLED'] = False

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

db.init_app(app)
migrate.init_app(app, db)
csrf.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = CalculoForm()
    usuario = validacao_form(form)
    if usuario is not None:
        return render_template('resultado.html', context=usuario)
    return render_template('index.html', form=form)


@app.route('/iframe', methods=['GET', 'POST'])
def iframe():
    form = CalculoForm()
    usuario = validacao_form(form)
    if usuario is not None:
        return render_template('resultado_iframe.html', context=usuario)
    return render_template('index_iframe.html', form=form)


def validacao_form(form):
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
        return usuario


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
    gender = RadioField('Gênero', choices=[('male', 'Masculino'), ('female', 'Feminino')], 
                        validators=[InputRequired(message="Este campo é obrigatório.")])
    
    age = IntegerField('Idade', validators=[InputRequired(message="Este campo é obrigatório."),
                                            NumberRange(message='O campo idade dever 0 ou maior', min=0)])
    weight = DecimalField('Peso(kg)', validators=[InputRequired(message="Este campo é obrigatório."),
                                                  NumberRange(min=1)])
    date_input = DateField('Data de início dos sintomas', validators=[InputRequired(message="Este campo é obrigatório.")])
    submit = SubmitField('Calcular')

    def validate_date_input(form, field):
        if field.data < (datetime.date.today() - datetime.timedelta(days=30)) or field.data > datetime.date.today():
            raise ValidationError('Atenção! A data de início dos sintomas não deve ser anterior a 30 dias ou maior que a data atual.')


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    PROPORCAO = ('Sendo 1/3 de sais de reidratação oral e no início com volume maior. '
                 'Para os 2/3 restantes, efetuar injestão de liquídos caseiros (água, '
                 'suco de frutas, soro caseiro, chás, água de coco, etc...)')


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
            self.total_liquido_ml = 130 *self.weight
            self.formula = '130ml/kg/dia'
        elif self.weight <= 20:
            self.total_liquido_ml =  100 * self.weight
            self.formula = '100ml/Kg/dia'
        elif self.weight <= 30:
            self.total_liquido_ml = 80 * self.weight
            self.formula = '80ml/Kg/dia'
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
