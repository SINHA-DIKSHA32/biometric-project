from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import cv2

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
REPORT_FOLDER = 'reports'
PATIENT_DB = 'patients.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Register patient
@app.route('/register', methods=['POST'])
def register():
    try:
        name = request.form['name']
        gender = request.form['gender']
        age = request.form['age']
        weight = request.form['weight']
        mobile = request.form['mobile']
        email = request.form['email']
        blood_group = request.form['blood_group']
        allergic = request.form['allergic']
        history = request.form['history']

        # Save fingerprint image
        fingerprint_file = request.files['fingerprint']
        fingerprint_filename = secure_filename(fingerprint_file.filename)
        fingerprint_path = os.path.join(UPLOAD_FOLDER, fingerprint_filename)
        fingerprint_file.save(fingerprint_path)

        # Save optional report
        report_filename = ""
        if 'report' in request.files and request.files['report'].filename:
            report_file = request.files['report']
            report_filename = secure_filename(report_file.filename)
            report_path = os.path.join(REPORT_FOLDER, report_filename)
            report_file.save(report_path)

        # Save to JSON
        if os.path.exists(PATIENT_DB):
            with open(PATIENT_DB, 'r') as f:
                patients = json.load(f)
        else:
            patients = []

        patients.append({
            "name": name,
            "gender": gender,
            "age": age,
            "weight": weight,
            "mobile": mobile,
            "email": email,
            "blood_group": blood_group,
            "allergic": allergic,
            "history": history,
            "fingerprint": fingerprint_filename,
            "report": report_filename
        })

        with open(PATIENT_DB, 'w') as f:
            json.dump(patients, f, indent=2)

        return jsonify({"message": f"✅ Patient '{name}' registered successfully."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Match fingerprint using ORB
def match_fingerprint(uploaded_path, stored_path):
    img1 = cv2.imread(uploaded_path, 0)
    img2 = cv2.imread(stored_path, 0)
    if img1 is None or img2 is None:
        return False

    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    if des1 is None or des2 is None:
        return False

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)

    good_matches = [m for m in matches if m.distance < 30]  # More strict

    print(f"Total matches: {len(matches)}, Good matches: {len(good_matches)}")

    return len(good_matches) > 40  # Require more and better matches


# Scan route
@app.route('/scan', methods=['POST'])
def scan():
    if 'fingerprint' not in request.files:
        return jsonify({"error": "No fingerprint file uploaded"}), 400

    file = request.files['fingerprint']
    filename = secure_filename(file.filename)
    uploaded_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(uploaded_path)

    try:
        with open(PATIENT_DB, 'r') as f:
            patients = json.load(f)
    except:
        patients = []

    for patient in patients:
        stored_path = os.path.join(UPLOAD_FOLDER, patient['fingerprint'])
        if os.path.exists(stored_path) and match_fingerprint(uploaded_path, stored_path):
            return jsonify({
                "name": patient['name'],
                "gender": patient['gender'],
                "age": patient['age'],
                "weight": patient['weight'],
                "mobile": patient['mobile'],
                "email": patient['email'],
                "blood_group": patient['blood_group'],
                "allergic": patient['allergic'],
                "history": patient['history'],
                "report": patient.get('report', '')
            })

    return jsonify({"error": "No match found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
