from flask import Flask, jsonify
from processing import PacketCapture
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", 
                    async_mode="threading",
                    logger=True,
                    engineio_logger=True,)
capture_job = None

@app.route("/start-sniffing")
def start_sniffing():
    global capture_job
    capture_job = PacketCapture(
        interface=r'\Device\NPF_{157D5AAE-90B3-486A-8885-3EC7BF71F825}',
        socketio=socketio
    )
    socketio.start_background_task(capture_job.run)
    return jsonify({"status": "started"})


@app.route("/stop-sniffing")
def stop_sniffing():
    global capture_job
    if capture_job:
        capture_job.stop()
        return jsonify({"status": "stopped"})
    return jsonify({"error": "no capture running"}), 400

@app.errorhandler(Exception)
def catch_all(e):
    app.logger.exception("Uncaught error in request")
    # always return JSON so the client sees a body
    return jsonify({"error": str(e)}), 500


@socketio.on('connect', namespace='/packets')
def on_connect():
    app.logger.info("Client connected")


@socketio.on('disconnect', namespace='/packets')
def on_disconnect():
    app.logger.info("Client disconnected")
