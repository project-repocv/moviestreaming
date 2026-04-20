# Simple Banking Application

A simple web-based banking application with a Flask backend and HTML/CSS/JavaScript frontend.

## Features

- **View Accounts**: See all bank accounts with their balances
- **Deposit Money**: Add funds to any account
- **Withdraw Money**: Remove funds from an account (with balance validation)
- **Transfer Funds**: Move money between accounts
- **Transaction History**: Track all transactions for each account

## Project Structure

```
banking-app/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
└── frontend/
    └── index.html          # Web interface
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser (Chrome, Firefox, Safari, Edge)

## Installation & Setup

### Step 1: Install Backend Dependencies

Navigate to the backend directory and install Python packages:

```bash
cd /workspace/banking-app/backend
pip install -r requirements.txt
```

### Step 2: Start the Backend Server

Run the Flask application:

```bash
python app.py
```

The server will start on `http://localhost:5000`

You should see output like:
```
Banking API Server starting on http://localhost:5000
 * Running on http://0.0.0.0:5000
```

### Step 3: Open the Frontend

Open the `index.html` file in your web browser:

**Option A - Direct File Access:**
- Navigate to `/workspace/banking-app/frontend/index.html`
- Double-click the file to open it in your default browser
- Or drag and drop the file into your browser window

**Option B - Using a Local Server (Recommended):**

If you have Python installed, you can serve the frontend with:

```bash
cd /workspace/banking-app/frontend
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

Alternatively, if you have Node.js:

```bash
cd /workspace/banking-app/frontend
npx serve
```

## Testing the Application

### Pre-loaded Test Accounts

The application comes with three pre-configured accounts:

| Account Number | Name         | Initial Balance |
|----------------|--------------|-----------------|
| 1001           | John Doe     | $5,000.00       |
| 1002           | Jane Smith   | $3,500.00       |
| 1003           | Bob Wilson   | $7,200.00       |

### Test Scenarios

#### 1. View All Accounts
- When you open the application, you should see all three accounts listed on the left
- Each account shows the account number, holder name, and current balance

#### 2. Select an Account
- Click on any account in the list to view its details
- The selected account will be highlighted
- Account details and available actions will appear on the right panel

#### 3. Deposit Money
1. Select an account (e.g., John Doe - 1001)
2. Click the "💰 Deposit" button
3. Enter an amount (e.g., 500)
4. Click "Confirm Deposit"
5. Verify the balance increases and the transaction appears in history

#### 4. Withdraw Money
1. Select an account
2. Click the "💸 Withdraw" button
3. Enter an amount less than the balance (e.g., 200)
4. Click "Confirm Withdrawal"
5. Verify the balance decreases and the transaction appears in history

**Test Validation:**
- Try withdrawing more than the balance - you should see an "Insufficient funds" error

#### 5. Transfer Between Accounts
1. Select an account to transfer from (e.g., John Doe - 1001)
2. Click the "🔄 Transfer" button
3. Select a destination account from the dropdown (e.g., Jane Smith - 1002)
4. Enter an amount (e.g., 1000)
5. Click "Confirm Transfer"
6. Verify:
   - Source account balance decreases
   - Destination account balance increases
   - Both accounts show the transfer in their transaction history

#### 6. View Transaction History
- Scroll down to see the transaction history section
- Transactions are color-coded:
  - 🟢 Green border: Deposits and incoming transfers
  - 🔴 Red border: Withdrawals and outgoing transfers
  - 🔵 Blue border: Incoming transfers
  - 🟠 Orange border: Outgoing transfers

### API Testing (Optional)

You can also test the backend API directly using curl or tools like Postman:

```bash
# Get all accounts
curl http://localhost:5000/api/accounts

# Get specific account
curl http://localhost:5000/api/accounts/1001

# Deposit money
curl -X POST http://localhost:5000/api/accounts/1001/deposit \
  -H "Content-Type: application/json" \
  -d '{"amount": 500}'

# Withdraw money
curl -X POST http://localhost:5000/api/accounts/1001/withdraw \
  -H "Content-Type: application/json" \
  -d '{"amount": 200}'

# Transfer money
curl -X POST http://localhost:5000/api/transfer \
  -H "Content-Type: application/json" \
  -d '{"from_account": "1001", "to_account": "1002", "amount": 100}'
```

## Troubleshooting

### Backend won't start
- Ensure Python 3.8+ is installed: `python --version`
- Make sure you're in the backend directory
- Check if port 5000 is already in use

### Frontend can't connect to backend
- Ensure the backend server is running
- Check that the backend is accessible at `http://localhost:5000`
- If using a local server for frontend, ensure CORS is enabled (it is by default)

### Browser security warnings
- When opening HTML files directly, some browsers may restrict API calls
- Use a local HTTP server (Option B above) to avoid this issue

## Stopping the Application

To stop the servers:
- Press `Ctrl+C` in the terminal where the server is running
- Close the browser tab/window

## Notes

- This is a demonstration application using file-based storage
- Account data persists in `accounts.json` in the backend directory
- For production use, implement proper database, authentication, and security measures
