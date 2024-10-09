from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import random
import time
import threading
import os

app = Flask(__name__)
CORS(app)

attack_data = []
attack_active = False
attack_metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "response_times": []
}

# Function to simulate the attack and track metrics
def simulate_attack(attack_type, target_url, num_requests):
    global attack_active, attack_data, attack_metrics
    attack_data = []  # Clear previous attack data
    attack_metrics = {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "response_times": []
    }

    requests_sent = 0
    start_time = time.time()

    for _ in range(num_requests):
        if not attack_active or requests_sent >= num_requests:
            attack_active = False
            break

        time.sleep(1)  # Simulate delay between requests
        requests_sent += random.randint(1, 10)  # Simulate number of requests sent in the current second
        attack_metrics['total_requests'] += 1  # Update total requests

        current_time = time.time() - start_time
        attack_data.append({"time": f"{int(current_time)}s", "requests": requests_sent, "target": target_url, "type": attack_type})

        # Simulate response times and update metrics
        response_time = random.uniform(0.1, 2.0)  # Simulate a random response time
        attack_metrics['response_times'].append(response_time)

        # Simulate success/failure of request
        if response_time < 1.5:
            attack_metrics['successful_requests'] += 1
        else:
            attack_metrics['failed_requests'] += 1

    # After the attack ends, evaluate if the site is vulnerable
    evaluate_vulnerability()

def evaluate_vulnerability():
    # Use the attack metrics to determine if the site might be vulnerable
    total_requests = attack_metrics.get('total_requests', 0)
    failed_requests = attack_metrics.get('failed_requests', 0)
    response_times = attack_metrics.get('response_times', [])

    if total_requests == 0:
        return "No attack was executed."

    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    failure_rate = (failed_requests / total_requests) * 100 if total_requests > 0 else 0

    if avg_response_time > 1.5 and failure_rate > 50:
        return "The site may be vulnerable to Denial of Service (DoS) attacks due to high response time and failure rate."
    else:
        return "The site seems to be stable, with low response times and failure rates."

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

@app.route('/stability_metrics', methods=['GET'])
def stability_metrics():
    total_requests = attack_metrics.get('total_requests', 0)
    successful_requests = attack_metrics.get('successful_requests', 0)
    failed_requests = attack_metrics.get('failed_requests', 0)
    response_times = attack_metrics.get('response_times', [])
    
    # Calculate the average response time
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Calculate success and error rates
    success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
    error_rate = (failed_requests / total_requests) * 100 if total_requests > 0 else 0

    # Provide a summary of the attack
    vulnerability_status = evaluate_vulnerability()

    return jsonify({
        'responseTime': avg_response_time,
        'successRate': success_rate,
        'errorRate': error_rate,
        'vulnerabilityStatus': vulnerability_status
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
