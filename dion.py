from app import create_app, socketio, db

app = create_app(debug=True)


if __name__=='__main__':
    socketio.run(app)