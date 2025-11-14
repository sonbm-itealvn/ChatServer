import os
import uuid
import boto3
from datetime import datetime
from fastapi import UploadFile, HTTPException
from dotenv import load_dotenv
from app.data.database import db

load_dotenv()

# AWS S3 Configuration
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "ap-southeast-1")
)

BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

def upload_image_to_s3(file: UploadFile, folder: str = "technical_errors") -> str:
    try:
        # Kiểm tra file có phải là ảnh không
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File phải là ảnh")
        
        # Tạo tên file unique
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"chat-log-img/original/{folder}/{uuid.uuid4()}.{file_extension}"
        
        # Upload lên S3
        s3_client.upload_fileobj(
            file.file,
            BUCKET_NAME,
            unique_filename,
            ExtraArgs={
                'ContentType': file.content_type,
                'ACL': 'public-read'
            }
        )
        
        # Tạo URL public
        image_url = f"https://{BUCKET_NAME}.s3.{os.getenv('AWS_REGION', 'ap-southeast-1')}.amazonaws.com/{unique_filename}"
        
        return image_url
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi upload ảnh: {str(e)}")

def save_technical_error_to_db(
    user_id: str,
    full_name: str,
    organization: str = None,
    phone: str = None,
    email: str = None,
    issue_description: str = None,
    image_urls: list = None
) -> dict:
    """Save technical error to database"""
    try:
        technical_errors_collection = db["technical_errors"]
        
        error_data = {
            "user_id": user_id,
            "full_name": full_name,
            "organization": organization,
            "phone": phone,
            "email": email,
            "issue_description": issue_description,
            "image_urls": image_urls or [],
            "timestamp": datetime.utcnow(),
            "status": "pending"
        }
        
        result = technical_errors_collection.insert_one(error_data)
        error_data["_id"] = result.inserted_id
        
        return error_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lưu lỗi kỹ thuật: {str(e)}")

def get_technical_errors_by_user_id(user_id: str) -> list:
    """Get technical errors for a specific user"""
    try:
        technical_errors_collection = db["technical_errors"]
        
        cursor = technical_errors_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1)
        
        errors = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for error in errors:
            error["_id"] = str(error["_id"])
        
        return errors
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi lấy lỗi kỹ thuật: {str(e)}")

def update_technical_error_status(error_id: str, status: str, notes: str = None) -> dict:
    """Update technical error status"""
    try:
        from bson import ObjectId
        technical_errors_collection = db["technical_errors"]
        
        update_data = {"status": status}
        if notes:
            update_data["notes"] = notes
        update_data["updated_at"] = datetime.utcnow()
        
        result = technical_errors_collection.update_one(
            {"_id": ObjectId(error_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy lỗi kỹ thuật")
        
        return {"success": True, "message": "Cập nhật trạng thái thành công"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi cập nhật trạng thái: {str(e)}")

