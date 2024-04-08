from flask import Flask, request, jsonify, Response, send_file
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth

from file_repository import FileRepository

app = Flask(__name__)
auth = HTTPBasicAuth()

app.config["UPLOAD_FOLDER"] = "store"

users = {
    "alexandr": generate_password_hash("123"),
    "julia": generate_password_hash("321")
}


@auth.verify_password  # type: ignore
def verify_password(username: str, password: str) -> str | None:
    if username in users and \
            check_password_hash(users.get(username), password):  # type: ignore
        return username


@app.route("/upload", methods=["POST"])
@auth.login_required  # type: ignore
def upload_file() -> Response:
    repository: FileRepository = FileRepository(app.config["UPLOAD_FOLDER"])  # type: ignore
    file: FileStorage = request.files["file"]
    file_hash: str = repository.save(auth.current_user(), file)
    return jsonify({"file_hash": file_hash})


@app.route("/delete", methods=["POST"])
@auth.login_required  # type: ignore
def delete_file() -> Response:
    repository: FileRepository = FileRepository(app.config["UPLOAD_FOLDER"])  # type: ignore
    file_hash: str = request.form["file_hash"]
    repository.delete(username=auth.current_user(), filename=secure_filename(file_hash))
    return jsonify({"status": "deleted"})


@app.route("/download/<path:file_hash>", methods=["GET"])
def download_file(file_hash: str):
    repository: FileRepository = FileRepository(app.config["UPLOAD_FOLDER"])  # type: ignore
    secured_file_hash: str = secure_filename(file_hash)
    return send_file(repository.get(secured_file_hash))
