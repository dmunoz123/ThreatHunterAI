import logging
from flask_app import app, socketio


root = logging.getLogger()
# Set the default logging level for the root logger
root.setLevel(logging.INFO)
# Create a FileHandler to write log messages to a file
file_h = logging.FileHandler("myapp.log", mode="a")
file_h.setLevel(logging.INFO)
# log timestamp, logging level, log record name, and log message
formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
file_h.setFormatter(formatter)
root.addHandler(file_h)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Started")
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
    logger.info("Finished")
