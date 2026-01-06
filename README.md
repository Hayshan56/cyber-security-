# Secure Password Manager

This is a secure, command-line password manager written in Python.

## Features

- **Strong Password Generation:** Generate cryptographically secure passwords of a specified length.
- **Secure Storage:** Passwords are encrypted using AES-128-CBC with a key derived from a master password using PBKDF2. Each password file has a unique salt to protect against rainbow table attacks.
- **Full CRUD Functionality:** Add, retrieve, update, delete, and list password entries.
- **Clipboard Integration:** Copy passwords directly to the clipboard for convenience and security.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd secure-password-manager
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

## Usage

The main entry point is `main.py`.

### Generate a new password
```bash
python main.py generate [-l LENGTH]
```
Example:
```bash
python main.py generate -l 24
```

### Add a new password entry
```bash
python main.py add <service> <username>
```
You will be prompted for your master password and the password to store.

### Retrieve a password
```bash
python main.py get <service> [-c]
```
- Use the `-c` or `--copy` flag to copy the password directly to the clipboard.
You will be prompted for your master password.

### Update a password entry
```bash
python main.py update <service> [-u NEW_USERNAME] [-p]
```
- Use `-u` to specify a new username.
- Use `-p` to be prompted for a new password.
You will be prompted for your master password.

### Delete a password entry
```bash
python main.py delete <service>
```
You will be prompted for your master password.

### List all stored services
```bash
python main.py list
```
You will be prompted for your master password.
