let currentPage = 1;

async function fetchAccounts(page) {
    try {
        const response = await fetch(`/accounts/list?page=${page}`);
        if (!response.ok) throw new Error('Failed to fetch accounts');
        const data = await response.json();

        const tbody = document.getElementById('accounts-table');
        if (data.accounts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="2">No accounts found</td></tr>';
        } else {
            tbody.innerHTML = data.accounts.map(acc => `
                <tr>
                    <td>${acc.account_number}/${acc.bank_code}</td>
                    <td>$${acc.balance.toLocaleString()}</td>
                </tr>
            `).join('');
        }

        document.getElementById('page-info').textContent = `Page ${data.page} of ${data.total_pages}`;
        document.getElementById('prev-btn').disabled = data.page <= 1;
        document.getElementById('next-btn').disabled = data.page >= data.total_pages;

        currentPage = data.page;

        hideError();
    } catch (error) {
        showError('Error loading accounts: ' + error.message);
    }
}

function changePage(delta) {
    fetchAccounts(currentPage + delta);
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

function refreshData(){
    fetchAccounts(currentPage)
}

fetchAccounts(1);