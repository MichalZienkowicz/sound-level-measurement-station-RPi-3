# Sound Level Measurement Station on Raspberry Pi 3
Provided files allow for creating an application for gathering sound level data on Raspberry Pi 3, model B. 
Data is stored in a MySQL data base on MariaDB server. Can be displayed on a web interface, which is implemented using Apache2 server and Flask framework. 

User can select time over which data was gathered. Only data from first to last measurement timestamp are avaliable, if data between them is missing, 
0 dB is displayed for that time period. User can select averaging time (15s, 1min, 15min, 1h), allowing for displaying the levels with different density. 

## Interface:
![image](https://github.com/user-attachments/assets/a6b6b8a7-1508-4940-849f-80317a998690)
![image](https://github.com/user-attachments/assets/ec8aa204-54ac-45b8-b5c6-7f4a78f03615)

## Folder structure:                    
<pre>
  home/ 
  └── user/                                           # "michz" is used as user name
      └── Project/ 
          ├── rms_saver.py                            # Records and logs RMS values 
          ├── check_file_save_to_db.py                # Parses new data files and saves to DB 
          ├── app.py                                  # Back-end of a web interface 
          ├── db_config.json                          # For connecting with local database 
          ├── index.html                              # Web interface front-end file 
          ├── turn_on_measurement.sh                  # 
          └── rms_data/                               # Directory with data logs 
              └── rms_data_2024-05-01_14-00-00.txt    # Example file with timestamped RMS data </pre>

## Setup
Follow these steps to set up and run the Sound Level Measurement Station on your Raspberry Pi. Setting a virtual environment is adviced.

#### 1. Set up your MySQL (MariaDB) database
- Install and configure MariaDB or MySQL on your Raspberry Pi.
- Create a database called **sound**.
- Create a table **rms_data** with the following structure:
  
  ```sql
  CREATE TABLE rms_data (
      id INT AUTO_INCREMENT PRIMARY KEY,
      timestamp DATETIME NOT NULL,
      rms_value DOUBLE NOT NULL
  );```
  
#### 2. Configure database settings

Open the file db_config.json and adjust connection settings to your database (set **user** and **password**)

#### 3. Install dependencies
in your directory ```/home/user/Project``` install Python 3 and required dependencies (requirements.txt)

#### 4. Update user name related paths
As for now, you have to manually change variables containing user name (change michz to your user name), which are listed below:
- **turn_on_measurement.sh**:
- 
  line 10:```tmux new-session -d -s $session_name "python3 /home/michz/Project/rms_saver.py"```
  
- **rms_saver.py**:
- 
  line 22: ```DATA_DIR = "/home/michz/Project/rms_data"```
  
- **check_file_save_to_db.py**:

  line 13:```DATA_DIR = "/home/michz/Project/rms_data"```
  
  line 14: ```CONFIG_PATH = "/home/michz/Project/db_config.json"```

- **app.py**:

  line 23: ```CONFIG_PATH = "/home/michz/Project/db_config.json"```

#### 5. Start measurements
You can start measurements by running ```turn_on_measurement.sh``` script, which creates tmux session.
To stop measurements, end session using ```tmux kill-session -t rms_saver_session```.

#### 6. Transfer data to DB
Run python script ```check_file_save_to_db.py``` to upload new data to the data base. Optionally you can consider executing this using crontab for regular updates.

#### 7. View data through web interface
Interface will start to work after running ```app.py```.
Interface adress is http://<raspberry_ip>:5000/

## Used devices:
- Raspberry Pi 3, model B
- Virtual 7.1 ch sound (USB sound adapter)
- Screamer Tracer TRAMIC44883 Microphone






