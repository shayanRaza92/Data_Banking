from PyQt6.QtWidgets import QPushButton, QTableWidget, QHeaderView

COMMON_STYLE = """
/* GLOBAL SANS-SERIF FONT */
* {
    font-family: 'Segoe UI', sans-serif;
    font-size: 10pt;
}

/* MAIN BACKGROUND - "Premium Wealth" Dark Gradient */
#centralwidget {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #141E30, stop:1 #243B55);
}

/* LABELS */
QLabel {
    color: #e0e0e0;
    font-weight: bold;
    font-size: 11pt;
    background: transparent;
}
/* Title Labels - Gold Accent */
QLabel#titleLabel {
    font-size: 20pt;
    font-weight: 900;
}

/* INPUT FIELDS - "Glass" Look */
QLineEdit, QTextEdit, QPlainTextEdit, QDateEdit, QSpinBox {
    background-color: rgba(255, 255, 255, 0.95);
    color: #333333;
    border: 2px solid #5d7599;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 11pt;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #FFD700; /* Gold Focus */
    background-color: #ffffff;
}
QLineEdit::placeholder {
    color: #666666;
    font-style: italic;
}

/* COMBO BOXES */
QComboBox {
    background-color: rgba(255, 255, 255, 0.95);
    color: #333333;
    border: 2px solid #5d7599;
    border-radius: 8px;
    padding: 6px 15px;
    min-width: 6em;
}
QComboBox:on {
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #333333;
    selection-background-color: #FFD700;
    selection-color: #000000;
    border: 1px solid #5d7599;
}

/* BUTTONS - Gradient with Symbols */
QPushButton {
    background-color: #1cb5e0;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #000046, stop:1 #1cb5e0);
    color: white;
    font-weight: bold;
    border-radius: 12px;
    padding: 10px 20px;
    font-size: 12pt;
    border: 1px solid rgba(255, 255, 255, 0.2);
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1cb5e0, stop:1 #000046);
    border: 1px solid #FFD700;
}
QPushButton:pressed {
    background-color: #000046;
    margin-top: 2px;
}

/* TABLES - Premium Grid */
QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f0faff;
    color: #333333;
    gridline-color: #d0d0d0;
    selection-background-color: #000046; /* Navy Blue Selection */
    selection-color: #FFD700; /* Gold Text on Selection */
    border-radius: 8px;
    font-size: 10pt;
    border: none;
}
QHeaderView::section {
    background-color: #000046;
    color: #FFD700;
    padding: 8px;
    font-weight: bold;
    font-size: 11pt;
    border: none;
    border-right: 1px solid #1cb5e0;
}

/* SCROLL BARS */
QScrollBar:vertical {
    border: none;
    background: #243B55;
    width: 12px;
    margin: 0px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background: #FFD700;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

def add_icons(window):
    """Adds symbols to buttons based on their object name."""
    
    # Map button names/patterns to icons
    icon_map = {
        "btnBack": "🔙 Back",
        "btnUserLogin": "👤 User Login",
        "btnAdminLogin": "🛡️ Admin Login",
        "btnLogin": "🔐 Login",
        "btnRegister": "📝 Register",
        "btnSubmit": "✅ Submit",
        "btnApply": "📑 Apply",
        
        "btnCreateAccount": "🆕 Create Account",
        "btnWithdraw": "🏧 Withdraw",
        "btnDeposit": "💰 Deposit",
        "btnTransfer": "💸 Transfer Money",
        "btnHistory": "📜 Transaction History",
        "btnShowBalance": "💳 View Balance",
        "btnApplyLoan": "🏦 Apply for Loan",
        
        "btnApprove": "✔️ Approve",
        "btnReject": "❌ Reject",
        "btnDelete": "🗑️ Delete",
        "btnDisapprove": "🚫 Disapprove",
        
        "btnViewUsers": "👥 View Users",
        "btnApproveUsers": "✅ Approve Users",
        "btnDeleteUsers": "🗑️ Deactivate Users",
        "btnViewTransactions": "📊 View Transactions",
        "btnApproveLoan": "👍 Approve Loans",
        "btnApproveTransactions": "💸 Approve Transfers",
        
        "btnDate": "📅 Select Date",
        "btnCheck": "🔍 Check",
        "btnAddPhone": "➕ Add Phone",
        "btnPay": "💸 Pay Loan"
    }

    buttons = window.findChildren(QPushButton)
    for btn in buttons:
        name = btn.objectName()
        
        # Exact match
        if name in icon_map:
            # Check if icon already added to avoid duplication on re-runs
            current_text = btn.text()
            new_text = icon_map[name]
            # Only update if it doesn't already contain the icon (simple heuristic)
            if new_text.split()[0] not in current_text: 
                btn.setText(new_text)
        
        # Fallback partial matches if needed
        elif "back" in name.lower():
            btn.setText("🔙 Back")

def apply_style(window):
    """Applies the common stylesheet and icons to the given window."""
    
    # 1. Apply Stylesheet
    if window.centralWidget():
        window.centralWidget().setObjectName("centralwidget")
        window.centralWidget().setStyleSheet(COMMON_STYLE)
    else:
        window.setStyleSheet(COMMON_STYLE)

    # 2. Add Icons
    add_icons(window)
