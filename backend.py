from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/appointment_db'
mongo = PyMongo(app)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if mongo.db.users.find_one({"username": username}):
        return jsonify({"message": "User already exists"}), 400

    # Check if password already exists
    if mongo.db.users.find_one({"password":password}):
        return jsonify({"message": "Password already exists"}), 400

    # Hash the password
    # hashed_password = generate_password_hash(password)
    mongo.db.users.insert_one({"username": username, "password": password})

    return jsonify({"message": "User created successfully"}), 200
    

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = mongo.db.users.find_one({"username": username})
    if user and user['password']==password:
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    data = request.json
    doctor_id = data.get('doctor_id')
    date = data.get('date')
    time = data.get('time')
    
    mongo.db.appointments.insert_one({"doctor_id": doctor_id, "date": date, "time": time})
    return jsonify({"message": "Appointment booked successfully"}), 200

@app.route('/get_appointments', methods=['GET'])
def get_appointments():
    appointments = mongo.db.appointments.find()
    result = []
    for appointment in appointments:
        appointment['_id'] = str(appointment['_id'])  # Convert ObjectId to string
        result.append(appointment)
    return jsonify(result)

@app.route('/cancel_latest_appointment', methods=['DELETE'])
def cancel_latest_appointment():
    latest_appointment = mongo.db.appointments.find_one(sort=[("date", -1), ("time", -1)])
    if latest_appointment:
        result = mongo.db.appointments.delete_one({"_id": latest_appointment["_id"]})
        if result.deleted_count > 0:
            return jsonify({"message": "Latest appointment canceled successfully"}), 200
    return jsonify({"message": "No appointments found or failed to cancel"}), 400

# @app.route('/check_password', methods=['POST'])
# def check_password():
#     data = request.get_json()
#     password = data.get("password")
#     if mongo.db.users.find_one({"password": password}):
#         return jsonify({"message": "Password already exists"}), 409
#     return jsonify({"message": "Password available"}), 200



if __name__ == '__main__':
    app.run(debug=True)
