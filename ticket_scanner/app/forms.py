from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired
from models import open_summits


# Forms
class PostCodeForm(FlaskForm):
    summit = SelectField('Текущее Событие', render_kw={'placeholder': 'Выбирите событие'},
                         validators=[DataRequired()],
                         choices=open_summits)
    code = StringField('Отправить код', render_kw={'placeholder': 'Введите код билета'},
                       validators=[DataRequired()])
