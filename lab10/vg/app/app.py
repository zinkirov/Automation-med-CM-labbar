import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import os
from urllib.parse import urlparse
from flask import Flask, jsonify, render_template, request
import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.get("/")
def dashboard():
    return render_template("index.html")

def database_connection():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        user="monitor_app",
        password=os.environ["DB_PASSWORD"],
        database="service_monitor",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
    )


@app.get("/api/services")
def list_services():
    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, url FROM services ORDER BY id")
            services = cursor.fetchall()
        return jsonify(services)
    finally:
        connection.close()


@app.post("/api/services")
def create_service():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Skicka JSON med name och url"}), 400

    name = data.get("name")
    url = data.get("url")

    if not isinstance(name, str) or not name.strip() or len(name) > 100:
        return jsonify({"error": "name måste vara 1–100 tecken"}), 400

    if not isinstance(url, str) or len(url) > 255:
        return jsonify({"error": "url måste vara en giltig HTTP-adress"}), 400

    parsed_url = urlparse(url)
    if parsed_url.scheme not in ("http", "https") or not parsed_url.hostname:
        return jsonify({"error": "url måste börja med http:// eller https://"}), 400

    name = name.strip()
    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO services (name, url) VALUES (%s, %s)",
                (name, url),
            )
            service_id = cursor.lastrowid
        connection.commit()
        return jsonify({"id": service_id, "name": name, "url": url}), 201
    finally:
        connection.close()

@app.post("/api/services/<int:service_id>/check")
def check_service(service_id):
    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT url FROM services WHERE id = %s",
                (service_id,),
            )
            service = cursor.fetchone()
    finally:
        connection.close()

    if service is None:
        return jsonify({"error": "Tjänsten finns inte"}), 404

    status_code = None
    error_message = None
    started = time.perf_counter()

    try:
        http_request = Request(
            service["url"],
            headers={"User-Agent": "ServiceMonitor/1.0"},
        )
        with urlopen(http_request, timeout=5) as response:
            status_code = response.status
    except HTTPError as error:
        status_code = error.code
        error_message = f"HTTP {error.code}"
    except (URLError, TimeoutError, OSError) as error:
        error_message = str(error)[:255]

    response_ms = round((time.perf_counter() - started) * 1000)
    is_up = status_code is not None and 200 <= status_code < 400

    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO checks
                    (service_id, is_up, status_code, response_ms, error_message)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (service_id, is_up, status_code, response_ms, error_message),
            )
            check_id = cursor.lastrowid
        connection.commit()
    finally:
        connection.close()

    return jsonify({
        "id": check_id,
        "service_id": service_id,
        "is_up": is_up,
        "status_code": status_code,
        "response_ms": response_ms,
        "error_message": error_message,
    })


@app.get("/api/services/<int:service_id>/checks")
def list_checks(service_id):
    connection = database_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, service_id, checked_at, is_up,
                       status_code, response_ms, error_message
                FROM checks
                WHERE service_id = %s
                ORDER BY checked_at DESC, id DESC
                LIMIT 20
                """,
                (service_id,),
            )
            checks = cursor.fetchall()
    finally:
        connection.close()

    for check in checks:
        check["is_up"] = bool(check["is_up"])
        check["checked_at"] = check["checked_at"].isoformat()

    return jsonify(checks)        
