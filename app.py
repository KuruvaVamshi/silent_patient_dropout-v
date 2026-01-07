from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

# ------------------------------------
# Helper functions (UNCHANGED)
# ------------------------------------
def normalize(val, max_val):
    return min(val / max_val, 1.0)

def calculate_dropout_score(inputs):
    late_follow = normalize(inputs["Late_Follow"], 50)
    refill_delay = normalize(inputs["Refill_Delay"], 60)
    since_last = normalize(inputs["Since_Last_Applied"], 90)
    missed_labs = normalize(inputs["Missed_Lab_Tests"], 10)
    p_between = normalize(inputs["p_Between"], 60)
    team_calls = normalize(inputs["Team_Calls"], 10)

    replied = 1 if inputs["Response"] == "Yes" else 0

    score = (
        0.25 * late_follow +
        0.25 * refill_delay +
        0.20 * since_last +
        0.10 * missed_labs +
        0.10 * p_between
    )

    if replied == 1:
        score -= 0.10
        score -= 0.10 * team_calls
    else:
        score += 0.10
        score += 0.15 * team_calls

    return round(max(0, min(score * 100, 100)), 2)

def map_risk_level(score):
    if score < 35:
        return "Low"
    elif score < 60:
        return "Medium"
    else:
        return "High"

# ------------------------------------
# PAGE NAVIGATION ROUTES
# ------------------------------------

@app.route("/")
def home():
    return render_template("index.html")   # first page

@app.route("/doctor")
def doctor_login():
    return render_template("doctor.html")

# ---------------- PATIENT LOGIN ----------------
@app.route("/patient")
def patient_login():
    return render_template("patient.html")

#-- SILENT PATIENT DROPOUT---------

@app.route("/silent-dropout")
def silent_dropout():
    return render_template("silent-dropout.html")

@app.route("/patient-status")
def patient_status():
    return render_template("patient-status.html")
 # after login success

# ------------------------------------
# API ROUTE (USED BY silent-dropout.html)
# ------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    required_fields = [
        "p_Between",
        "Late_Follow",
        "Refill_Delay",
        "Since_Last_Applied",
        "Missed_Lab_Tests",
        "Team_Calls",
        "Response"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    score = calculate_dropout_score(data)
    risk = map_risk_level(score)

    return jsonify({
        "silent_dropout_score": score,
        "risk_level": risk
    })

# ------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
