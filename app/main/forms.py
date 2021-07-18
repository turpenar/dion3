from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, SubmitField, HiddenField, BooleanField
from wtforms.validators import DataRequired, NumberRange

from app.main import config

stats_list = config.get_stats_data_file()
skills_data_file = config.get_skill_data_file()

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
    gender = SelectField(u'Gender', choices=config.gender_choices)
    profession = SelectField(u'Profession', choices=config.profession_choices)
    
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
            self.stat_total_validation.errors.append('Total stats must be less than ' + str(config.available_stat_points))
            return False
        return True
    
for stat in stats_list:
    setattr(NewCharacterForm, stat, IntegerField(stat, validators=[DataRequired(), NumberRange(min=20, max=100, message="Please choose a number between 20 and 100")]))
  
  
class SkillsForm(FlaskForm):
    
    physical_training_points_var = IntegerField('Physical Training Points', id="physical_training_points_var", validators=[NumberRange(min=0, message="You do not have enough physical training points")])
    mental_training_points_var = IntegerField('Mental Training Points', id="mental_training_points_var", validators=[NumberRange(min=0, message="You do not have enough mental training points")])

    submit = SubmitField('Update Skills')
    
for category in skills_data_file:
    for skill in skills_data_file[category]:
        setattr(SkillsForm, skill, IntegerField(skill, id="skill_value_var_" + skill))
