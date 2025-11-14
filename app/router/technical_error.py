from fastapi import APIRouter, HTTPException, status, Request
from typing import List
import logging
from datetime import datetime
import json

from app.entities.models import TechnicalErrorReportCreate, TechnicalErrorReport
from app.data.database import (
    save_technical_error_report,
    get_technical_error_reports,
    get_technical_error_report_by_id
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/technical-error-report/debug")
async def debug_technical_error_report(request: Request):
    """
    Debug endpoint để kiểm tra raw request data
    """
    try:
        body = await request.body()
        logger.info(f"Raw request body: {body}")
        
        try:
            json_data = await request.json()
            logger.info(f"Parsed JSON: {json_data}")
            return {"received_data": json_data, "status": "debug_success"}
        except Exception as parse_error:
            logger.error(f"JSON parse error: {parse_error}")
            return {"error": f"JSON parse error: {str(parse_error)}", "raw_body": body.decode()}
            
    except Exception as e:
        logger.exception(f"Debug endpoint error: {e}")
        return {"error": str(e)}

@router.post("/technical-error-report", response_model=dict)
async def create_technical_error_report(report: TechnicalErrorReportCreate):
    """
    Tạo báo cáo lỗi kỹ thuật mới
    """
    try:
        # Log thông tin request để debug
        logger.info(f"Received technical error report: {report}")
        
        # Validation: Phải có ít nhất email hoặc số điện thoại
        if not report.phone and not report.email:
            logger.warning(f"Missing contact info - phone: {report.phone}, email: {report.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phải cung cấp ít nhất email hoặc số điện thoại"
            )
        
        # Validation: Kiểm tra các trường bắt buộc
        if not report.name or not report.name.strip():
            logger.warning(f"Empty name field: {report.name}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên không được để trống"
            )
        
        if not report.organization or not report.organization.strip():
            logger.warning(f"Empty organization field: {report.organization}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tổ chức không được để trống"
            )
        
        if not report.error_content or not report.error_content.strip():
            logger.warning(f"Empty error_content field: {report.error_content}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nội dung lỗi không được để trống"
            )
        
        # Lưu vào database
        logger.info(f"Saving report to database...")
        success = save_technical_error_report(
            name=report.name.strip(),
            organization=report.organization.strip(),
            error_content=report.error_content.strip(),
            phone=report.phone.strip() if report.phone else None,
            email=report.email.strip() if report.email else None,
            image_url=report.image_url.strip() if report.image_url else None
        )
        
        if success:
            logger.info(f"Report saved successfully")
            return {
                "message": "Báo cáo lỗi kỹ thuật đã được lưu thành công",
                "status": "success"
            }
        else:
            logger.error(f"Failed to save report to database")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Không thể lưu báo cáo lỗi kỹ thuật"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Lỗi khi tạo báo cáo lỗi kỹ thuật: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi tạo báo cáo lỗi kỹ thuật"
        )

@router.get("/technical-error-reports", response_model=dict)
async def get_all_technical_error_reports(limit: int = 50, offset: int = 0):
    """
    Lấy danh sách tất cả báo cáo lỗi kỹ thuật
    """
    try:
        if limit < 1 or limit > 100:
            limit = 50
        
        if offset < 0:
            offset = 0
        
        reports = get_technical_error_reports(limit, offset)
        
        # Chuyển đổi ObjectId thành string để có thể serialize
        for report in reports:
            if "_id" in report:
                report["id"] = str(report["_id"])
                del report["_id"]
        
        return {
            "reports": reports,
            "total": len(reports),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.exception(f"Lỗi khi lấy danh sách báo cáo lỗi kỹ thuật: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi lấy danh sách báo cáo lỗi kỹ thuật"
        )

@router.get("/technical-error-report/{report_id}", response_model=dict)
async def get_technical_error_report(report_id: str):
    """
    Lấy báo cáo lỗi kỹ thuật theo ID
    """
    try:
        report = get_technical_error_report_by_id(report_id)
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy báo cáo lỗi kỹ thuật"
            )
        
        # Chuyển đổi ObjectId thành string
        if "_id" in report:
            report["id"] = str(report["_id"])
            del report["_id"]
        
        return {"report": report}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Lỗi khi lấy báo cáo lỗi kỹ thuật {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi lấy báo cáo lỗi kỹ thuật"
        )
