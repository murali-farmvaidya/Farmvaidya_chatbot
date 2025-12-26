def user_doc(email, password_hash, name):
    return {
        "email": email,
        "name": name,
        "password_hash": password_hash,
        "auth_provider": "local"
    }
