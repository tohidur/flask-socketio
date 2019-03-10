import eventlet
eventlet.monkey_patch()

import json
from flask import Flask
from flask import request
from flask_socketio import SocketIO, send, emit, join_room, leave_room, \
    Namespace, rooms

DEBUG = True

app = Flask(__name__)
app.config['SECRET_KEYA'] = 'secret!'
socketio = SocketIO(app, debug=DEBUG, async_mode='eventlet')


# Receiving message
# =================
@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)
    send(message)


# Custom Events. Custom events supports multiple arguments also.
@socketio.on('my event')
def handle_my_custom_event(data):
    print("received args: " + json.dumps(data))
    _d = {}
    send(_d, json=True)

    # To send ack to the client, Client callback function will be invoked
    # with these arguments
    return 'one', 2


# Namespace
@socketio.on('my event namespace', namespace='/test')
def handle_my_custom_namespace_event(json):
    print("received json: " + str(json))
    emit('my response', json)

    # Sending multiple arguments
    emit('my response', 'foo', namespace='/test')


# Without decorator
def my_function_handler(data):
    print("received my function handler: " + str(data))


socketio.on_event(
    "my function handler event",
    my_function_handler,
    namespace='/'
)


# Sending Message
# ===============
# With callback
def ack():
    print 'callback message was received'


@socketio.on('my event ack')
def handle_my_event_ack(json):
    emit('my response', json, callback=ack)


# Broadcasting
# ============
# Use broadcast=True argument to broadcast
# NOTE: the callbacks are not invoked for broadcast message.
@socketio.on('my event broadcast')
def handle_my_event_broadcast(data):
    emit(
        'my response', {"msg": "Its a broadcast"},
        broadcast=True, namespace='/'
    )
    send_message_without_client_context()


# Above all example the emit from server was in client context.
# If its not then broadcast=True will be assumed and does not need to be
# Specified.
def send_message_without_client_context():
    socketio.emit(
        'my response',
        {'data': 'without client context is actually a broadcast'}
    )


# Rooms
# =====
"""
For many applications it is necessary to group users into subsets that can be
address together.
Flask-SocketIO supports this concept of rooms through the join_room() and
leave_room() functions.
"""


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    print('joined room: ')
    print(rooms())
    emit('my response', username + ' has entered the room.', room=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('my response', username + ' has left the room.', room=room)


"""
All clients are assigned a room when they connect, named with the session ID of
the connection. Which can be obtained from request.sid. When a client
disconnects it is removed from all the room it was in. The context-free
socketio.send and socketio.emit also accepts room argument.
"""

# Connection Events
# =================
"""
Flask-SocketIO also dispatches connection and disconnection events. The
following example shows how to register handler for them.
"""


@socketio.on('connect', namespace='/chat')
def test_connect():
    print('connected')
    emit('my response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
    print('Client Disconnected')


"""
The connection event handler can optionally return False to reject the
connection. This is so that the client can be authenticated at this point.
"""


# Class Based Namespace
# =====================
# Decorator based namespace has higher preference than classed based, if
# there is a conflict in event name.
class MyCustomNamespace(Namespace):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_my_event(self, data):
        emit('my response', data)


socketio.on_namespace(MyCustomNamespace('/test2'))


# Error Handling
# ==============
@socketio.on_error()    # Handles default namespace.
def error_handler(e):
    pass


@socketio.on_error('/chat')     # Handles chat namespace.
def error_handler_chat(e):
    pass


@socketio.on_error_default    # Handles all namespaces without an explicit one
def default_error_handler(e):
    pass


# On error the message data arguments of the current request can also be
# inspected with the request.event variable.


@socketio.on('my error event')
def on_my_error_event(data):
    raise RuntimeError()


@socketio.on_error_default
def default_error_handler(e):
    print(request.event['message'])     # "my error event"
    print(request.event['args'])


# Authentication
# ==============
"""
After a regular Flask-Login authentication is performed and the login_user()
function is called to record the user in the user session, any SocketIO
connections will have access to the current_user context variable.

login_required decorator cannot be used with SocketIO event handlers.
Custom decorator can be created as follows.
"""

import functools
from flask import request
from flask_login import current_user
from flask_socketio import disconnect


@socketio.on('_connect')
def connect_handler():
    if current_user.is_authenticated:
        emit("my response",
             {'message': '{0} has joined'.format(current_user.name)},
             broadcast=True)
    else:
        return False


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@socketio.on('my event authenticated')
@authenticated_only
def handle_my_custom_event(data):
    emit('my response', {'message': '{0} has joined'.format(current_user.name)},
         broadcast=True)


# Deployments
# =============
"""
Best performant option is to use eventlet worker with gevent

gunicorn --worker-class eventlet -w 1 module:app

Alternative is gevent. gevent works pefectly well with long polling.
With websocket we need to use GeventWebSocketWorker

gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 module:app 
"""


# Using nginx as a WebSocket Reverse Proxy
# ========================================
"""
It is possible to use nginx as a frontend reverse proxy that passes request
to application. However, only releases of nginx 1.4 and newer support proxying
of the WebSocket protocol. Below is a basic nginx configuration that proxies
HTTP and websocket request.

Check nginx configuration files - ws.nginx and ws.loadbalance.nginx
"""


# Serve Demo client page
@app.route('/test_client')
def test_client():
    return """
        <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.6/socket.io.min.js"></script>
        <script type="text/javascript" charset="utf-8">
            var socket = io.connect('http://' + document.domain + ':' + location.port);
            socket.on('connect', function() {
                console.log('Connected');

                socket.on('my response', function(data, callback) {
                    console.log('got response: ' + JSON.stringify(data));
                    if (callback !== undefined) {
                        callback();
                    };
                });

                console.log("Emitting my event");
                socket.emit(
                    'my event', {'data': 'Im connected!'},
                    function(a, b){
                        console.log('got response: ' + a);  // Will print one
                        console.log('got response: ' + b);  // Will print 1
                    }
                );

                console.log("Sending function handler event");
                socket.emit('my function handler event', {});

                console.log("Sending Event to get a ack");
                socket.emit("my event ack", {"data": "json"});

                console.log('To get a broadcast');
                socket.emit("my event broadcast", {});

                console.log('joining room');
                socket.emit('join', {'username': 'tohi', 'room': 'tohi_room'});
                socket.emit('join', {'username': 'tohi2', 'room': 'tohi_room2'});

                console.log('leaving room');
                socket.emit('leave', {'username': 'tohi2', 'room': 'tohi_room2'});

            });


            var ns_socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
            ns_socket.on('connect', function() {
                console.log("Namespaced socket connected");
                ns_socket.emit('my event namespace', {'data': 'Namespaced event'});

                ns_socket.on('my response', function(data) {
                    console.log('Namespaced got response: ' + data);
                });
            });

        </script>
    """


if __name__ == '__main__':
    socketio.run(app, debug=DEBUG)
