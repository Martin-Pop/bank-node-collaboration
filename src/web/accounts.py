import logging
from flask import Blueprint, render_template, jsonify, request, current_app

log = logging.getLogger("WEB")

accounts_bp = Blueprint('accounts', __name__)


@accounts_bp.route('/')
def index():
    """
    Renders the accounts list page.
    """
    return render_template('accounts.html')


@accounts_bp.route('/list')
def get_accounts_paged():
    """
    API endpoint for getting accounts paged.
    Query params: ?page=1
    """
    try:
        bank = current_app.config['BANK']

        page = request.args.get('page', 1, type=int)
        limit = 10

        if page < 1:
            page = 1

        offset = (page - 1) * limit
        total_accounts = bank.get_accounts_count()

        if offset >= total_accounts > 0:
            paged_accounts = []
        else:
            paged_accounts = bank.get_accounts_paged(offset, limit)

        return jsonify({
            "accounts": paged_accounts,
            "total": total_accounts,
            "page": page,
            "per_page": limit,
            "total_pages": (total_accounts + limit - 1) // limit
        })

    except Exception as e:
        log.error(f"Error getting accounts: {e}")
        return jsonify({"error": str(e)}), 500