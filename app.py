from flask import Flask, request, jsonify, send_file
import mysql.connector
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime, timedelta
import numpy as np
import math
import matplotlib
import json
# ----------------------------------------------------------------------------------------
# app.py
#   
# App providing interface to data avaliable in the DB
# Web interface - index.html
# Based on the chosen averaging time (average_time), data is displayed with given resolution
# ----------------------------------------------------------------------------------------


matplotlib.use('Agg')

app = Flask(__name__)

CONFIG_PATH = "/home/michz/Project/db_config_web.json"

with open(CONFIG_PATH, "r") as f:
    db_config = json.load(f)

def round_to_nearest_15_seconds(dt): 
    new_seconds = round(dt.second / 15) * 15
    return dt.replace(second=new_seconds, microsecond=0)

def get_rms_data(start_time, end_time):
    # Fetches RMS data from MySQL database between start_time and end_time
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = """
        SELECT timestamp, rms_value
        FROM rms_data
        WHERE timestamp BETWEEN %s AND %s
        ORDER BY timestamp
    """
    
    cursor.execute(query, (start_time, end_time))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    timestamps = [row[0] for row in result]
    rms_values = [row[1] for row in result]

    # print("Fetched timestamps:", len(timestamps))
    # print("Fetched RMS values:", len(rms_values)) 

    return timestamps, rms_values
    
def fill_missing_values(timestamps, values):
    # Replace empty values with zeros for plotting
    timestamps_continuous = []
    values_continuous = []
    data_dict = {round_to_nearest_15_seconds(ts): val for ts, val in zip(timestamps, values)}
    
    current_time = min(timestamps)
    end_time = max(timestamps)
    
    while current_time <= end_time:
        timestamps_continuous.append(current_time)
        if current_time in data_dict:
            values_continuous.append(data_dict[current_time])
        else:
            values_continuous.append(0)
        current_time += timedelta(seconds=15)
        
    return timestamps_continuous, values_continuous

def calculate_level(rms_values):
    p0 = 20e-6
    rms_values = np.asarray(rms_values)
    rms_levels = 20 * np.log10(rms_values/10 / p0) # devided by 10 for estimated microphone sensitivity
    return rms_levels
        
def average_level_data_for_plot(timestamps_continuous, levels_continuous, average_time):
    # calculate average levels over given average_time (average_time is also the plotting step)
    step = average_time // 15
    print("step: ", step)
    tc_sampled = []
    levels_averaged = []
    
    for i in range(0, len(levels_continuous)//step*step, step):
        tc_sampled.append(timestamps_continuous[i+step])
        level_samples = levels_continuous[i:i + step]
        level_avg = 10 * math.log10(sum(10 ** (l / 10) for l in level_samples) / step)
        levels_averaged.append(level_avg)
        
    return tc_sampled, levels_averaged


@app.route('/')
def index():
    return send_file('/var/www/html/index.html')
    
@app.route('/plot_rms_data', methods=['GET'])
def plot_rms_data():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    average_time = request.args.get('average_time')

    print(f"Received request with start_time: {start_time}, end_time: {end_time}, average_time: {average_time}")

    if not start_time or not end_time or not average_time:
        return jsonify({'error': 'Missing parameters'}), 400

    if average_time not in ['15', '60', '900', '3600']:
        return jsonify({'error': 'Invalid average_time value'}), 400

    average_time = int(average_time)
    timestamps, rms_values = get_rms_data(start_time, end_time)

    # Do not plot if there is no avaliable data to display
    if not timestamps or not rms_values:
        return jsonify({'error': 'No data found for the specified range and average time'}), 404

    levels = calculate_level(rms_values)
    timestamps_cont, levels_cont = fill_missing_values(timestamps, levels)
    time_samples, level_averages = average_level_data_for_plot(timestamps_cont, levels_cont, average_time)
    
    fig, ax = plt.subplots()
    ax.plot(time_samples, level_averages, label='Sound Level')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Sound Level (dB)')
    ax.legend()
    ax.grid(True)

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)

    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)