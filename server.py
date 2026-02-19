from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/set_speed')
def set_speed():
    speed = request.args.get('speed', 0, type=int)
    # Simple input validation
    speed = max(0, min(100, speed))
    # In the future, this is where your DCC/Motor code goes!
    print(f"MOCK: Sending DCC command for speed {speed}")
    return f"Speed set to {speed}%"

# This handles both the home page AND any weird URLs the phone pings
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)