from flask import Flask, render_template, request, redirect, session, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "mcps-boxlight-secret"

PORTAL_PASSWORD = "MCPS1234!"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "mcps_portal_data.json")


def load_units():
    try:
        if not os.path.exists(DATA_FILE):
            print(f"DATA FILE NOT FOUND: {DATA_FILE}")
            return []

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("JSON data is not a list.")
            return []

        return data

    except Exception as exc:
        print(f"ERROR LOADING UNITS: {exc}")
        return []


def get_unit_by_id(unit_id):
    units = load_units()

    for unit in units:
        try:
            if int(unit.get("id", 0)) == int(unit_id):
                return unit
        except Exception:
            continue

    return None


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "")

        if password == PORTAL_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("portal"))

        return render_template("login.html", error="Invalid password")

    return render_template("login.html")


@app.route("/portal")
def portal():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip().lower()
    units = load_units()

    if search:
        filtered = []

        for unit in units:
            combined = " ".join([
                str(unit.get("intake_id", "")),
                str(unit.get("serial_number", "")),
                str(unit.get("model", "")),
                str(unit.get("brand", "")),
                str(unit.get("status", "")),
                str(unit.get("screen_size", "")),
            ]).lower()

            if search in combined:
                filtered.append(unit)

        units = filtered

    return render_template("portal.html", units=units, search=search)


@app.route("/unit/<int:unit_id>")
def unit_detail(unit_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    unit = get_unit_by_id(unit_id)

    if not unit:
        return redirect(url_for("portal"))

    return render_template("detail.html", unit=unit)


@app.route("/unit/<int:unit_id>/packing-slip")
def packing_slip(unit_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    unit = get_unit_by_id(unit_id)

    if not unit:
        return redirect(url_for("portal"))

    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("packing_slip.html", unit=unit, today=today)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
