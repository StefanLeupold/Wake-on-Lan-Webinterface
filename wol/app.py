from flask import Flask, render_template, request, redirect, url_for
from wakeonlan import send_magic_packet
import json
import platform
import subprocess

app = Flask(__name__)

# Load existing devices from the JSON file
try:
    with open('devices.json', 'r') as f:
        devices = json.load(f)
except FileNotFoundError:
    devices = []

# Function to check the status of a device
def check_device_status(device):
    if 'ip' in device:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        ping = subprocess.run(
            ["ping", param, "1", "-w", "1000", device['ip']],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if ping.returncode == 0:
            return True
    return False

# Main page
@app.route('/')
def index():
    # Update the status for each device
    for device in devices:
        device['status'] = check_device_status(device)
    return render_template('index.html', devices=devices)

# Wake-up function
@app.route('/wake_up/<int:device_id>')
def wake_up(device_id):
    if 0 <= device_id < len(devices):
        send_magic_packet(devices[device_id]['mac'])
    return redirect(url_for('index'))

# Add device
@app.route('/add_device', methods=['POST'])
def add_device():
    name = request.form['name']
    mac = request.form['mac']
    ip = request.form['ip']
    
    devices.append({'name': name, 'mac': mac, 'ip': ip})
    
    # Save to the JSON file
    with open('devices.json', 'w') as f:
        json.dump(devices, f, indent=2)
    
    return redirect(url_for('index'))

# Delete device
@app.route('/delete_device/<int:device_id>')
def delete_device(device_id):
    if 0 <= device_id < len(devices):
        del devices[device_id]

        # Save to the JSON file
        with open('devices.json', 'w') as f:
            json.dump(devices, f, indent=2)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
