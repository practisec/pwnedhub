from flask import request, current_app, session
from flask_socketio import emit, join_room, leave_room, rooms as joined_rooms
from pwnedapi.models import Config, User, Message, Room
from pwnedapi.utils import decode_jwt
from pwnedapi import socketio, db
from werkzeug.exceptions import Forbidden
import hashlib
import traceback

# global store for all websocket client sids (rooms names)
clients = {}

def create_room_name(member_ids):
    # sort ids to make the name consistent regardless of how the ids are provided
    member_ids.sort()
    # create seed date for the hash
    seed = ':'.join([str(i) for i in member_ids])
    # create the hash digest
    digest =  hashlib.sha1(seed.encode()).hexdigest()
    # return an abbreviated value
    return digest[:8]

def parse_jwt():
    request.jwt = {}
    token = request.cookies.get('access_token')
    if Config.get_value('BEARER_AUTH_ENABLE'):
        token = request.args.get('access_token')
    try:
        payload = decode_jwt(token)
    except:
        return
    request.jwt = payload

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
    # add client sid to global store
    clients[session.user.id] = request.sid
    emit('log', f"Socket connected.")
    # preload users
    users = [u.serialize() for u in User.query.all()]
    emit('loadUsers', {'users': users})
    # preload rooms
    rooms = [r.serialize(session.user) for r in session.user.rooms.all()]
    emit('loadRooms', {'rooms': rooms})
    # load the default room
    default_room = rooms[0]
    emit('loadRoom', default_room)

@socketio.on('disconnect')
def disconnect_handler():
    # remove client sid from global store
    del clients[session.user.id]

@socketio.on('create-room')
def create_room_handler(data):
    # needed to re-establish session.user after commit
    current_user_id = session.user.id
    name = create_room_name(data['member_ids'])
    room = Room.get_by_name(name)
    if not room:
        # create the room
        room = Room(
            name=name,
            private=data['private'],
        )
        db.session.add(room)
        db.session.commit()
        emit('log', f"Created room: id={room.id}, name={room.name}")
        session.user = User.query.get(current_user_id)
        # initialize memberships
        for member_id in data['member_ids']:
            user = User.query.get(member_id)
            user.create_membership(room)
        # reload rooms
        # must create both memberships before reloading either member
        for member_id in data['member_ids']:
            user = User.query.get(member_id)
            if user.id in clients:
                rooms = [r.serialize(user) for r in user.rooms.all()]
                emit('loadRooms', {'rooms': rooms}, room=clients[user.id])
    # load the room
    emit('loadRoom', room.serialize(session.user))

@socketio.on('join-room')
def join_room_handler(data):
    room = Room.query.get(data['id'])
    if room.name not in joined_rooms():
        join_room(room.name)
    # send a message to the joined room with admin bot
    # if the room is private and the user is not a member
    if room.private:
        members = room.members.all()
        if session.user.id not in [m.id for m in members]:
            sender = members[0]
            receiver = members[1]
            if sender and receiver:
                current_app.bot_task_queue.enqueue(
                    'adminbot.tasks.test_login_send_private_message',
                    kwargs={
                        'name': sender.name,
                        'email': sender.email,
                        'room_id': room.id,
                        'message': 'Do you ever get the feeling that someone is reading our private messages?'
                    }
                )
    emit('log', f"Joined room: id={data['id']}, name={data['name']}")

# unused
@socketio.on('leave-room')
def leave_room_handler(data):
    leave_room(data['name'])
    emit('log', f"Left room: {data['id']}")

@socketio.on('create-message')
def create_message_handler(data):
    message = Message(
        comment=data['message']['comment'],
        author=session.user,
        room_id=data['room']['id']
    )
    db.session.add(message)
    db.session.commit()
    emit('newMessage', message.serialize(), room=data['room']['name'])

@socketio.on('delete-message')
def delete_message_handler(data):
    message = Message.query.get(data['message']['id'])
    if message.author.id != session.user.id and session.user.is_admin == False:
        raise Forbidden('Unauthorized deletion attempt.')
    # create response object before deleting it
    serialized_message = message.serialize()
    db.session.delete(message)
    db.session.commit()
    emit('delMessage', serialized_message, room=data['room']['name'])

@socketio.on_error_default
def default_error_handler(e):
    emit('log', request.event)
    print(traceback.format_exc())
