from celery import Celery
import time
from flask_socketio import SocketIO

celery = Celery('demo', broker='amqp://')
"""
Configuration
add user
sudo rabbitmqctl add_user demo_user demo_user
sudo rabbitmqctl add_vhost demo_host
sudo rabbitmqctl rabbitmqctl set_permissions -p demo_host demo_user ".*" ".*" ".*"

Run the workers
celery -A tasks worker -loglevel=info -concurrency=4
"""

BROKER_URL = "amqp://up_stl:up_stl@localhost:5672/up_stl_host"
socketio = SocketIO(message_queue=BROKER_URL)


def send_message(event, namespace, room, message):
    socketio.emit(event, {'msg': message}, namespace=namespace, room=room)


@celery.task
def long_task(n, session):
    room = session
    namespace = '/long_task'

    send_message('status', namespace, room, 'Begin')
    send_message('msg', namespace, room, 'Begin Task {}'.format(long_task.request.id))
    send_message('msg', namespace, room, 'This will take {} seconds'.format(n))

    for i in range(n):
        print i
        time.sleep(1)

    send_message('msg', namespace, room, 'End Task {}'.format(long_task.request.id))
    send_message('status', namespace, room, 'End')
