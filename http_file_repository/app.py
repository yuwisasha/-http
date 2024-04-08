from flask import Flask, request, jsonify, Response, send_file
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from file_repository import FileRepository

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "store"


@app.route("/upload", methods=["POST"])
def upload_file() -> Response:
    repository: FileRepository = FileRepository(app.config["UPLOAD_FOLDER"])  # type: ignore
    file: FileStorage = request.files["file"]
    file_data: bytes = file.read()
    file_hash: str = repository.save(file_data)
    return jsonify({"file_hash": file_hash})


@app.route("/delete", methods=["POST"])
def delete_file() -> Response:
    repository: FileRepository = FileRepository(app.config["UPLOAD_FOLDER"])  # type: ignore
    file_hash: str = request.form["file_hash"]
    repository.delete(filename=file_hash)
    return jsonify({"status": "deleted"})


@app.route("/download/<path:file_hash>", methods=["GET"])
def download_file(file_hash: str):
    repository: FileRepository = FileRepository(app.config["UPLOAD_FOLDER"])  # type: ignore
    secured_file_hash: str = secure_filename(file_hash)
    return send_file(repository.get(secured_file_hash))
