### Install
pip install flask-socketio==3.3.1

### Requirements
eventlet and gevent is most performant option with websocket.
gevent needs one of gevent-websocket and uWSGI to support websocket. For gevent uWSGI is preferred.


If using multi processes, a message queue service is used by the processes to coordinate operations.
Supported queues are Redis and RabbitMQ.

Client side SocketIO javascript library can be used.


##### Run flask App
FLASK_APP=demo.py flask run


##### Receiving/Sending message
# Namespaces
It allows client to multiple several independent connections on the same physical socket.
No no namespace is specified a global namespace '/' is used.

##### Sending Message
When working in namespace pass namespace kwarg
`send(message, namespace='/chat')`
`emit('my response', json, namespace='/demo')`

##### Send a event with multiple arguments
`emit('my response', ('foo', 'bar', 'baz'), namespace='/demo')`


### Deployments
Best performant option is to use `eventlet` worker with `gevent`.

`gunicorn --worker-class eventlet -w 1 module:app`

Alternative is `gevent`. `gevent` works pefectly well with long polling.
With websocket we need to use `GeventWebSocketWorker`.

`gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 module:app`


### Using nginx as a WebSocket Reverse Proxy
It is possible to use nginx as a frontend reverse proxy that passes request
to application. However, only releases of nginx 1.4 and newer support proxying
of the WebSocket protocol. Below is a basic nginx configuration that proxies
HTTP and websocket request.

Check nginx configuration files - `ws.nginx` and `ws.loadbalance.nginx`


### Multiple workers and communicating with a external process.
Check `demo_multiple_workers.py`


### NOTE
If message queue is used (or other python library if its usages coroutine framework) then it needs to be monkey
patched

It is important to note that an external process that wants to connect to a SocketIO server
does not need to use eventlet or gevent like the main server. Having a server use a coroutine framework,
while an external process is not a problem. For example, Celery workers do not need
to be configured to use eventlet or gevent just because the main server does.
But if your external process does use a coroutine framework for whatever reason,
then monkey patching is likely required, so that the message queue accesses coroutine friendly functions and classes.


### API References
1. SocketIO
    * logger - True or logger object. default to False.
    * async_mode - The asynchronous module to use.
    * ping_timeout
    * ping_interval
    * engineio_logger - To enable EngineIO logging.

2. close_room
    This can be used from outside of SocketIO event context.

3. run
    * app
    * host
    * port
    * debug
    * use_reloader
    * log_output - default False in normal mode and True in debug mode. Unused when threading async mode is used.

4. start_background_task(target, *args, **kwargs)
    Starts a background

5. Sleep
