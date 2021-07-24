from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, SubmitField, HiddenField, BooleanField, FieldList, FormField
from wtforms.validators import DataRequired, NumberRange

from app.main import config

stats_list = config.get_stats_data_file()

class LoginForm(FlaskForm):
    username = StringField('username', [DataRequired()])
    password = StringField('password', [DataRequired()])
    remember = BooleanField('remember me')
    submit = SubmitField('Login')
    
    
class SignUpForm(FlaskForm):
    username = StringField('username', [DataRequired()])
    password = StringField('password', [DataRequired()])
    submit = SubmitField('Sign Up')


class NewCharacterForm(FlaskForm):
    first_name = StringField('First Name', [DataRequired()])
    last_name = StringField('Last Name', [DataRequired()])
    gender = SelectField(u'Gender', id='gender', choices=config.gender_choices)
    profession = SelectField(u'Profession', id='profession', choices=config.profession_choices)
    heritage = SelectField(u'Heritage', id='heritage', choices=config.heritage_choices)

    stat_training_points_var = IntegerField('Stat Training Points', id="stat_training_points_var", validators=[NumberRange(min=0, message="You do not have enough stat training points")])
    
    stat_total_validation = IntegerField('stat_total_validation')
    
    submit = SubmitField('Create Character')
    
    def validate(self):
        
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        
        stat_total = 0
        for stat in stats_list:
            stat_total += int(getattr(self, stat).data)
            
        if stat_total >= config.available_stat_points:
            self.stat_total_validation.errors.append('Total stats cannot exceed ' + str(config.available_stat_points - 1))
            return False
        return True
    
for stat in stats_list:
    setattr(NewCharacterForm, stat, IntegerField(stat, id="stat_value_var_" + stat, validators=[DataRequired(), NumberRange(min=20, max=100, message="Please choose a number between 20 and 100")]))
  
  
class SkillEntryForm(FlaskForm):
    def __init__(self, skill_name):
        skill = IntegerField(skill_name, id="skill_value_var_" + skill_name)


class SkillsForm(FlaskForm):
    physical_training_points_var = IntegerField('Physical Training Points', id="physical_training_points_var", validators=[NumberRange(min=0, message="You do not have enough physical training points")])
    mental_training_points_var = IntegerField('Mental Training Points', id="mental_training_points_var", validators=[NumberRange(min=0, message="You do not have enough mental training points")])
    submit = SubmitField('Update Skills')


class SkillsProfessionForm(SkillsForm):
    pass


def add_skills_to_skill_form(profession):
    skill_data_file = config.get_skill_data_file(profession=profession)
    for category in skill_data_file:
        for skill in skill_data_file[category]:
            setattr(SkillsProfessionForm, skill, IntegerField(skill, id="skill_value_var_" + skill))
    return
