import os
import mysql.connector
import json
from datetime import datetime
# ----------------------------------------------------------------------------------------
# check_file_save_to_db.py
# 
# Script for managing data saved by rms_saver.py, sending new rms values into DB
# DATA_DIR should be the same as in rms_saver.py
#
# ----------------------------------------------------------------------------------------

DATA_DIR = "/home/michz/Project/rms_data"
CONFIG_PATH = "/home/michz/Project/db_config.json"

with open(CONFIG_PATH, "r") as f:
    db_config = json.load(f)

def save_rms_to_db(timestamp, rms_value):
    # Insert new row with measurement result into DB
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = "INSERT INTO rms_data (timestamp, rms_value) VALUES (%s, %s)"
        val = (timestamp, rms_value)

        cursor.execute(sql, val)
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def get_latest_timestamp_from_db():
    # obtain date of last measurement data saved in DB
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = "SELECT MAX(timestamp) FROM rms_data"
        cursor.execute(sql)
        result = cursor.fetchone()

        if result[0] is not None:
            return result[0]
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def process_new_files():
    latest_timestamp = get_latest_timestamp_from_db()
    file_list = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".txt")])

    for file_name in file_list:
        file_path = os.path.join(DATA_DIR, file_name)
        if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
            file_timestamp_str = file_name.replace("rms_data_","").replace(".txt","")
            file_timestamp = datetime.strptime(file_timestamp_str, '%Y-%m-%d_%H-%M-%S')

            # If the file is newer than the latest timestamp in the DB, add its content to the DB
            if latest_timestamp is None or file_timestamp >= latest_timestamp:
                
                with open(file_path, "r") as file:
                    lines = file.readlines()
                    data_to_insert = []
                    for line in lines:
                        timestamp_str, rms_value_str = line.strip().split(",")
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        rms_value = float(rms_value_str)
                        if latest_timestamp is None or timestamp > latest_timestamp:
                            data_to_insert.append((timestamp, rms_value))
                    
                    # Ensure chronological order
                    data_to_insert.sort(key=lambda x: x[0])
                    
                    for timestamp, rms_value in data_to_insert:
                        save_rms_to_db(timestamp, rms_value)
                    print(f"saving {len(data_to_insert)} records from: {file_path}")

if __name__ == "__main__":
    process_new_files()