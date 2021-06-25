#!/usr/bin/env python
from flask.globals import current_app
import eventlet
from flask import Flask, render_template, redirect, url_for, session, request, copy_current_request_context
from flask_socketio import emit, join_room, leave_room, rooms, disconnect
from flask_login import current_user, login_user, logout_user, login_required

from app import socketio, login, db
from app.main import main, config, player, world, actions
from app.main.models import User, Character, Room
from app.main.forms import LoginForm, SignUpForm, NewCharacterForm

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.

@login.user_loader
def load_user(id):
    return User(id)


@main.route('/')
@login_required
def index():
    return render_template('index.html')


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
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user == None:
            new_user = User(username=form.username.data)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            return '<h1>New user has been created!</h1>'
        return '<h1>User already exists!</h1>'
    return render_template('/signup.html', form=form)


@main.route('/play')
@login_required
def play():
    return render_template('play.html', async_mode=socketio.async_mode)


@main.route('/characters', methods=['POST', 'GET'])
@login_required
def characters():
    
    characters = []
    character_names = []

    user = User.query.filter_by(username=current_user.username).first()

    if user: 
        if user.characters:
            for char in user.characters:
                characters.append(char.char)        
                character_names.append(char.char.first_name + " " + char.char.last_name)

        if request.method == "POST":
            current_character = request.form.get('character')
            current_character_split = current_character.split()
            current_character_firstname = current_character_split[0]
            current_character_lastname = current_character_split[1]
            return render_template('/play.html', 
                    user=current_user.username,
                    character_first_name=current_character_firstname,
                    character_last_name=current_character_lastname)
    
    return render_template('/characters.html', Characters=character_names)


@main.route('/new_character', methods=['POST', 'GET'])
@login_required
def new_character():
    
    message = ""
        
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
        
        for stat in new_character.char.stats:
            new_character.char.stats[stat] = stats_initial[stat]
            
        new_character.char.set_character_attributes()    
        new_character.char.set_gender(new_character.char.gender)
        new_character.char.level_up_skill_points()

        current_user.characters.append(new_character)
        
        db.session.add(new_character)
        db.session.commit()
              
        return '<h1>Character Created! Please close the window and return to the main page.</h1>'
        
    return render_template('/new_character.html', form=form, Stats=stats)



@socketio.event
def my_event(message):
    emit('game_action',
         {'data': message['data']})
    character_file = db.session.query(Character).filter_by(first_name=message['first_name'], last_name=message['last_name']).first()
    if character_file:
        character = character_file.char
        test_result = db.session.query(Room).filter_by(x=character.location_x, 
                                                     y=character.location_y, 
                                                     area_name=character.area_name
                                                     )
        room_file = db.session.query(Room).filter_by(x=character.location_x, 
                                                     y=character.location_y, 
                                                     area_name=character.area_name
                                                     ).first()
        room = room_file.room
    else:
        emit('game_action',
             {'data': message['You have not loaded a character']})
        return

    action_result = actions.do_action(action_input=message['data'], character=character, room=room)

    if not action_result['action_success']:
        emit('game_event',
            {'data': action_result['action_error']})
    else:
        if action_result['room_change']['room_change_flag'] == True:
            room_file.characters.remove(character_file)
            emit('game_event',
                {'data': action_result['room_change']['leave_room_text']}, to=str(action_result['room_change']['old_room']), include_self=False)
            leave_room(room=str(action_result['room_change']['old_room']))
            join_room(room=str(action_result['room_change']['new_room']))
            room_file = db.session.query(Room).filter_by(room_number=action_result['room_change']['new_room']).first()
            room_file.characters.append(character_file)
            emit('game_event',
                {'data': action_result['room_change']['enter_room_text']}, to=str(action_result['room_change']['new_room']), include_self=False)
        if action_result['character_output']['character_output_flag'] == True:
            emit('game_event',
                {'data': action_result['character_output']['character_output_text']})
        if action_result['display_room']['display_room_flag']:
            char_names = []
            for char in room_file.characters:
                if char == character_file:
                    pass
                else:
                    char_names.append(char.first_name)
            if len(char_names) > 0:
                action_result['display_room']['display_room_text'] = action_result['display_room']['display_room_text'] + "Also here:  " + " ".join(char_names)
            emit('game_event',
                {'data': action_result['display_room']['display_room_text']})
        if action_result['room_output']['room_output_flag'] == True:
            emit('game_event',
                {'data': action_result['room_output']['room_output_text']}, to=str(character.get_room().room_number), include_self=False)
        emit('status_update',
            {'data': action_result['status_output']})
    db.session.merge(character_file)
    db.session.merge(room_file)
    db.session.commit()

@socketio.event
def connect_room(message):
    character_file = db.session.query(Character).filter_by(first_name=message['first_name'], last_name=message['last_name']).first()
    character = character_file.char
    if character:
        join_room(str(character.get_room().room_number))
        room_file = db.session.query(Room).filter_by(room_number=character.get_room().room_number).first()
        room_file.characters.append(character_file)
    emit('game_event', 
            {'data':  "{} arrived.".format(character.first_name)}, to=str(character.get_room().room_number), include_self=False
        )
    db.session.merge(character_file)
    db.session.merge(room_file)
    db.session.commit()

@socketio.event
def disconnect_room(message):
    character_file = db.session.query(Character).filter_by(first_name=message['first_name'], last_name=message['last_name']).first()
    character = character_file.char
    if character:
        character.leave_room()
    leave_room(str(character.get_room().room_number))
    room_file = db.session.query(Room).filter_by(room_number=character.get_room().room_number).first()
    room_file.characters.remove(character_file)
    emit('game_event', 
            {'data':  "{} left.".format(character.first_name)}, to=str(character.get_room().room_number), include_self=False
        )
    db.session.merge(character_file)
    db.session.merge(room_file)
    db.session.commit()



@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)

@socketio.on('connect')
def test_connect():
    emit('game_event', {'data': 'You are now connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)

def enemy_spawn(enter_text, room_number):
    socketio.emit('game_event',
        {'data': enter_text}, to=str(room_number))

def enemy_event(action_result):
    if action_result['room_change']['room_change_flag'] == True:
        socketio.emit('game_event',
            {'data': action_result['room_change']['leave_room_text']}, to=str(action_result['room_change']['old_room']))
        socketio.emit('game_event',
            {'data': action_result['room_change']['enter_room_text']}, to=str(action_result['room_change']['new_room']))
    if action_result['character_output']['character_output_flag'] == True:
        socketio.emit('game_event',
            {'data': action_result['character_output']['character_output_text']})
    if action_result['room_output']['room_output_flag'] == True:
        socketio.emit('game_event',
            {'data': action_result['room_output']['room_output_text']}, to=str(action_result['room_output']['room_output_number']))

        # emit('game_event',
        #     {'data':  rooms()})


