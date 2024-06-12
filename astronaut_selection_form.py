from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, RadioField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email


class AstronautSelectionForm(FlaskForm):
    last_name = StringField('Фамилия', validators=[DataRequired()])
    first_name = StringField('Имя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    education = StringField('Образование', validators=[DataRequired()])
    profession = SelectField('Выбор основной профессии', choices=[
        ("инженер-исследователь", "Инженер-исследователь"),
        ("пилот", "Пилот"),
    ], validators=[DataRequired()])
    gender = RadioField('Пол', choices=[('male', 'Мужской'), ('female', 'Женский')],
                        validators=[DataRequired()])
    motivation = TextAreaField('Мотивация', validators=[DataRequired()])
    stay_on_mars = RadioField('Готовы ли остаться на Марсе?', choices=[('yes', 'Да'), ('no', 'Нет')],
                              validators=[DataRequired()])
    photo = FileField('Фото', validators=[DataRequired()])
