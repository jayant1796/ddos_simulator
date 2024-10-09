from flask import Flask, jsonify, request, render_template
import random
import time
import threading

app = Flask(__name__)

attack_data = []
attack_active = False

def simulate_attack(attack_type, target_url, num_requests):
    global attack_active, attack_data
    requests_sent = 0
    start_time = time.time()

    for _ in range(num_requests):
        if not attack_active:
            break
        time.sleep(1)  
        requests_sent += random.randint(1, 10) 
        current_time = time.time() - start_time
        attack_data.append({"time": f"{int(current_time)}s", "requests": requests_sent, "target": target_url, "type": attack_type})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_attack', methods=['POST'])
def start_attack():
    global attack_active
    attack_info = request.json
    attack_type = attack_info.get('type')
    target_url = attack_info.get('target')
    num_requests = attack_info.get('requests')

    if not attack_active: 
        attack_active = True
        threading.Thread(target=simulate_attack, args=(attack_type, target_url, num_requests)).start()
        return jsonify({"message": f"{attack_type} attack started on {target_url} with {num_requests} requests!"}), 200
    return jsonify({"message": "An attack is already in progress!"}), 400

@app.route('/stop_attack', methods=['POST'])
def stop_attack():
    global attack_active
    attack_active = False
    return jsonify({"message": "Attack stopped!"}), 200

@app.route('/attack_data', methods=['GET'])
def get_attack_data():
    return jsonify(attack_data), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)  # Set the desired port here
