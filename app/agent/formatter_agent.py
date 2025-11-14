from pydantic import BaseModel

class CompanyAgentContext(BaseModel):
    """Context dùng cho các agent chăm sóc khách hàng doanh nghiệp."""
    customer_name: str | None = None
    customer_email: str | None = None
    topic: str | None = None  # Chủ đề khách hàng đang hỏi (VD: "giá", "hỗ trợ", "công ty")

def create_initial_context() -> CompanyAgentContext:
    """Tạo context mặc định cho cuộc hội thoại khách hàng doanh nghiệp."""
    return CompanyAgentContext()
