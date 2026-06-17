from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Simple in-memory database
ACCOUNTS_FILE = 'accounts.json'

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as f:
            return json.load(f)
    # Initialize with some test accounts
    initial_accounts = {
        "1001": {"account_number": "1001", "name": "John Doe", "balance": 5000.00, "transactions": []},
        "1002": {"account_number": "1002", "name": "Jane Smith", "balance": 3500.00, "transactions": []},
        "1003": {"account_number": "1003", "name": "Bob Wilson", "balance": 7200.00, "transactions": []}
    }
    save_accounts(initial_accounts)
    return initial_accounts

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)

# Load accounts on startup
accounts = load_accounts()

@app.route('/api/accounts', methods=['GET'])
def get_all_accounts():
    return jsonify(list(accounts.values()))

@app.route('/api/accounts/<account_number>', methods=['GET'])
def get_account(account_number):
    if account_number in accounts:
        return jsonify(accounts[account_number])
    return jsonify({"error": "Account not found"}), 404

@app.route('/api/accounts/<account_number>/deposit', methods=['POST'])
def deposit(account_number):
    if account_number not in accounts:
        return jsonify({"error": "Account not found"}), 404
    
    data = request.get_json()
    amount = float(data.get('amount', 0))
    
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
    
    accounts[account_number]['balance'] += amount
    accounts[account_number]['transactions'].append({
        "type": "deposit",
        "amount": amount,
        "balance_after": accounts[account_number]['balance']
    })
    save_accounts(accounts)
    
    return jsonify(accounts[account_number])

@app.route('/api/accounts/<account_number>/withdraw', methods=['POST'])
def withdraw(account_number):
    if account_number not in accounts:
        return jsonify({"error": "Account not found"}), 404
    
    data = request.get_json()
    amount = float(data.get('amount', 0))
    
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
    
    if amount > accounts[account_number]['balance']:
        return jsonify({"error": "Insufficient funds"}), 400
    
    accounts[account_number]['balance'] -= amount
    accounts[account_number]['transactions'].append({
        "type": "withdrawal",
        "amount": amount,
        "balance_after": accounts[account_number]['balance']
    })
    save_accounts(accounts)
    
    return jsonify(accounts[account_number])

@app.route('/api/transfer', methods=['POST'])
def transfer():
    data = request.get_json()
    from_account = data.get('from_account')
    to_account = data.get('to_account')
    amount = float(data.get('amount', 0))
    
    if from_account not in accounts or to_account not in accounts:
        return jsonify({"error": "One or both accounts not found"}), 404
    
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
    
    if amount > accounts[from_account]['balance']:
        return jsonify({"error": "Insufficient funds"}), 400
    
    # Perform transfer
    accounts[from_account]['balance'] -= amount
    accounts[to_account]['balance'] += amount
    
    accounts[from_account]['transactions'].append({
        "type": "transfer_out",
        "amount": amount,
        "to_account": to_account,
        "balance_after": accounts[from_account]['balance']
    })
    
    accounts[to_account]['transactions'].append({
        "type": "transfer_in",
        "amount": amount,
        "from_account": from_account,
        "balance_after": accounts[to_account]['balance']
    })
    
    save_accounts(accounts)
    
    return jsonify({
        "from_account": accounts[from_account],
        "to_account": accounts[to_account]
    })

if __name__ == '__main__':
    print("Banking API Server starting on http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
