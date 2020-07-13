from flask import request, session
from flask_socketio import emit, join_room, leave_room
from common.models import User, Message
from pwnedapi import socketio, db
from pwnedapi.views.api import parse_jwt
from werkzeug.exceptions import Forbidden
import traceback

def load_user():
    # g doesn't persist across events, so session is used to track the authenticated user
    # since websockets don't use session, using it should be transparent to the client
    # for some reason session.user does not equate to <object>.user, so the id property
    # must be used to make equality comparisons
    session.user = None
    uid = request.jwt.get('sub')
    if uid:
        session.user = User.query.get(uid)

@socketio.on('connect')
def connect_handler():
    parse_jwt()
    load_user()
    if not session.user:
        return False
    emit('newConnection', f"Socket connected.")

@socketio.on('join-room')
def join_room_handler(data={}):
    room = data.get('room', 'general')
    join_room(room)
    session['room'] = room
    emit('log', f"Joined room: #{room}.")

# not used yet
@socketio.on('leave-room')
def leave_room_handler():
    room = session.get('room')
    leave_room(room)
    session.room = None
    emit('log', f"Left room: #{room}.")

@socketio.on('create-message')
def create_message_handler(data):
    comment = data.get('message')
    message = Message(comment=comment, author=session.user)
    db.session.add(message)
    db.session.commit()
    room = session.get('room')
    emit('newMessage', message.serialize(), room=room)

@socketio.on('delete-message')
def delete_message_handler(data):
    mid = data.get('id')
    message = Message.query.get(mid)
    if message.author.id != session.user.id and session.user.is_admin == False:
        raise Forbidden('Unauthorized deletion attempt.')
    db.session.delete(message)
    db.session.commit()
    room = session.get('room')
    emit('delMessage', mid, room=room)

@socketio.on_error_default
def default_error_handler(e):
    #print(request.event["message"]) # "my error event"
    #print(request.event["args"])    # (data,)
    print(traceback.format_exc())
