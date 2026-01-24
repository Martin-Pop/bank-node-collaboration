let statsInterval = null;
let uptimeInterval = null;
let isBankOpen = false;

const uptimeElement = document.getElementById('uptime');
let serverStartTime = parseFloat(uptimeElement.getAttribute('data-start-time') || 0) * 1000;

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

function hideError() {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');

        if (response.status === 404 || response.status === 502) {
             return;
        }

        if (!response.ok) throw new Error('Failed to fetch stats');
        const data = await response.json();

        document.getElementById('bank-code').textContent = data.bank_code;
        document.getElementById('total-amount').textContent = '$' + data.total_amount.toLocaleString();
        document.getElementById('client-count').textContent = data.client_count;
        document.getElementById('active-connections').textContent = data.active_connections || 0;

        isBankOpen = data.is_open;
        updateBankStatusUI(data.is_open);

        hideError();
    } catch (error) {
        if (document.querySelector('.container')) {
            showError('Error loading stats: ' + error.message);
        }
    }
}

function updateUptime() {
    if (!isBankOpen) return;

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

    const uptimeEl = document.getElementById('uptime');
    if (uptimeEl) {
        uptimeEl.textContent =
            `${hours.toString().padStart(2, '0')}:${displayMinutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

function updateBankStatusUI(isOpen) {
    const statusDot = document.querySelector('.status');
    const startBtn = document.getElementById('btn-start');
    const stopBtn = document.getElementById('btn-stop');
    const uptimeSpan = document.getElementById('uptime');

    if (!statusDot || !startBtn || !stopBtn) return;

    if (isOpen) {
        statusDot.style.background = '#5cb85c';
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-block';
    } else {
        statusDot.style.background = '#d9534f';
        startBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
        uptimeSpan.textContent = "Offline";
    }
}

async function controlBank(action) {
    try {
        const response = await fetch('/api/control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: action })
        });

        if (!response.ok) throw new Error('Action failed');

        setTimeout(refreshData, 500);

        if (action === 'start') {
            isBankOpen = true;
            serverStartTime = Date.now();
        }

    } catch (error) {
        showError(`Failed to ${action} bank: ` + error.message);
    }
}

function stopPolling() {
    if (statsInterval) clearInterval(statsInterval);
    if (uptimeInterval) clearInterval(uptimeInterval);
}

async function confirmAppShutdown() {
    if (confirm('DANGER: This will kill the entire application server. Continue?')) {
        try {
            stopPolling();

            const response = await fetch('/api/shutdown', { method: 'POST' });

            if (response.ok) {
                document.body.innerHTML = `
    <style>body { margin: 0; padding: 0; overflow: hidden; }</style>
    <div style="
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background-color: #f4f4f9;
        font-family: Roboto, Helvetica, Arial, sans-serif;
        text-align: center;
        color: #333;
    ">
        <h1 style="margin: 0 0 16px 0; font-size: 2rem; color: #d32f2f;">Application Shutdown</h1>
        <p style="margin: 0; font-size: 1.2rem; color: #555;">You can close this tab.</p>
    </div>
`;
            }
        } catch (error) {
            showError('Shutdown error: ' + error.message);
        }
    }
}

function refreshData() {
    fetchStats();
}

refreshData();
statsInterval = setInterval(refreshData, 5000);
uptimeInterval = setInterval(updateUptime, 1000);