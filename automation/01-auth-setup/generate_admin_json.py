#!/usr/bin/env python3
import bcrypt
import json
import getpass
import sys

def main():
    print("=========================================")
    print(" Admin User MongoDB JSON Generator")
    print("=========================================\n")
    
    username = input("Enter admin username: ").strip()
    
    password = getpass.getpass("Enter admin password (will be hidden): ")
    password_confirm = getpass.getpass("Confirm admin password: ")
    if password != password_confirm:
        print("Passwords do not match!")
        sys.exit(1)
        
    private_key = getpass.getpass("Enter unique private key (will be hidden): ")
    private_key_confirm = getpass.getpass("Confirm unique private key: ")
    if private_key != private_key_confirm:
        print("Private keys do not match!")
        sys.exit(1)

    print("\nGenerating bcrypt hashes... Please wait.")
    
    passkey_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    private_key_hash = bcrypt.hashpw(private_key.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    mongo_doc = {
        "username": username,
        "passkey_hash": passkey_hash,
        "private_key_hash": private_key_hash,
        "role": "admin"
    }
    
    print("Copy the JSON block below and follow these steps:")
    print("1. Open MongoDB Compass and connect to your Atlas cluster.")
    print("2. Expand your database (e.g., 'codexrelic').")
    print("3. Click on the '+' next to the database name to create a new collection.")
    print("4. Name the collection: admin_users")
    print("5. Open the 'admin_users' collection and click 'ADD DATA' -> 'Insert Document'.")
    print("6. Change the view to '{}' (JSON format) and paste the block below, then click 'Insert':\n")
    
    print(json.dumps(mongo_doc, indent=4))
    print("\n=========================================\n")

if __name__ == "__main__":
    main()
