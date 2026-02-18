from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_speed')
def set_speed():
    speed = request.args.get('speed', 0, type=int)
    # Simple input validation
    speed = max(0, min(100, speed))
    return f"Speed set to {speed}%"

if __name__ == '__main__':
    # host='0.0.0.0' allows wireless connections via the Hotspot
    app.run(host='0.0.0.0', port=80)