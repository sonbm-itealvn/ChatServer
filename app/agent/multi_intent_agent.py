from typing import List, Tuple
from app.agent.info_agent import company_info_agent
from app.agent.price_agent import company_price_agent
from app.agent.support_error_agent import company_support_error_agent
from app.agent.support_technical_agent import company_support_technical_agent

# Optional: You can add LLM-based parsing for more intelligent query splitting

def split_intents(user_query: str) -> List[Tuple[str, str]]:
    """
    Tách câu hỏi thành các intent nhỏ theo loại tác vụ.
    Trả về danh sách (intent_key, sub_query)
    """
    user_query_lower = user_query.lower()
    sub_queries = []

    if any(kw in user_query_lower for kw in ["tên công ty", "địa chỉ", "lịch sử", "fiine là gì"]):
        sub_queries.append(("company_info", "Công ty tên là gì và làm gì?"))

    if any(kw in user_query_lower for kw in ["gói dịch vụ", "giá", "bao nhiêu", "phí", "chi phí"]):
        sub_queries.append(("company_price", "Fiine đang cung cấp các gói dịch vụ nào và mức giá là bao nhiêu?"))

    if any(kw in user_query_lower for kw in ["lỗi", "sự cố", "không vào được", "bị treo"]):
        sub_queries.append(("company_support_error", user_query))

    if any(kw in user_query_lower for kw in ["cách dùng", "tạo công việc", "hướng dẫn", "tính năng"]):
        sub_queries.append(("company_support_technical", user_query))

    return sub_queries


def call_agents_for_query(user_query: str) -> str:
    """
    Gọi tuần tự các agent theo từng phần câu hỏi và hợp nhất kết quả.
    """
    intent_to_agent = {
        "company_info": company_info_agent,
        "company_price": company_price_agent,
        "company_support_error": company_support_error_agent,
        "company_support_technical": company_support_technical_agent,
    }

    sub_queries = split_intents(user_query)
    responses = []

    for intent, sub_query in sub_queries:
        agent = intent_to_agent.get(intent)
        if agent:
            try:
                result = agent.run(sub_query)
                if result:
                    responses.append(result)
            except Exception as e:
                responses.append(f"[Lỗi khi gọi {intent}]: {str(e)}")

    if not responses:
        return "Xin lỗi, tôi không thể xác định được yêu cầu của bạn. Bạn vui lòng nói rõ hơn nhé."

    return "\n\n".join(responses)
