
let totalRequestsSent = 0;

async function startAttack(attackType) {
    const targetUrl = document.getElementById('targetUrl').value;
    const numRequests = document.getElementById('numRequests').value;

    if (!targetUrl) {
        alert("Please enter a target URL.");
        return;
    }

    if (!numRequests || numRequests <= 0) {
        alert("Please enter a valid number of requests.");
        return;
    }

    document.getElementById('statusIndicator').innerHTML = `
        <h3>Status: Attacking ${attackType} on ${targetUrl} with ${numRequests} requests</h3>
        <div class="loader"></div>
    `;

    const response = await fetch('/start_attack', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ type: attackType, target: targetUrl, requests: numRequests })
    });

    if (response.ok) {
        attackData = [];
        totalRequestsSent = 0; 

        const endTime = Date.now() + 5000;

        const interval = setInterval(async () => {
            const dataResponse = await fetch('/attack_data');
            if (dataResponse.ok) {
                const data = await dataResponse.json();
                updateChart(data);
                totalRequestsSent += data[data.length - 1].requests; 
            }
            if (Date.now() > endTime) {
                clearInterval(interval);
                document.getElementById('statusIndicator').innerHTML = `
                    <h3>Status: Attack ended.</h3>
                    <p>Total requests sent during attack: ${totalRequestsSent}</p>
                `;
                attack_active = false; 
            }
        }, 1000);
    } else {
        const message = await response.json();
        alert(message.message);
    }
}


function updateChart(data) {
    const ctx = document.getElementById('attackChart').getContext('2d');
    ctx.clearRect(0, 0, 400, 200);

    const labels = data.map(d => d.time);
    const requestCounts = data.map(d => d.requests);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Traffic (Requests Sent)',
                data: requestCounts,
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Requests Sent'
                    },
                    grid: {
                        color: 'rgba(200, 200, 200, 0.5)',
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time (seconds)'
                    },
                    grid: {
                        color: 'rgba(200, 200, 200, 0.5)',
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Requests: ${context.parsed.y}`;
                        }
                    }
                }
            }
        }
    });
}
