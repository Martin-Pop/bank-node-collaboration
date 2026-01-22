let startTime = Date.now();

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

async function fetchAccounts() {
    try {
        const response = await fetch('/api/accounts');
        if (!response.ok) throw new Error('Failed to fetch accounts');
        const accounts = await response.json();

        const tbody = document.getElementById('accounts-table');
        if (accounts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="2">No accounts</td></tr>';
        } else {
            tbody.innerHTML = accounts.map(acc => `
                <tr>
                    <td>${acc.account_number}/${acc.bank_code}</td>
                    <td>$${acc.balance.toLocaleString()}</td>
                </tr>
            `).join('');
        }
    } catch (error) {
        showError('Error loading accounts: ' + error.message);
    }
}

function updateUptime() {
    const elapsed = Date.now() - startTime;
    const minutes = Math.floor(elapsed / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    document.getElementById('uptime').textContent =
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function refreshData() {
    fetchStats();
    fetchAccounts();
}

async function confirmShutdown() {
    if (confirm('Are you sure you want to shutdown the bank?')) {
        try {
            const response = await fetch('/api/shutdown', { method: 'POST' });
            if (response.ok) {
                document.querySelector('.status').style.background = '#d9534f';
                alert('Bank is shutting down...');
            }
        } catch (error) {
            showError('Shutdown error: ' + error.message);
        }
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function hideError() {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

refreshData();
setInterval(refreshData, 5000);
setInterval(updateUptime, 1000);