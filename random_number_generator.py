from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context
from random import random
from time import sleep
from threading import Thread, Event

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

socketio = SocketIO(app)

thread = Thread()
thread_stop_event = Event()


class RandomThread(Thread):
    def __init__(self):
        self.delay = 1
        super(RandomThread, self).__init__()

    def random_number_generator(self):
        while not thread_stop_event.isSet():
            number = round(random() * 10, 3)
            socketio.emit('new_number', {'number': number}, namespace='/test')
            sleep(self.delay)

    def run(self):
        self.random_number_generator()


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    print('Client Connected')

    if not thread.isAlive():
        thread = RandomThread()
        thread.start()


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
