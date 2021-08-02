#!/usr/bin/env python

from flask import render_template, redirect, url_for, session, request, copy_current_request_context
from flask_socketio import emit, join_room, leave_room, disconnect
from flask_login import current_user, login_user, logout_user, login_required

from app import socketio, login, db
from app.main import main, config, player, actions, spells
from app.main.models import User, Character, Room
from app.main.forms import LoginForm, SignUpForm, NewCharacterForm, SkillsProfessionForm, add_skills_to_skill_form


stat_training_points = config.available_stat_points

@login.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None


@main.route('/')
@login_required
def index():
    return render_template('home.html')

@main.route('/home')
@login_required
def home():
    return render_template('home.html')


@main.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('main.index'))
        return '<h1>Invalid username or password</h1>'
    return render_template('/login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/signup', methods=['POST', 'GET'])
def signup():
    form = SignUpForm()
    
    if form.validate_on_submit():
        existing_user = db.session.query(User).filter_by(username=form.username.data).first()
        if existing_user == None:
            new_user = User(username=form.username.data)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            response = "You have created an account! Head back to the Log In screen to sign in."
        else:
            response = "User already exists! Head back to the Log in screen to sign in."
        return render_template('/signup_complete.html', response=response)
    return render_template('/signup.html', form=form)


@main.route('/signup_complete')
def signup_complete():
    return render_template('/signup_complete.html')


@main.route('/play')
@login_required
def play():
    return render_template('play.html', async_mode=socketio.async_mode)


@main.route('/characters', methods=['POST', 'GET'])
@login_required
def characters():
    
    characters = []
    character_names = []

    user = db.session.query(User).filter_by(username=current_user.username).first()

    if user: 
        if user.characters:
            for char in user.characters:
                characters.append(char.char)        
                character_names.append(char.char.first_name + " " + char.char.last_name)

        if request.method == "POST":
            current_character = request.form.get('character')
            current_character_split = current_character.split()
            current_character_firstname = current_character_split[0]
            user.current_character_first_name = current_character_split[0]
            current_character_lastname = current_character_split[1]
            user.current_character_last_name = current_character_split[1]
            db.session.commit()
            return render_template('/play.html', 
                    user=current_user.username,
                    character_first_name=current_character_firstname,
                    character_last_name=current_character_lastname)
    
    return render_template('/characters.html', Characters=character_names)


@main.route('/new_character', methods=['POST', 'GET'])
@login_required
def new_character():
        
    form = NewCharacterForm()
    
    stats = config.get_stats_data_file()
    
    stats_initial = {}
    stats_total = 0

    if form.validate_on_submit():
        
        result = request.form
        first_name = result['first_name']
        last_name = result['last_name']
        gender = result['gender']
        profession = result['profession']
        heritage = result['heritage']
        
        for stat in stats:
            stats_initial[stat.lower()] = int(result[stat])
            stats_total += stats_initial[stat.lower()]

        new_character = Character(char=player.create_character('new_player'))
        
        new_character.char.name = first_name
        new_character.first_name = first_name
        new_character.char.first_name = first_name
        new_character.last_name = last_name
        new_character.char.last_name = last_name
        new_character.char.gender = gender
        new_character.char.profession = profession
        new_character.char.heritage = heritage
        
        for stat in new_character.char.stats:
            new_character.char.stats[stat] = stats_initial[stat]
            
        new_character.char.set_character_attributes()    
        new_character.char.set_gender(new_character.char.gender)
        new_character.char.level_up_skill_points()

        user = db.session.query(User).filter_by(username=current_user.username).first()
        user.characters.append(new_character)
        
        db.session.add(new_character)
        db.session.commit()

        response = f"{first_name} {last_name} has been created! Head back to the characters to select and play."
              
        return render_template('/character_created.html', response=response)
        
    return render_template('/new_character.html', form=form, Stats=stats, total_stat_training_points=stat_training_points)


@main.route('/character_created')
@login_required
def character_created():
    return render_template('/character_created.html')


@main.route('/skills', methods=['POST', 'GET'])
@login_required
def skills_modify():

    user = db.session.query(User).filter_by(username=current_user.username).first()
    if not user.current_character_first_name:
        return '<h1>You do not yet have a character. Please create a new character or load a character.</h1>'

    character_file = db.session.query(Character).filter_by(first_name=user.current_character_first_name, last_name=user.current_character_last_name).first()
    add_skills_to_skill_form(profession=character_file.char.profession)
    form = SkillsProfessionForm()
    skill_data_file = config.get_skill_data_file(profession=character_file.char.profession)
    
    if form.validate_on_submit():
        result = request.form
        character_file.char.physical_training_points = result['physical_training_points_var']
        character_file.char.mental_training_points = result['mental_training_points_var']
        for skill in character_file.char.skills:
            character_file.char.skills[skill] = int(result[skill])
            if character_file.char.skills[skill] > 40:
                character_file.char.skills_bonus[skill] = 140 + character_file.char.skills[skill] - 40
            elif character_file.char.skills[skill] > 30:
                character_file.char.skills_bonus[skill] = 120 + (character_file.char.skills[skill] - 30) * 2
            elif character_file.char.skills[skill] > 20:
                character_file.char.skills_bonus[skill] = 90 + (character_file.char.skills[skill] - 20) * 3
            elif character_file.char.skills[skill] > 10:
                character_file.char.skills_bonus[skill] = 50 + (character_file.char.skills[skill] - 10) * 4
            else:
                character_file.char.skills_bonus[skill] = character_file.char.skills[skill] * 5
            if skill == "spell_research":
                all_base_spells = spells.get_spells_skill_level(spell_base=character_file.char.profession, skill_level=int(result[skill]))
                spells_forget = character_file.char.check_spells_forget(spell_base=character_file.char.profession, spell_numbers=all_base_spells)
                spells_learned = character_file.char.check_spells_learned(spell_base=character_file.char.profession, spell_numbers=all_base_spells)
                character_file.char.learn_spells(spell_base=character_file.char.profession, spell_numbers=all_base_spells)
                if spells_forget:
                    spell_message = f""""\
You unlearned the following spells:
{spells_forget}\
                    """
                elif spells_learned:
                    spell_message = f"""\
You learned new spells! Type SPELLS to access a list of all spells you know.
{spells_learned}\
                    """
                else:
                    spell_message = """"""
        db.session.commit()
        character_announcement(announcement=f"""\
You have updated your skills! Type SKILLS to see your new skill values and bonuses.

{spell_message}\
        """)
        response = "Skills updated! Please close the window and return to the game window."
        return render_template('/skills_updated.html', response=response)
    
    return render_template('/skills.html', form=form, player=character_file.char, skillDataFile=skill_data_file)


@main.route('/skills_updated')
def skills_updated():
    return render_template('/skills_updated.html')


@socketio.event
def my_event(message):
    emit('game_action',
         {'data': message['data']}
         )
    character_file = db.session.query(Character).filter_by(first_name=message['first_name'], last_name=message['last_name']).first()
    if character_file:
        character = character_file.char
        room_file = db.session.query(Room).filter_by(x=character.location_x, 
                                                     y=character.location_y, 
                                                     area_name=character.area_name
                                                     ).first()
    else:
        emit('game_action',
             {'data': 'You have not loaded a character'}
             )
        return

    action_result = actions.do_action(action_input=message['data'], character_file=character_file, room_file=room_file)

    if not action_result['action_success']:
        emit('game_event',
            {'data': action_result['action_error']}
            )
    else:
        if action_result['room_change']['room_change_flag'] == True:
            emit('game_event',
                {'data': action_result['room_change']['leave_room_text']}, to=str(action_result['room_change']['old_room']), include_self=False
                )
            leave_room(room=str(action_result['room_change']['old_room']))
            join_room(room=str(action_result['room_change']['new_room']))
            emit('game_event',
                {'data': action_result['room_change']['enter_room_text']}, to=str(action_result['room_change']['new_room']), include_self=False
                )
        if action_result['area_change']['area_change_flag'] == True:
            leave_room(room=str(action_result['area_change']['old_area']))
            join_room(room=str(action_result['area_change']['new_area']))
        if action_result['character_output']['character_output_flag'] == True:
            emit('game_event',
                {'data': action_result['character_output']['character_output_text']}
                )
        if action_result['display_room']['display_room_flag']:
            emit('game_event',
                {'data': action_result['display_room']['display_room_text']}
                )
        if action_result['room_output']['room_output_flag'] == True:
            emit('game_event',
                {'data': action_result['room_output']['room_output_text']}, to=str(character.get_room().room_number), include_self=False
                )
        if action_result['status_output']['status_output_flag'] == True:
            emit('status_update',
                {'data': action_result['status_output']['status_output_text']}
                )
        db.session.commit()
    return


@socketio.event
def connect_room(message):
    character_file = db.session.query(Character).filter_by(first_name=message['first_name'], last_name=message['last_name']).first()
    user_file = db.session.query(User).filter_by(id=character_file.user_id).first()
    user_file.current_sid = request.sid
    character = character_file.char
    if character:
        emit('game_event',
                {'data': "Welcome to Dion. To find out more about available commands, use the HELP command."}
            )
        join_room(str(character.get_room().room_number))
        join_room(str(character.area_name))
        room_file = db.session.query(Room).filter_by(room_number=character.get_room().room_number).first()
        room_file.characters.append(character_file)
        emit('game_event', 
                {'data':  f"{character.first_name} arrived."}, to=str(character.get_room().room_number), include_self=False
            )
        
        action_result = actions.do_action(action_input='look', character_file=character_file, room_file=room_file)

        if not action_result['action_success']:
            emit('game_event',
                {'data': action_result['action_error']}
                )
        else:
            if action_result['display_room']['display_room_flag']:
                emit('game_event',
                    {'data': action_result['display_room']['display_room_text']}
                    )
            if action_result['status_output']['status_output_flag'] == True:
                emit('status_update',
                    {'data': action_result['status_output']['status_output_text']}
                    )
        db.session.commit()
    return


@socketio.event
def disconnect_room(message):
    character_file = db.session.query(Character).filter_by(first_name=message['first_name'], last_name=message['last_name']).first()
    user_file = db.session.query(User).filter_by(id=character_file.user_id).first()
    user_file.current_sid = None
    character = character_file.char
    if character:
        character.leave_room()
        leave_room(str(character.get_room().room_number))
        leave_room(str(character.area_name))
        room_file = db.session.query(Room).filter_by(room_number=character.get_room().room_number).first()
        room_file.characters.remove(character_file)
        emit('game_event', 
                {'data':  "{} left.".format(character.first_name)}, to=str(character.get_room().room_number), include_self=False
            )
        db.session.commit()
    return


@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()
        return
        
    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)
    return


@socketio.on('connect')
def test_connect():
    emit('game_event', {'data': 'You are now connected'})
    print('Client connected', request.sid)
    db.session.query(User)
    return


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)
    return


def enemy_event(action_result, character_file=None):
    if character_file:
        user_file = db.session.query(User).filter_by(id=character_file.user_id).first()
        if action_result['room_output']['room_output_flag'] == True:
            socketio.emit('game_event',
                {'data': action_result['room_output']['room_output_text']}, to=str(action_result['room_output']['room_output_number']), skip_sid=user_file.current_sid)
        if action_result['character_output']['character_output_flag'] == True:
            socketio.emit('game_event',
                {'data': action_result['character_output']['character_output_text']}, to=str(user_file.current_sid))
        if action_result['status_output']['status_output_flag'] == True:
            socketio.emit('status_update',
                {'data': action_result['status_output']['status_output_text']}, to=str(user_file.current_sid)
                )
    if action_result['room_change']['room_change_flag'] == True:
        socketio.emit('game_event',
            {'data': action_result['room_change']['leave_room_text']}, to=str(action_result['room_change']['old_room']))
        socketio.emit('game_event',
            {'data': action_result['room_change']['enter_room_text']}, to=str(action_result['room_change']['new_room']))
    return

def character_announcement(announcement):
    socketio.emit('game_event',
            {'data': announcement}
            )
    return


