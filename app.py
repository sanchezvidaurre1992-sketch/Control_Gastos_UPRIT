import csv
import io
import os
import sqlite3
from datetime import date, datetime
from functools import wraps

from flask import (
    Flask, flash, make_response, redirect, render_template,
    request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "instance", "gastos.db"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cambia-esta-clave-secreta-antes-de-publicar")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("COOKIE_SECURE", "0") == "1"


def get_db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                monto REAL NOT NULL CHECK (monto > 0),
                creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_gastos_usuario_fecha
            ON gastos(usuario_id, fecha);
        """)
        # Credenciales iniciales solicitadas para la práctica. Cambiar en producción.
        user = conn.execute("SELECT id FROM usuarios WHERE username = ?", ("admin",)).fetchone()
        if user is None:
            conn.execute(
                "INSERT INTO usuarios (username, password_hash) VALUES (?, ?)",
                ("admin", generate_password_hash(os.environ.get("ADMIN_PASSWORD", "123")))
            )


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Inicia sesión para continuar.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.before_request
def ensure_database():
    if not getattr(app, "_database_ready", False):
        init_db()
        app._database_ready = True


@app.route("/", methods=["GET"])
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_db() as conn:
            user = conn.execute(
                "SELECT id, username, password_hash FROM usuarios WHERE username = ?",
                (username,)
            ).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Bienvenido al control de gastos.", "success")
            return redirect(url_for("dashboard"))
        flash("Usuario o contraseña incorrectos.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    with get_db() as conn:
        gastos = conn.execute(
            """SELECT id, fecha, descripcion, monto
               FROM gastos WHERE usuario_id = ?
               ORDER BY fecha DESC, id DESC LIMIT 8""",
            (session["user_id"],)
        ).fetchall()
        resumen = conn.execute(
            """SELECT COUNT(*) AS cantidad, COALESCE(SUM(monto), 0) AS total
               FROM gastos WHERE usuario_id = ?""",
            (session["user_id"],)
        ).fetchone()
        mes = conn.execute(
            """SELECT COALESCE(SUM(monto), 0) AS total
               FROM gastos WHERE usuario_id = ?
               AND substr(fecha, 1, 7) = ?""",
            (session["user_id"], date.today().strftime("%Y-%m"))
        ).fetchone()
    return render_template("index.html", gastos=gastos, resumen=resumen, total_mes=mes["total"], hoy=date.today().isoformat())


@app.route("/gastos/nuevo", methods=["POST"])
@login_required
def nuevo_gasto():
    fecha = request.form.get("fecha", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    monto_raw = request.form.get("monto", "").strip().replace(",", ".")
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        monto = float(monto_raw)
        if monto <= 0 or monto > 999999999:
            raise ValueError
        if not descripcion or len(descripcion) > 180:
            raise ValueError
    except (ValueError, TypeError):
        flash("Verifica la fecha, descripción y monto. El monto debe ser mayor que cero.", "danger")
        return redirect(url_for("dashboard"))
    with get_db() as conn:
        conn.execute(
            "INSERT INTO gastos (usuario_id, fecha, descripcion, monto) VALUES (?, ?, ?, ?)",
            (session["user_id"], fecha, descripcion, monto)
        )
    flash("Gasto registrado correctamente.", "success")
    return redirect(url_for("dashboard"))


@app.route("/gastos/<int:gasto_id>/eliminar", methods=["POST"])
@login_required
def eliminar_gasto(gasto_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM gastos WHERE id = ? AND usuario_id = ?",
            (gasto_id, session["user_id"])
        )
    flash("Si el gasto existía, fue eliminado.", "info")
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/reportes")
@login_required
def reportes():
    desde = request.args.get("desde", "").strip()
    hasta = request.args.get("hasta", "").strip()
    condiciones = ["usuario_id = ?"]
    params = [session["user_id"]]
    try:
        if desde:
            datetime.strptime(desde, "%Y-%m-%d")
            condiciones.append("fecha >= ?")
            params.append(desde)
        if hasta:
            datetime.strptime(hasta, "%Y-%m-%d")
            condiciones.append("fecha <= ?")
            params.append(hasta)
    except ValueError:
        flash("El rango de fechas no es válido.", "danger")
        return redirect(url_for("reportes"))
    where = " AND ".join(condiciones)
    with get_db() as conn:
        gastos = conn.execute(
            f"SELECT id, fecha, descripcion, monto FROM gastos WHERE {where} ORDER BY fecha DESC, id DESC",
            params
        ).fetchall()
        resumen = conn.execute(
            f"SELECT COUNT(*) AS cantidad, COALESCE(SUM(monto), 0) AS total FROM gastos WHERE {where}",
            params
        ).fetchone()
    return render_template("reportes.html", gastos=gastos, resumen=resumen, desde=desde, hasta=hasta)


@app.route("/reportes/exportar")
@login_required
def exportar_csv():
    desde = request.args.get("desde", "").strip()
    hasta = request.args.get("hasta", "").strip()
    condiciones = ["usuario_id = ?"]
    params = [session["user_id"]]
    try:
        if desde:
            datetime.strptime(desde, "%Y-%m-%d")
            condiciones.append("fecha >= ?")
            params.append(desde)
        if hasta:
            datetime.strptime(hasta, "%Y-%m-%d")
            condiciones.append("fecha <= ?")
            params.append(hasta)
    except ValueError:
        flash("El rango de fechas no es válido.", "danger")
        return redirect(url_for("reportes"))
    with get_db() as conn:
        rows = conn.execute(
            "SELECT fecha, descripcion, monto FROM gastos WHERE "
            + " AND ".join(condiciones) + " ORDER BY fecha DESC", params
        ).fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fecha", "Descripcion", "Monto (S/)"])
    for row in rows:
        writer.writerow([row["fecha"], row["descripcion"], f'{row["monto"]:.2f}'])
    response = make_response("\ufeff" + output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = "attachment; filename=reporte_gastos.csv"
    return response


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_DEBUG") == "1")
