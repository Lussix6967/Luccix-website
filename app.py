from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_mail import Mail, Message
import json
import os

app = Flask(__name__)

# --- E-MAIL EINSTELLUNGEN FÜR WEB.DE ---
app.config['MAIL_SERVER'] = 'smtp.web.de'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'luccix@web.de'
# HINWEIS: Trage hier dein normales WEB.DE Passwort ein, oder (besser) ein "App-Passwort", 
# falls du die Zwei-Faktor-Authentifizierung bei WEB.DE aktiv hast.
app.config['MAIL_PASSWORD'] = 'Luccixclothing1110!' 
app.config['MAIL_DEFAULT_SENDER'] = 'luccix@web.de'

mail = Mail(app)

# Pfad zur Datei, in der die Stimmen dauerhaft gespeichert werden
VOTES_FILE = "votes.json"

DEFAULT_DATA = {
    "oversized_hoodie": {
        "name": "LUCCIX BOXY SHIRT",
        "bild_url": "/static/shirt.png",
        "stimmen": 0
    },
    "cargo_hose": {
        "name": "LUCCIX FITTED CAP",
        "bild_url": "/static/cap.png",
        "stimmen": 0
    }
}

def load_votes():
    if not os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, "w") as f:
            json.dump(DEFAULT_DATA, f)
        return DEFAULT_DATA
    try:
        with open(VOTES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_DATA

def save_votes(data):
    with open(VOTES_FILE, "w") as f:
        json.dump(data, f)

@app.route("/")
def home():
    klamotten_daten = load_votes()
    voted_cookie = request.cookies.get("voted_items", "")
    try:
        voted_items = json.loads(voted_cookie)
    except Exception:
        voted_items = []
    return render_template("mode_index.html", klamotten=klamotten_daten, voted_items=voted_items)

@app.route("/vote/<artikel_id>", methods=["POST"])
def vote(artikel_id):
    klamotten_daten = load_votes()
    if artikel_id in klamotten_daten:
        voted_cookie = request.cookies.get("voted_items", "")
        try:
            voted_items = json.loads(voted_cookie)
        except Exception:
            voted_items = []

        if artikel_id in voted_items:
            klamotten_daten[artikel_id]["stimmen"] = max(0, klamotten_daten[artikel_id]["stimmen"] - 1)
            voted_items.remove(artikel_id)
        else:
            klamotten_daten[artikel_id]["stimmen"] += 1
            voted_items.append(artikel_id)

        save_votes(klamotten_daten)
        response = make_response(redirect(url_for("home")))
        response.set_cookie("voted_items", json.dumps(voted_items), max_age=30*24*60*60)
        return response
    return redirect(url_for("home"))

@app.route("/contact", methods=["POST"])
def contact():
    klamotten_daten = load_votes()
    customer_email = request.form.get("email")
    customer_message = request.form.get("message")
    
    # Echte E-Mail aufbauen und an luccix@web.de senden
    try:
        msg = Message(
            subject=f"LUCCIX Website: New Message from {customer_email}",
            recipients=['luccix@web.de'], # Hier kommt die Nachricht an
            body=f"You received a new message from your website contact form:\n\n"
                 f"From: {customer_email}\n\n"
                 f"Message:\n{customer_message}"
        )
        mail.send(msg)
        success_text = "Thank you! Your message has been sent directly to our team."
    except Exception as e:
        print(f"E-Mail-Error: {e}")
        success_text = "Thank you! Your message has been recorded."

    return render_template("mode_index.html", klamotten=klamotten_daten, voted_items=[], success_message=success_text)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
