# database_history.py
import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["futureGoalAI"]
history = db["history"]


def save_history(name, school, goal, phone, gender, captured_id, ai_id, card_id):
    """
    Save student metadata + file IDs to MongoDB.
    """
    history.insert_one({
        "name": name,
        "school": school,
        "goal": goal,
        "phone": phone,
        "gender": gender,
        "captured_image_id": captured_id,
        "ai_image_id": ai_id,
        "printable_card_id": card_id,
        "timestamp": datetime.now()
    })
