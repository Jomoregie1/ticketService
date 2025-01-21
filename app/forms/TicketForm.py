from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class TicketForm(FlaskForm):
    description = TextAreaField(
        "Description",
        validators=[
            DataRequired(message="Description is required."),
            Length(min=10, max=500, message="Description must be between 10 and 500 characters.")
        ]
    )

    itemid = SelectField(
        "Item",
        choices=[],
        coerce=int,
        validators=[DataRequired(message="Please select an item.")]
    )

    submit = SubmitField("Submit Ticket")
