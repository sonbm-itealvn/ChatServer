import bcrypt
from app.data.database import user_collection

def register_user(username, password):
    if user_collection.find_one({"username": username}):
        return None
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    result = user_collection.insert_one({"username": username, "password": hashed})
    return str(result.inserted_id)

def login_user(username, password):
    user = user_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode(), user["password"]):
        return str(user["_id"])
    return None
