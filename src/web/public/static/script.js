const uptimeElement = document.getElementById('uptime');
const serverStartTime = parseFloat(uptimeElement.getAttribute('data-start-time')) * 1000; // Convert to ms

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error('Failed to fetch stats');
        const data = await response.json();

        document.getElementById('bank-code').textContent = data.bank_code;
        document.getElementById('total-amount').textContent = '$' + data.total_amount.toLocaleString();
        document.getElementById('client-count').textContent = data.client_count;
        document.getElementById('active-connections').textContent = data.active_connections || 0;

        hideError();
    } catch (error) {
        showError('Error loading stats: ' + error.message);
    }
}

function updateUptime() {
    const elapsed = Date.now() - serverStartTime;

    if (elapsed < 0) {
        document.getElementById('uptime').textContent = "Starting...";
        return;
    }

    const totalSeconds = Math.floor(elapsed / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const hours = Math.floor(minutes / 60);
    const displayMinutes = minutes % 60;

    document.getElementById('uptime').textContent =
        `${hours.toString().padStart(2, '0')}:${displayMinutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function refreshData() {
    fetchStats();
}

refreshData();
setInterval(refreshData, 5000);
setInterval(updateUptime, 1000);