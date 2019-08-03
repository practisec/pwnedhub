from flask import session
from flask_socketio import disconnect, emit
from pwnedhub import socketio, db
from common.models import User, Tool
from common.validators import is_valid_command
from functools import wraps
import os
import subprocess

def login_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not User.query.get(session.get('user_id') or -1):
            disconnect()
        else:
            return func(*args, **kwargs)
    return wrapped

@socketio.on('connect')
def connect_handler():
    if User.query.get(session.get('user_id') or -1):
        emit('status', 'Connected!')
    else:
        return False

@socketio.on('execute')
def command_execution_event_handler(data):
    tool = Tool.query.get(data.get('tid') or -1)
    if not tool:
        cmd = 'invalid'
        output = 'Invalid command.'
    else:
        path = tool.path
        args = data.get('args')
        cmd = ' '.join([x for x in [path, args] if x is not None])
        #[vuln] still vulnerable to command injection
        if not is_valid_command(cmd):
            output = 'Command contains invalid characters.'
        else:
            env = os.environ.copy()
            env['PATH'] = os.pathsep.join(('/usr/bin', env['PATH']))
            p = subprocess.Popen([cmd, args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=env)
            out, err = p.communicate()
            output = (out + err).decode()
    json_result = {'cmd': cmd, 'output': output}
    emit('output', json_result, json=True)

@socketio.on('info')
def tool_info_event_handler(data):
    tid = data.get('tid')
    tool = {}
    if tid:
        #[vuln] still vulnerable to SQL injection
        query = 'SELECT name, path, description FROM tools WHERE id='+tid
        try:
            tool = db.session.execute(query).first() or {}
        except:
            pass
    emit('info', dict(tool), json=True)
