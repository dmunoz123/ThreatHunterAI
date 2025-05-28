import logging
from flask_app import app, socketio


root = logging.getLogger()
root.setLevel(logging.INFO)
file_h = logging.FileHandler("myapp.log", mode="a")
file_h.setLevel(logging.INFO)
file_h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

# # Monkey‑patch its emit method so we always flush
# _orig_emit = file_h.emit

# def emit_and_flush(record):
#     _orig_emit(record)
#     file_h.flush()


# file_h.emit = emit_and_flush

# root.addHandler(file_h)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Started")
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
    logger.info("Finished")
