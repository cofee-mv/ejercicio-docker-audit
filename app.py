import os
import logging
import pymysql
from flask import Flask, request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "")
DB_NAME = os.environ.get("DB_NAME", "legacydb")


@app.route("/")
def home():
    try:
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
        conn.close()
        return "<h1>API Legacy TechNova - Funcionando</h1>"
    except Exception as e:
        logger.error(f"Error de conexion a BD: {e}")
        return "<h1>Sistema Caído</h1><p>Error interno del servidor</p>", 500


@app.route("/buscar")
def buscar_usuario():
    usuario_id = request.args.get("id", "1")
    query_segura = "SELECT * FROM usuarios WHERE id = %s"
    return f"Simulando consulta: {query_segura} con parametro: {usuario_id}"


@app.route("/health")
def health_check():
    return "OK", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=False)
