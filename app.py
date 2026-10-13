from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Hier sind jetzt direkte Links zu echten Streetwear-Bildern hinterlegt
klamotten_daten = {
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

@app.route("/")
def home():
    return render_template("mode_index.html", klamotten=klamotten_daten)

@app.route("/vote/<artikel_id>", methods=["POST"])
def vote(artikel_id):
    if artikel_id in klamotten_daten:
        # Stimme um 1 erhöhen
        klamotten_daten[artikel_id]["stimmen"] += 1
    return redirect(url_for("home"))

if __name__ == "__main__":
    # Der Server im Internet weist uns automatisch einen Port zu
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)