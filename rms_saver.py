import pyaudio
import numpy as np
import time
from datetime import datetime
import os

CHUNK = 22050
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 15
NEW_FILES_N_MINUTES = 15
DATA_DIR = "/home/michz/Project/rms_data"


def save_rms_and_time_to_dict(rms_15):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rms_data_dict[current_time] = rms_15

def save_dict_to_file(file_name):
    file_path = os.path.join(DATA_DIR, f"rms_data_{file_name}.txt")
    with open(file_path, "a") as file:
        for timestamp, rms_value in sorted(rms_data_dict.items()):
            file.write(f"{timestamp},{rms_value}\n")

def wait_for_full_minute(): #FUNKCJA WYGENEROWANA PRZE CHAT GPT
    now = datetime.now()
    while now.second % 60 != 0:
        time.sleep(1 - now.microsecond / 1e6)
        now = datetime.now()

rms_data_dict = {}
rms_values = []
wait_for_full_minute()
start_time = time.time()
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
file_rotation_time = start_time + (NEW_FILES_N_MINUTES * 60)
folder_date_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

try:
    while True:
        data = stream.read(CHUNK)
        samples = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean((samples / 10000) ** 2))
        rms_values.append(rms)

        elapsed_time = time.time() - start_time
        current_time = datetime.now()

        if elapsed_time + 0.25 >= RECORD_SECONDS:
            rms_15 = np.sqrt(np.mean(np.array(rms_values) ** 2))
            save_rms_and_time_to_dict(rms_15)
            rms_values = []

            if current_time.second % 15 != 0:
                seconds_to_next_quarter = 15 - (current_time.second % 15)
                start_time = time.time() + seconds_to_next_quarter - 0.5
            else:
                start_time = time.time()

        if time.time() >= file_rotation_time:
            save_dict_to_file(folder_date_name)
            rms_data_dict.clear()  
            file_rotation_time = time.time() + (NEW_FILES_N_MINUTES * 60)
            folder_date_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

except KeyboardInterrupt:
    stream.stop_stream()
    stream.close()
    audio.terminate()