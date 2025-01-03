from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
# Bruker du Mariadb så bytter du ut mysql med mariadb. Mariadb må installeres med (pip install mariadb) Koden finner du på neste linje.
# import mariadb

app = Flask(__name__)
app.secret_key = "dinhemmelignøkkel"


# bruker du Mariadb så bytter du ut mysql med mariadb. connect
# return mariadb.connect(
# Husk å endre host, user, password og database, slik at de er tilpasset dine instillinger
# Database-tilkobling
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="userdb"
    )
@app.route("/registrer", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        brukernavn = request.form['brukernavn']
        epost = request.form['epost']
        passord = generate_password_hash(request.form['passord'])

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (brukernavn, epost, passord_hash) VALUES (%s, %s, %s)", 
                       (brukernavn, epost, passord))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Bruker registrert!", "success")
        return redirect(url_for("login"))

    return render_template("registrer.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        brukernavn = request.form['brukernavn']
        passord = request.form['passord']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE brukernavn=%s", (brukernavn,))
        bruker = cursor.fetchone()
        cursor.close()
        conn.close()

        if bruker and check_password_hash(bruker['passord_hash'], passord):
            session['brukernavn'] = bruker['brukernavn']
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", feil_melding="Ugyldig brukernavn eller passord")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "brukernavn" in session:
        return render_template("dashboard.html", brukernavn=session['brukernavn'])
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("brukernavn", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
