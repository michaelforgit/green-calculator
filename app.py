from flask import Flask, request, redirect, url_for
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,
                     RadioField, PasswordField, SubmitField, SelectField)
from wtforms.validators import InputRequired, Length
import os
SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

STATE_CHOICES = ['Tesla','Whip']

class CarForm(FlaskForm):
    mpg = IntegerField('Miles per gallon', validators=[InputRequired()])
    mpw = IntegerField("Miles per week", validators=[InputRequired()])
    gasPrice = IntegerField("Gas Price", validators=[InputRequired()])
    carSelect = SelectField("Select Car", choices=STATE_CHOICES, validators=[InputRequired()])
    carCost = IntegerField("Car Cost", validators=[InputRequired()])
    elecCost = IntegerField("Electricity Cost", validators=[InputRequired()])
    submit = SubmitField('See Results')

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/car/", methods=['GET', 'POST'])
def car():
    if request.method == 'POST':
        print("HELLO WORLD")
        print(request.form['mpw'])
    return render_template('car.html', form=CarForm())

@app.route("/house/", methods=['GET'])
def house():
    return render_template('house.html')

if __name__ == "__main__":
    app.run(debug=True)

