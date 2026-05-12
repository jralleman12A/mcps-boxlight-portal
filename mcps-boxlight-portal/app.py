from flask import Flask, render_template, request, redirect, session, url_for
import json
import os

app = Flask(__name__)
app.secret_key = "mcps-boxlight-secret"

PORTAL_PASSWORD = "ChangeThisPassword123!"

DATA_FILE = os.path.join("data", "mcps_portal_data.json")


def load_units():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        password = request.form.get("password")

        if password == PORTAL_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("portal"))

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
            values = [
                str(unit.get("intake_id", "")),
                str(unit.get("serial_number", "")),
                str(unit.get("model", "")),
                str(unit.get("brand", "")),
            ]

            combined = " ".join(values).lower()

            if search in combined:
                filtered.append(unit)

        units = filtered

    return render_template(
        "portal.html",
        units=units,
        search=search,
    )


@app.route("/unit/<int:unit_id>")
def unit_detail(unit_id):

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    units = load_units()

    unit = None

    for item in units:
        if item.get("id") == unit_id:
            unit = item
            break

    if not unit:
        return redirect(url_for("portal"))
    app.run(debug=True)