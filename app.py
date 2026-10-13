from flask import Flask, render_template, request, redirect, url_for, make_response
import json

app = Flask(__name__)

# Product database
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
    # Read voted items from user's cookies (stored as a JSON list string)
    voted_cookie = request.cookies.get("voted_items", "[]")
    try:
        voted_items = json.loads(voted_cookie)
    except Exception:
        voted_items = []
        
    return render_template("mode_index.html", klamotten=klamotten_daten, voted_items=voted_items)

@app.route("/vote/<artikel_id>", methods=["POST"])
def vote(artikel_id):
    if artikel_id in klamotten_daten:
        voted_cookie = request.cookies.get("voted_items", "[]")
        try:
            voted_items = json.loads(voted_cookie)
        except Exception:
            voted_items = []

        if artikel_id in voted_items:
            # User already voted -> Remove vote (Unlike)
            klamotten_daten[artikel_id]["stimmen"] = max(0, klamotten_daten[artikel_id]["stimmen"] - 1)
            voted_items.remove(artikel_id)
        else:
            # User hasn't voted yet -> Add vote (Like)
            klamotten_daten[artikel_id]["stimmen"] += 1
            voted_items.append(artikel_id)

        # Save the updated list back into the user's browser cookies
        response = make_response(redirect(url_for("home")))
        response.set_cookie("voted_items", json.dumps(voted_items), max_age=30*24*60*60) # Valid for 30 days
        return response
        
    return redirect(url_for("home"))

@app.route("/contact", methods=["POST"])
def contact():
    # Extract data from the contact form
    email = request.form.get("email")
    message = request.form.get("message")
    
    # FOR NOW: Prints messages to your VS Code Terminal / Render Logs.
    # Later, you can connect an email service here.
    print(f"NEW MESSAGE FROM {email}: {message}")
    
    # Redirect back to home with a success flag
    return render_template("mode_index.html", klamotten=klamotten_daten, voted_items=[], success_message="Thank you! Your message has been sent.")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)