from flask import Flask, jsonify, render_template, request
from dcc import Accessory
from serial_comms import get_connected_serial_device

print("Starting server...")

app = Flask(__name__)

class State:
    def __init__(self):
        self.controller = get_connected_serial_device()
        self.signal = Accessory(self.controller, 42, ["green", "red", "yellow", "two-yellow"])

state = None
if state is None:
    state = State()

# Current state
current_signal = "green"

@app.route('/set_speed')
def set_speed():
    speed = request.args.get('speed', 0, type=int)
    speed = max(0, min(100, speed))
    print(f"MOCK: Sending DCC command for speed {speed}")
    return f"Speed set to {speed}%"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

@app.route('/set_signal')
def set_signal():
    global current_signal
    # Get the signal name from the URL (?type=red)
    new_signal = request.args.get('type', 'green')
    
    state.signal.setState(new_signal)

    current_signal = new_signal
    print(f"Signal changed to: {current_signal}")
    
    # Return confirmation
    return jsonify({"status": "success", "current_signal": current_signal})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)