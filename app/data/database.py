import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, Any, List

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["chatbotagent"]
user_collection = db["users"]
chat_collection = db["chats"]
chat_history_collection = db["chat_history"]
technical_error_collection = db["technical_errors"]

def save_chat_history(
    conversation_id: str,
    user_id: str,
    question: str,
    answer: str,
    agent: str,
    context: Dict[str, Any] = None,
    events: List[Dict[str, Any]] = None
) -> bool:
    """
    Lưu lịch sử chat vào database
    """
    try:
        chat_doc = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "agent": agent,
            "timestamp": datetime.utcnow(),
            "context": context,
            "events": events
        }
        
        result = chat_history_collection.insert_one(chat_doc)
        return result.inserted_id is not None
    except Exception as e:
        print(f"Lỗi khi lưu lịch sử chat: {e}")
        return False

def get_chat_history_by_user(user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Lấy lịch sử chat của user từ database
    """
    try:
        cursor = chat_history_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).skip(offset).limit(limit)
        
        return list(cursor)
    except Exception as e:
        print(f"Lỗi khi lấy lịch sử chat: {e}")
        return []

def get_chat_history_by_conversation(conversation_id: str) -> List[Dict[str, Any]]:
    """
    Lấy lịch sử chat theo conversation_id
    """
    try:
        cursor = chat_history_collection.find(
            {"conversation_id": conversation_id}
        ).sort("timestamp", 1)  # Sắp xếp theo thời gian tăng dần
        
        return list(cursor)
    except Exception as e:
        print(f"Lỗi khi lấy lịch sử chat theo conversation: {e}")
        return []

def save_technical_error_report(
    name: str,
    organization: str,
    error_content: str,
    phone: str = None,
    email: str = None,
    image_url: str = None
) -> bool:
    """
    Lưu báo cáo lỗi kỹ thuật vào database
    """
    try:
        # Kiểm tra ít nhất phải có email hoặc số điện thoại
        if not phone and not email:
            raise ValueError("Phải cung cấp ít nhất email hoặc số điện thoại")
        
        error_report = {
            "name": name,
            "organization": organization,
            "phone": phone,
            "email": email,
            "error_content": error_content,
            "image_url": image_url,
            "timestamp": datetime.utcnow()
        }
        
        result = technical_error_collection.insert_one(error_report)
        return result.inserted_id is not None
    except Exception as e:
        print(f"Lỗi khi lưu báo cáo lỗi kỹ thuật: {e}")
        return False

def get_technical_error_reports(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """
    Lấy danh sách báo cáo lỗi kỹ thuật từ database
    """
    try:
        cursor = technical_error_collection.find().sort("timestamp", -1).skip(offset).limit(limit)
        return list(cursor)
    except Exception as e:
        print(f"Lỗi khi lấy danh sách báo cáo lỗi kỹ thuật: {e}")
        return []

def get_technical_error_report_by_id(report_id: str) -> Dict[str, Any]:
    """
    Lấy báo cáo lỗi kỹ thuật theo ID
    """
    try:
        from bson import ObjectId
        return technical_error_collection.find_one({"_id": ObjectId(report_id)})
    except Exception as e:
        print(f"Lỗi khi lấy báo cáo lỗi kỹ thuật theo ID: {e}")
        return None
