#!/usr/bin/env python
import eventlet
from flask import Flask, render_template, redirect, url_for, session, request, copy_current_request_context
from flask_socketio import emit, join_room, leave_room, close_room, rooms, disconnect
from flask_login import UserMixin, current_user, login_user, logout_user, login_required

from app import socketio, login, db
from app.main import main, config, player, world, actions
from app.main.models import User, Character, Room
from app.main.forms import LoginForm, SignUpForm, NewCharacterForm

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('game_event',
                      {'data': 'Server generated event', 'count': count})

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
        for character in characters:
            character_names.append(character.first_name + " " + character.last_name)

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
        new_character.char.room = world.tile_exists(x=new_character.char.location_x, y=new_character.char.location_y, area=new_character.char.area)

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
    character = character_file.char
    if character:
        character.room = world.tile_exists(x=character.location_x, y=character.location_y, area=character.area)
        if not character.room.room_filled:
            character.room.fill_room(character=character)
    room_file = db.session.query(Room).filter_by(room_number=character.room.room_number).first()
    action_result = actions.do_action(action_input=message['data'], character=character)

    if not action_result['action_success']:
        emit('game_event',
            {'data': action_result['action_error']})
    else:
        if action_result['room_change']['room_change_flag'] == True:
            emit('game_event',
                {'data': action_result['room_change']['leave_room_text']}, to=str(action_result['room_change']['old_room']), include_self=False)
            leave_room(str(action_result['room_change']['old_room']))
            join_room(str(action_result['room_change']['new_room']))
            room_file = db.session.query(Room).filter_by(room_number=action_result['room_change']['new_room']).first()
            room_file.characters.append(character_file)
            emit('game_event',
                {'data': action_result['room_change']['enter_room_text']}, to=str(action_result['room_change']['new_room']), include_self=False)
        if action_result['character_output']['character_output_flag'] == True:
            emit('game_event',
                {'data': action_result['character_output']['character_output_text']})
        if action_result['display_room_flag']:
            intro_text = character.room.intro_text()
            char_names = []
            for char in room_file.characters:
                char_names.append(char.first_name)
            char_names.remove(character.first_name)
            if len(char_names) > 0:
                intro_text = intro_text + "<br>" + "Also here:  " + " ".join(char_names)
            emit('game_event',
                {'data': intro_text})
        if action_result['room_output']['room_output_flag'] == True:
            emit('game_event',
                {'data': action_result['room_output']['room_output_text']}, to=str(character.room.room_number), include_self=False)
        emit('status_update',
            {'data': action_result['status_output']})

        emit('game_event',
            {'data':  rooms()})

    character_file.char = character

    db.session.commit()

@socketio.event
def my_broadcast_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.event
def join(message):
    join_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.event
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close_room')
def on_close_room(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         to=message['room'])
    close_room(message['room'])


@socketio.event
def my_room_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         to=message['room'])


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


@socketio.event
def my_ping():
    emit('my_pong')


@socketio.on('connect')
def test_connect():
    # thread = eventlet.spawn(background_thread)
    emit('game_event', {'data': 'You are now connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)


