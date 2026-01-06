import argparse
import getpass
import json
import secrets
import string
import os

from storage import Storage


def generate_password(length=16):
    """
    Generates a strong, random password.
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = "".join(secrets.choice(alphabet) for i in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3
            and any(c in string.punctuation for c in password)
        ):
            break
    return password


def get_password_store():
    """Prompts for master password, initializes storage and loads passwords."""
    master_password = getpass.getpass("Enter master password: ")
    storage = Storage(master_password)
    data = storage.load()

    if data is None:
        if os.path.exists(storage.filepath):
            print("Failed to decrypt password store. Master password may be incorrect.")
            return None, None
        else:
            return storage, {}

    try:
        passwords = json.loads(data)
        return storage, passwords
    except json.JSONDecodeError:
        print("Error: Could not decode password data. It might be corrupted.")
        return None, None


def main():
    """
    Main function for the password manager.
    """
    parser = argparse.ArgumentParser(description="A secure password manager.")
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate a new password")
    gen_parser.add_argument(
        "-l", "--length", type=int, default=16, help="Length of the password"
    )

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new password entry")
    add_parser.add_argument("service", help="The service name (e.g., google)")
    add_parser.add_argument("username", help="The username for the service")

    # Get command
    get_parser = subparsers.add_parser(
        "get", help="Get a password for a service"
    )
    get_parser.add_argument(
        "service", help="The service name to retrieve the password for"
    )

    # Update command
    update_parser = subparsers.add_parser("update", help="Update a password entry")
    update_parser.add_argument("service", help="The service name to update")
    update_parser.add_argument("-u", "--username", help="The new username")
    update_parser.add_argument("-p", "--prompt-password", action="store_true", help="Prompt for a new password to update the entry")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a password entry")
    delete_parser.add_argument("service", help="The service name to delete")

    # List command
    subparsers.add_parser("list", help="List all stored services")

    args = parser.parse_args()

    if args.command == "generate":
        password = generate_password(args.length)
        print(f"Generated password: {password}")

    elif args.command == "add":
        storage, passwords = get_password_store()
        if storage is None:
            return

        password_to_store = getpass.getpass("Enter password to store: ")

        passwords[args.service] = {
            "username": args.username,
            "password": password_to_store,
        }

        storage.save(json.dumps(passwords))
        print(f"Password for {args.service} added.")

    elif args.command == "get":
        storage, passwords = get_password_store()
        if storage is None:
            return

        if not passwords:
            print("No passwords stored yet.")
            return

        if args.service in passwords:
            entry = passwords[args.service]
            print(f"Service: {args.service}")
            print(f"Username: {entry['username']}")
            print(f"Password: {entry['password']}")
        else:
            print(f"No password found for {args.service}.")

    elif args.command == "update":
        if not args.username and not args.prompt_password:
            print("Error: Please specify a new username with -u or prompt for a new password with -p.")
            return

        storage, passwords = get_password_store()
        if storage is None:
            return

        if not passwords:
            print("No passwords stored yet.")
            return

        if args.service in passwords:
            if args.username:
                passwords[args.service]["username"] = args.username
            if args.prompt_password:
                new_password = getpass.getpass("Enter the new password: ")
                passwords[args.service]["password"] = new_password
            storage.save(json.dumps(passwords))
            print(f"Entry for {args.service} updated.")
        else:
            print(f"No entry found for {args.service}.")

    elif args.command == "delete":
        storage, passwords = get_password_store()
        if storage is None:
            return

        if not passwords:
            print("No passwords stored yet.")
            return

        if args.service in passwords:
            del passwords[args.service]
            storage.save(json.dumps(passwords))
            print(f"Entry for {args.service} deleted.")
        else:
            print(f"No entry found for {args.service}.")

    elif args.command == "list":
        storage, passwords = get_password_store()
        if storage is None:
            return

        if not passwords:
            print("No passwords stored yet.")
            return

        if passwords:
            print("Stored services:")
            for service in passwords:
                print(f"- {service}")
        else:
            print("No services stored yet.")


if __name__ == "__main__":
    main()
