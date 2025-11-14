from fastapi import APIRouter, File, Form, UploadFile
from app.services.uploadfile import upload_image_to_s3

router = APIRouter()
@router.post("/upload-image")
async def upload_image(
    image: UploadFile = File(None),
    user_id: str = Form(None)
):
    try:
        image_url = upload_image_to_s3(image)
        print("image_url", image_url)
        return {
            "success": True,
            "image_url": image_url,
            "message": "Upload ảnh thành công"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Upload ảnh thất bại"
        }
