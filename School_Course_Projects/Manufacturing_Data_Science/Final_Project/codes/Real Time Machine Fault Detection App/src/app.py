import os
import time
import datetime
import json
import sqlite3
from flask import Flask, render_template, jsonify, request
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import joblib  # For loading the trained model
import pandas as pd  # For data processing
from utils.signal_processing import process_signals

app = Flask(__name__)

# Load trained model
model = joblib.load('./models/fault_type_classifier_rf.pkl')

# Folder to monitor
MONITOR_FOLDER = './sensor_data'

latest_result = None
past_records = []
processed_files = set()

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        global latest_result, past_records
        if os.path.isfile(event.src_path):
            file_path = event.src_path
            if file_path in processed_files:
                return
            processed_files.add(file_path)

            try:
                # Add a short delay to ensure the file is fully written
                time.sleep(1)

                # Read the raw data
                raw_data = pd.read_csv(file_path, header=None).values.T
                
                # Preprocess the data using process_signals()
                processed_data = process_signals(raw_data)
                
                # Predict fault type and probabilities
                predictions = model.predict(processed_data)
                probabilities = model.predict_proba(processed_data)  # Assuming your model supports probabilities
                
                fault_types = predictions.tolist()  # Convert predictions to a list
                probabilities = probabilities.tolist()  # Convert probabilities to a list
                
                # Record the timestamp
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Check for faults and update the result
                if "normal" in fault_types:
                    latest_result = {"alert": False, "message": "No anomalies detected."}
                else:
                    fault_type_str = ", ".join(fault_types)  # Combine fault types into a string
                    latest_result = {"alert": True, "message": f"Fault detected: {fault_type_str}"}
                
                # Add the record to past_records
                past_records.append({
                    "timestamp": timestamp,
                    "fault_types": fault_types,
                    "probabilities": [max(prob) for prob in probabilities],
                    "file_path": file_path
                })

                # Save to database
                cursor.execute('''
                    INSERT INTO past_records (timestamp, fault_types, probabilities, file_path)
                    VALUES (?, ?, ?, ?)
                ''', (timestamp, ", ".join(fault_types), str(max([max(prob) for prob in probabilities])), file_path))
                conn.commit()

            except Exception as e:
                latest_result = {"alert": True, "message": f"Error processing file: {str(e)}"}

# Start monitoring the folder
observer = Observer()
event_handler = FileHandler()
observer.schedule(event_handler, MONITOR_FOLDER, recursive=False)
observer.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/latest_result', methods=['GET'])
def get_latest_result():
    global latest_result
    return jsonify(latest_result or {"alert": False, "message": "No data processed yet."})

# Initialize the database
DB_PATH = './records.db'
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS past_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        fault_types TEXT,
        probabilities TEXT,
        file_path TEXT
    )
''')
conn.commit()

@app.route('/api/past_records', methods=['GET'])
def get_past_records():
    filter_anomalies = request.args.get('filter_anomalies', 'false').lower() == 'true'
    query = 'SELECT * FROM past_records ORDER BY timestamp DESC'
    if filter_anomalies:
        query = 'SELECT * FROM past_records WHERE fault_types != "normal" ORDER BY timestamp DESC'
    cursor.execute(query)
    records = cursor.fetchall()
    return jsonify([
        {
            "timestamp": record[1],
            "fault_types": record[2].split(", "),
            "probabilities": float(record[3]),
            "file_path": record[4]
        }
        for record in records
    ])


if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        observer.stop()
        observer.join()