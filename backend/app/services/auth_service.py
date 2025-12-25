from app.db.mongo import users
from werkzeug.security import generate_password_hash, check_password_hash

def signup(email, password):
    users.insert_one({
        "email": email,
        "password_hash": generate_password_hash(password)
    })

def login(email, password):
    user = users.find_one({"email": email})
    if not user:
        return None
    if not check_password_hash(user["password_hash"], password):
        return None
    return str(user["_id"])
