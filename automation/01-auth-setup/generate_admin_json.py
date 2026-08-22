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
    
    print("\n=========================================")
    print(" 🎉 SUCCESS! Here is your MongoDB Entry 🎉")
    print("=========================================\n")
    print("Copy and paste the following JSON directly into MongoDB Compass")
    print("to insert the document into the 'users' collection:\n")
    
    print(json.dumps(mongo_doc, indent=4))
    print("\n=========================================\n")

if __name__ == "__main__":
    main()
