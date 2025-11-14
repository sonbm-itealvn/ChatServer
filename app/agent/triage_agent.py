import os
import openai
from dotenv import load_dotenv
from agents import Agent
from app.agent.formatter_agent import CompanyAgentContext
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from app.agent.info_agent import company_info_agent
from app.agent.price_agent import company_price_agent
from app.agent.support_error_agent import company_support_error_agent
from app.agent.support_technical_agent import company_support_technical_agent
from app.agent.guardrail import relevance_guardrail, jailbreak_guardrail
from app.agent.multi_intent_agent import call_agents_for_query

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class SmartTriageAgent(Agent[CompanyAgentContext]):
    def run(self, query: str) -> str:
        if sum(query.count(sep) for sep in ["và", "với", ",", "cùng"]) >= 2:
            return call_agents_for_query(query)
        return super().run(query)

triage_agent = SmartTriageAgent(
    name="Triage Agent",
    model="gpt-4.1-mini",
    handoff_description="Agent điều phối yêu cầu khách hàng đến agent phù hợp.",
    instructions=(f"""{RECOMMENDED_PROMPT_PREFIX}

Bạn là triage agent (tác nhân phân luồng).
Nhiệm vụ của bạn là xác định xem câu hỏi của người dùng có thuộc chủ đề Chuyển đổi số của Đoàn Thanh niên Việt Nam hay không và điều hướng đúng agent chuyên trách.

🎯 Nhiệm vụ chính của bạn

→ Khi câu hỏi của người dùng liên quan đến chuyển đổi số trong Đoàn Thanh niên Việt Nam, như:

Chuyển đổi số trong tổ chức Đoàn

Ứng dụng công nghệ số cho thanh niên

Nền tảng số, dữ liệu số, phần mềm phục vụ Đoàn

Giải pháp số hóa hồ sơ, phong trào, hoạt động

Lợi ích chuyển đổi số cho cán bộ Đoàn, đoàn viên, thanh niên

Chiến lược, định hướng, lộ trình chuyển đổi số của Đoàn

Ứng dụng AI, IoT, cloud, dữ liệu lớn cho hoạt động Đoàn

Chuyển đổi số tại cơ sở Đoàn trường, Đoàn doanh nghiệp, Đoàn địa phương

Giải pháp truyền thông số, mạng xã hội, nền tảng tương tác thanh niên

Chuyển đổi số trong quản lý đoàn vụ, đoàn viên, phong trào thanh niên

Triển khai các đề án, dự án chuyển đổi số theo TƯ Đoàn
→ Chuyển đến **Company Info Agent**
🔒 Giới hạn

Không trả lời nội dung chính sách.

Không suy đoán ngoài nội dung người dùng đưa ra.

Chỉ trả về duy nhất nhãn phân loại, không giải thích thêm.

⚠️ Lưu ý:
- KHÔNG trả lời thay agent chuyên môn.
- Ưu tiên chuyển đúng agent chỉ dựa vào nội dung.
"""),
    handoffs=[
        company_info_agent,
        company_price_agent,
        company_support_error_agent,
        company_support_technical_agent,
    ],
    input_guardrails=[relevance_guardrail, jailbreak_guardrail],
)

company_info_agent.handoffs.append(triage_agent)
company_price_agent.handoffs.append(triage_agent)
company_support_error_agent.handoffs.append(triage_agent)
company_support_technical_agent.handoffs.append(triage_agent)