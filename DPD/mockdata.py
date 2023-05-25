import json
import random
from datetime import datetime, timedelta
import mysql.connector


def generate_glucose_data():
    glucose_data = []
    start_time = datetime.now() - timedelta(days=1)
    for i in range(288):  # 288 5-minute intervals in a day
        timestamp = start_time + timedelta(minutes=5 * i)
        glucose_level = random.randint(60, 200)
        trend = random.choice(["STABLE", "SLIGHTLY_UP", "UP", "SLIGHTLY_DOWN", "DOWN"])
        glucose_data.append({
            "timestamp": timestamp.isoformat(),
            "glucose_level": glucose_level,
            "trend": trend,
            "unit": "mg/dL"
        })
    return glucose_data

def generate_alerts(glucose_data, low_threshold, high_threshold, patient_id):
    alerts = []
    for i, data in enumerate(glucose_data):
        if data["glucose_level"] < low_threshold:
            alerts.append({
                "id": f"A{patient_id}_{i}",
                "timestamp": data["timestamp"],
                "type": "low_glucose",
                "message": "Low glucose alert: Please take appropriate action."
            })
        elif data["glucose_level"] > high_threshold:
            alerts.append({
                "id": f"A{patient_id}_{i}",
                "timestamp": data["timestamp"],
                "type": "high_glucose",
                "message": "High glucose alert: Please take appropriate action."
            })
    return alerts

def generate_patient_data(patient_id):
    name = f"Patient {patient_id}"
    age = random.randint(18, 65)
    diabetes_type = random.choice(["Type 1", "Type 2"])

    return {
        "id": patient_id,
        "name": name,
        "age": age,
        "diabetes_type": diabetes_type
    }

def generate_car_data(car_id):
    return {
        "id": car_id,
        "make": "BMW",
        "model": random.choice(["3 Series", "5 Series", "7 Series"]),
        "year": random.randint(2015, 2023)
    }
    
def generate_safety_actions(alerts):
    safety_actions = []

    for alert in alerts:
        if alert["type"] == "low_glucose":
            action = random.choice([
                "Reducing speed and activating hazard lights.",
                "Activating lane assist.",
                "Setting a speed limit to ensure safe driving."
            ])
        elif alert["type"] == "high_glucose":
            action = random.choice([
                "Suggesting a rest stop and providing directions to the nearest doctor or hospital.",
                "Activating lane assist.",
                "Setting a speed limit to ensure safe driving."
            ])
        safety_actions.append({
            "alert_id": alert["id"],
            "action": action
        })

    return safety_actions

def store_mock_data_to_database(mock_data):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bmw"
    )

    try:
        with connection.cursor() as cursor:
            for data in mock_data:
                # Insert patient data
                patient = data["patient"]
                cursor.execute(
                    "INSERT INTO patients (id, name, age, diabetes_type) VALUES (%s, %s, %s, %s)",
                    (patient["id"], patient["name"], patient["age"], patient["diabetes_type"])
                )

                # Insert sensor data
                sensor = data["sensor"]
                cursor.execute(
                    "INSERT INTO sensors (id, model, battery_status, patient_id) VALUES (%s, %s, %s, %s)",
                    (sensor["id"], sensor["model"], sensor["battery_status"], patient["id"])
                )

                # Insert car data
                car = data["car"]
                cursor.execute(
                    "INSERT INTO cars (id, make, model, year, patient_id) VALUES (%s, %s, %s, %s, %s)",
                    (car["id"], car["make"], car["model"], car["year"], patient["id"])
                )

                # Insert glucose data and alerts
                for g_data in data["glucose_data"]:
                    cursor.execute(
                        "INSERT INTO glucose_data (timestamp, glucose_level, trend, unit, sensor_id) VALUES (%s, %s, %s, %s, %s)",
                        (g_data["timestamp"], g_data["glucose_level"], g_data["trend"], g_data["unit"], sensor["id"])
                    )
                    g_data_id = cursor.lastrowid

                    for alert in data["alerts"]:
                        if alert["timestamp"] == g_data["timestamp"]:
                            cursor.execute(
                                "INSERT INTO alerts (id, timestamp, type, message, glucose_data_id) VALUES (%s, %s, %s, %s, %s)",
                                (alert["id"], alert["timestamp"], alert["type"], alert["message"], g_data_id)
                            )
                            alert_id = alert["id"]

                            for safety_action in data["safety_actions"]:
                                if safety_action["alert_id"] == alert_id:
                                    cursor.execute(
                                        "INSERT INTO safety_actions (action, alert_id) VALUES (%s, %s)",
                                        (safety_action["action"], alert_id)
                                    )
        connection.commit()
    finally:
        connection.close()
        
def generate_mock_data(num_patients):
    patients_data = []

    for i in range(num_patients):
        patient_id = f"P{1000 + i}"
        patient_data = generate_patient_data(patient_id)
        glucose_data = generate_glucose_data()
        sensor_id = f"S{1000 + i}"

        low_threshold = 70
        high_threshold = 180
        alerts = generate_alerts(glucose_data, low_threshold, high_threshold, patient_id)
        safety_actions = generate_safety_actions(alerts)

        car_id = f"C{1000 + i}"
        car_data = generate_car_data(car_id)

        mock_data = {
            "sensor": {
                "id": sensor_id,
                "model": "CGM-Sensor-XYZ",
                "battery_status": f"{random.randint(10, 100)}%"
            },
            "patient": patient_data,
            "car": car_data,
            "glucose_data": glucose_data,
            "settings": {
                "low_glucose_threshold": low_threshold,
                "high_glucose_threshold": high_threshold,
                "measurement_interval_minutes": 5
            },
            "alerts": alerts,
            "safety_actions": safety_actions
        }

        patients_data.append(mock_data)

    return patients_data

num_patients = 1000
mock_data = generate_mock_data(num_patients)
mock_data_json = json.dumps(mock_data, indent=2)

store_mock_data_to_database(mock_data)

with open("mock_data.json", "w") as f:
    f.write(mock_data_json)
