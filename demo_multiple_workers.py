import eventlet
eventlet.monkey_patch()

import json
from flask import Flask
from flask_socketio import SocketIO, emit

DEBUG = True

app = Flask(__name__)
app.config['SECRET_KEYA'] = 'secret!'
socketio = SocketIO(app, debug=DEBUG, async_mode='eventlet')


# Multiple Workers
# ================
"""
Two requirements for multiple workers.

1. The load balancer must be configured to forward all HTTP requests from a
given client always to the same worker. This is sometimes referred as
"sticky sessions". For nginx, use `ip_hash` directive to achieve this.

Gunicorn can not be used with multiple workers because its load balancer
algorithm does not support sticky session.

2. Since each of the servers ows only a subset of client connections,
a message queue such as Redis or RabbitMQ is used by the servers to
co-ordinate complex operations such as broadcasting and rooms.

3. When working with message queue there are additional needs to be installed.
For Redis (pip install redis). RabbitMQ (pip install kombu)

4. If eventlet or gevent are used, then monkey patching the Python standard
library is normally required to force the message queue package to use
co-routines friendly and classes.
"""


# Emitting from an External Process
# =================================
"""
Sometimes, It is necessary to emit event from a process that is not socket
server, for an example socket server.

socketio = SocketIO(message_queue='redis://')
socketio.emit('my event', {'data': 'foo'}, namespace='/test')

When using SocketIO instance in this way. The Flask application instance is
not passed to the constructor.

The channel argument to SocketIO can be used to select a specific channel of
communication through the message queue. Using a custom channel name is
necessary when there are multiple independent SocketIO services sharing the
same queue.
"""


if __name__ == '__main__':
    socketio.run(app, debug=DEBUG)
