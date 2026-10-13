from flask import Flask, render_template, request, redirect, url_for, make_response
import json
import os

app = Flask(__name__)

# Pfad zur Datei, in der die Stimmen dauerhaft gespeichert werden
VOTES_FILE = "votes.json"

# Standard-Datenstruktur, falls die Datei noch nicht existiert
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
    """Laedt die aktuellen Stimmen aus der JSON-Datei."""
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
    """Speichert die Stimmen dauerhaft in der JSON-Datei."""
    with open(VOTES_FILE, "w") as f:
        json.dump(data, f)

@app.route("/")
def home():
    klamotten_daten = load_votes()
    
    # Stimmen aus den Browser-Cookies des Nutzers auslesen
    voted_cookie = request.cookies.get("voted_items", "[]")
    try:
        voted_items = json.loads(voted_cookie)
    except Exception:
        voted_items = []
        
    return render_template("mode_index.html", klamotten=klamotten_daten, voted_items=voted_items)

@app.route("/vote/<artikel_id>", methods=["POST"])
def vote(artikel_id):
    klamotten_daten = load_votes()

    if artikel_id in klamotten_daten:
        voted_cookie = request.cookies.get("voted_items", "[]")
        try:
            voted_items = json.loads(voted_cookie)
        except Exception:
            voted_items = []

        if artikel_id in voted_items:
            # Nutzer hat bereits abgestimmt -> Stimme abziehen (Unlike)
            klamotten_daten[artikel_id]["stimmen"] = max(0, klamotten_daten[artikel_id]["stimmen"] - 1)
            voted_items.remove(artikel_id)
        else:
            # Nutzer hat noch nicht abgestimmt -> Stimme hinzufügen (Like)
            klamotten_daten[artikel_id]["stimmen"] += 1
            voted_items.append(artikel_id)

        # Stimmen dauerhaft in der Datei speichern
        save_votes(klamotten_daten)

        # Cookie im Browser aktualisieren
        response = make_response(redirect(url_for("home")))
        response.set_cookie("voted_items", json.dumps(voted_items), max_age=30*24*60*60) # 30 Tage gueltig
        return response
        
    return redirect(url_for("home"))

@app.route("/contact", methods=["POST"])
def contact():
    klamotten_daten = load_votes()
    email = request.form.get("email")
    message = request.form.get("message")
    
    # Zeigt Nachrichten im Render-Protokoll (Logs) an
    print(f"NEW MESSAGE FROM {email}: {message}")
    
    return render_template("mode_index.html", klamotten=klamotten_daten, voted_items=[], success_message="Thank you! Your message has been sent.")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
