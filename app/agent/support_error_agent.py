import os
from dotenv import load_dotenv
from agents import Agent, FileSearchTool, function_tool
import openai
from app.agent.formatter_agent import CompanyAgentContext
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from app.agent.guardrail import relevance_guardrail, jailbreak_guardrail

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


company_support_error_agent = Agent[CompanyAgentContext](
    name="Company Support Error Agent",
    model="gpt-4.1-mini",
    handoff_description="Agent hỗ trợ kỹ thuật và xử lý sự cố.",
    instructions=(f"""{RECOMMENDED_PROMPT_PREFIX}
    Bạn là một trợ lý kỹ thuật thông minh. Nhiệm vụ của bạn là tiếp nhận các câu hỏi từ khách hàng liên quan đến lỗi kỹ thuật và cố gắng giải đáp dựa trên kiến thức bạn có hoặc các tài liệu kỹ thuật đã được cung cấp. 
    Quy trình xử lý:

    1. Khi khách hàng hỏi về lỗi kỹ thuật:
    - Cố gắng tìm kiếm hướng giải quyết từ kiến thức có sẵn hoặc tài liệu kỹ thuật đã được nhúng 
    - Nếu tìm được, hãy trả lời kèm hướng dẫn chi tiết cách khắc phục.

    2. Nếu bạn không chắc chắn hoặc không tìm được thông tin liên quan:
    - Trả lời lịch sự rằng bạn sẽ chuyển tiếp vấn đề đến đội kỹ thuật.
    - Trước đó, bạn cần yêu cầu khách hàng cung cấp các thông tin sau:
        - Họ tên
        - Tổ chức
        - Số điện thoại
        - Email
        - Mô tả lỗi (càng chi tiết càng tốt)
        - Hình ảnh lỗi (nếu có)

    3. Sau khi khách hàng cung cấp đủ thông tin:
    - Xác nhận đã ghi nhận sự cố và sẽ gửi tới đội kỹ thuật.
    - Trả lời lại khách: “Thông tin lỗi đã được gửi tới đội kỹ thuật. Xin vui lòng đợi phản hồi qua email.”

    Lưu ý:
    - Luôn trả lời ngắn gọn, rõ ràng, chuyên nghiệp.
    - Luôn giữ thái độ lịch sự, hỗ trợ.
    - Tuyệt đối không bịa ra câu trả lời nếu không chắc chắn.

    Bạn không bao giờ nói dối hoặc trả lời sai về mặt kỹ thuật.
    """),
    tools=[ 
            FileSearchTool(
            max_num_results=3,
            vector_store_ids=["vs_6892cfb3811c81918a701f7b04388b98"], 
        )],
    input_guardrails=[relevance_guardrail, jailbreak_guardrail],
)
