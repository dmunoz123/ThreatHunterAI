from flask import Flask, jsonify
from processing import PacketCapture
from flask_socketio import SocketIO
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
# from autogluon.tabular import TabularPredictor
from aws_utils import load_csv_from_s3
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading",
                    logger=True,
                    engineio_logger=True,)


# PREDICTOR_DIR = r"..\\ag-20250412_023747"
# predictor_main = TabularPredictor.load(
#     PREDICTOR_DIR, require_version_match=False,
#     require_py_version_match=False)

capture_job = None


# def _init_worker():
#     global predictor
#     predictor = TabularPredictor.load(
#         r"..\\ag-20250412_023747", require_version_match=False, require_py_version_match=False)


# def _predict_worker(x_pred):
#     # `predictor` is the one loaded in this process
#     return predictor.predict(x_pred).tolist()


# def _proba_worker(x_pred):
#     # 1) ask AutoGluon for the full Nx2 array/DataFrame
#     probs = predictor.predict_proba(x_pred)

#     # 2) if it came back as a DataFrame, grab its underlying numpy array
#     arr = probs.values if isinstance(probs, pd.DataFrame) else probs

#     # 3) return just the “bad” class (column index 1) as a Python list
#     return arr[:, 1].tolist()

# executor = ProcessPoolExecutor(
#     max_workers=2,
#     initializer=_init_worker,
# )

@app.route("/start-sniffing")
def start_sniffing():
    global capture_job
    capture_job = PacketCapture(
        interface=r'wlp0s20f3',
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

# @app.route("/run-predictions", methods=["GET"])
# def run_predictions():
#     bucket = "daniel-aws-s3-mks-myawstestbucket"
#     prefix = "success_packet_capture_"
#     s3 = boto3.client("s3")

#     app.logger.info("Entered run_predictions")
#     try:
#         # 1) list S3
#         resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
#         contents = resp.get("Contents", [])
#         app.logger.info("S3 objects listed: %d items", len(contents))
#         if not contents:
#             return jsonify({"error": "No capture data"}), 404

#         # 2) pick latest
#         latest_obj = max(contents, key=lambda obj: obj["LastModified"])
#         key = latest_obj["Key"]
#         app.logger.info("Latest S3 key: %s", key)

#         # 3) load CSV
#         df = load_csv_from_s3(bucket, key)
#         app.logger.info("Loaded CSV with shape %s", df.shape)

#         # 4) sample & prepare
#         sample = df.sample(n=1000) if len(df) >= 1000 else df
#         X = sample.drop(columns=["bad_packet"], errors="ignore")
#         app.logger.info("Sample size: %d rows", len(X))

#         # 5) predict via worker
#         app.logger.info("Submitting X to process pool for prediction")
#         start = time.time()
#         future = executor.submit(_predict_worker, X)
#         preds = future.result()
#         duration = time.time() - start
#         app.logger.info("ProcessPool predict took %.2fs", duration)


#         return jsonify({
#             "file_key": key,
#             "predictions": preds,
#             "model_info": {
#                 "eval_metric": str(predictor_main.eval_metric),
#                 "model_path": predictor_main.path,
#             }
#         })

#     except Exception:
#         app.logger.exception("Error in run_predictions")
#         return jsonify({"error": "Internal server error"}), 500



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
