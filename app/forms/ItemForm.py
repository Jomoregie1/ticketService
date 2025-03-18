from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class ItemForm(FlaskForm):
    manufacturerid = SelectField("Manufacturer", choices=[], coerce=int, validators=[DataRequired()])
    model = StringField("Model", validators=[DataRequired(), Length(min=2, max=100)])
    typeid = SelectField("Type", choices=[], coerce=int, validators=[DataRequired()])
    market_price = FloatField("Market Price", validators=[DataRequired(), NumberRange(min=1)])

    submit = SubmitField("Add Item")