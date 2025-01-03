from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
# Bruker du Mariadb så bytter du ut mysql med mariadb. Mariadb må installeres med (pip install mariadb) Koden finner du på neste linje.
# import mariadb


app = Flask(__name__)
app.secret_key = "dinhemmelignøkkel"

# Database-tilkobling
# bruker du Mariadb så bytter du ut mysql med mariadb. connect
# return mariadb.connect(
# Husk å endre host, user, password og database, slik at de er tilpasset dine instillinger 
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="userdb"
    )

# Rute for registrering
@app.route("/registrer", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        brukernavn = request.form['brukernavn']
        epost = request.form['epost']
        passord = generate_password_hash(request.form['passord'])

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (brukernavn, epost, passord_hash, rolle) VALUES (%s, %s, %s, %s)", 
                       (brukernavn, epost, passord, 'bruker'))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Bruker registrert!", "success")
        return redirect(url_for("login"))

    return render_template("registrer.html")

# Rute for login
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
            session['rolle'] = bruker['rolle']

            if bruker['rolle'] == 'admin':
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("user_dashboard"))
        else:
            return render_template("login.html", feil_melding="Ugyldig brukernavn eller passord")

    return render_template("login.html")

# Admin dashboard
@app.route("/admin")
def admin_dashboard():
    if session.get("rolle") == "admin":
        return render_template("admin_dashboard.html", brukernavn=session['brukernavn'])
    return redirect(url_for("login"))

# User dashboard
@app.route("/user")
def user_dashboard():
    if session.get("rolle") == "bruker":
        return render_template("user_dashboard.html", brukernavn=session['brukernavn'])
    return redirect(url_for("login"))

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Du har logget ut.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
