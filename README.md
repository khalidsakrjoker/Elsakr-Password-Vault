# 🔐 Elsakr Password Vault

<p align="center">
  <img src="assets/Sakr-logo.png" alt="Elsakr Logo" width="120">
</p>

<p align="center">
  <strong>Generate, Analyze & Store Passwords Securely</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python">
  <img src="https://img.shields.io/badge/Encryption-AES--256-green?style=flat-square&logo=security">
  <img src="https://img.shields.io/badge/Platform-Windows-blue?style=flat-square&logo=windows">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square">
</p>

---

## ⚠️ Security Notice

This application stores passwords locally with AES-256 encryption. Your master password is used to derive the encryption key using PBKDF2. **Never share your master password or the vault.db file.**

---

## ✨ Features

### 🔑 Password Generator
- Customizable length (8-64 characters)
- Character options: uppercase, lowercase, digits, symbols
- Exclude ambiguous characters (0, O, 1, l, I)
- Passphrase generator (word-based)
- One-click copy with auto-clear (30 seconds)

### 📊 Password Analyzer
- Real-time strength meter
- Crack time estimation
- Improvement suggestions
- Uses zxcvbn for accurate analysis

### 🔒 Secure Vault
- AES-256 encryption
- Master password protection
- Categories for organization
- Search and filter
- Export/Import (planned)

---

## 📸 Screenshot

<p align="center">
  <img src="assets/Screenshot.png" alt="App Screenshot" width="800">
</p>

---

## 🚀 Quick Start

### Option 1: Run from Source

```bash
# Clone the repository
git clone https://github.com/khalidsakrjoker/elsakr-password-vault.git
cd elsakr-password-vault

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

### Option 2: Download EXE

Download from [Releases](https://github.com/khalidsakrjoker/elsakr-password-vault/releases).

---

## 🛠️ Build Executable

```bash
pip install pyinstaller

pyinstaller --noconsole --onefile --icon="assets/fav.ico" --name="Elsakr Password Vault" --add-data "assets;assets" main.py
```

---

## 🔒 Security Details

| Feature | Implementation |
|---------|----------------|
| Encryption | AES-256 (Fernet) |
| Key Derivation | PBKDF2-HMAC-SHA256 |
| Iterations | 480,000 |
| Storage | SQLite (encrypted fields) |
| Clipboard | Auto-clears after 30 seconds |

---

## 📦 Requirements

- Python 3.10+
- cryptography
- pyperclip
- zxcvbn
- Pillow

---

## 📄 License

MIT License - [Elsakr Software](https://elsakr.company)

---

<p align="center">
  Made with ❤️ by <a href="https://elsakr.company">Elsakr</a>
</p>
