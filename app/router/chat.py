from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from uuid import uuid4
import time
import logging

from agents import (
    Runner,
    ItemHelpers,
    MessageOutputItem,
    HandoffOutputItem,
    ToolCallItem,
    ToolCallOutputItem,
    InputGuardrailTripwireTriggered,
    Handoff,
)
from app.agent.info_agent import company_info_agent
from app.agent.price_agent import company_price_agent
from app.agent.support_error_agent import company_support_error_agent
from app.agent.support_technical_agent import company_support_technical_agent
from app.agent.triage_agent import triage_agent
from app.entities.models import AgentEvent, ChatRequest,ChatResponse, GuardrailCheck, MessageResponse
from app.agent.formatter_agent import create_initial_context
from app.services.chat_history_service import ChatHistoryService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class ConversationStore:
    def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        pass

    def save(self, conversation_id: str, state: Dict[str, Any]):
        pass

class InMemoryConversationStore(ConversationStore):
    _conversations: Dict[str, Dict[str, Any]] = {}

    def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        return self._conversations.get(conversation_id)

    def save(self, conversation_id: str, state: Dict[str, Any]):
        self._conversations[conversation_id] = state

conversation_store = InMemoryConversationStore()

# =========================
# Helpers
# =========================

def _get_agent_by_name(name: str):
    agents = {
        triage_agent.name: triage_agent,
        company_info_agent.name: company_info_agent,
        # company_price_agent.name: company_price_agent,
        # company_support_error_agent.name: company_support_error_agent,
        # company_support_technical_agent.name : company_support_technical_agent,
    }
    return agents.get(name, triage_agent)

def _get_guardrail_name(g) -> str:
    name_attr = getattr(g, "name", None)
    if isinstance(name_attr, str) and name_attr:
        return name_attr
    guard_fn = getattr(g, "guardrail_function", None)
    if guard_fn is not None and hasattr(guard_fn, "__name__"):
        return guard_fn.__name__.replace("_", " ").title()
    fn_name = getattr(g, "__name__", None)
    if isinstance(fn_name, str) and fn_name:
        return fn_name.replace("_", " ").title()
    return str(g)

def _build_agents_list() -> List[Dict[str, Any]]:
    def make_agent_dict(agent):
        return {
            "name": agent.name,
            "description": getattr(agent, "handoff_description", ""),
            "handoffs": [getattr(h, "agent_name", getattr(h, "name", "")) for h in getattr(agent, "handoffs", [])],
            "tools": [getattr(t, "name", getattr(t, "__name__", "")) for t in getattr(agent, "tools", [])],
            "input_guardrails": [_get_guardrail_name(g) for g in getattr(agent, "input_guardrails", [])],
        }
    return [
        make_agent_dict(triage_agent),
        make_agent_dict(company_info_agent),
        # make_agent_dict(company_price_agent),
        # make_agent_dict(company_support_error_agent),
        # make_agent_dict(company_support_technical_agent),
    ]


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    is_new = not req.conversation_id or conversation_store.get(req.conversation_id) is None
    if is_new:
        conversation_id = uuid4().hex
        ctx = create_initial_context()
        current_agent_name = triage_agent.name
        state = {
            "input_items": [],
            "context": ctx,
            "current_agent": current_agent_name,
        }
        if req.message.strip() == "":
            conversation_store.save(conversation_id, state)
            return ChatResponse(
                conversation_id=conversation_id,
                current_agent=current_agent_name,
                messages=[],
                events=[],
                context=ctx.model_dump(),
                agents=_build_agents_list(),
                guardrails=[],
                reply="",
                metadata={}
            )
    else:
        conversation_id = req.conversation_id
        state = conversation_store.get(conversation_id)

    current_agent = _get_agent_by_name(state["current_agent"])
    state["input_items"].append({"content": req.message, "role": "user"})
    old_context = state["context"].model_dump().copy()
    guardrail_checks: List[GuardrailCheck] = []

    try:
        result = await Runner.run(current_agent, state["input_items"], context=state["context"])
    except InputGuardrailTripwireTriggered as e:
        failed = e.guardrail_result.guardrail
        gr_output = e.guardrail_result.output.output_info
        gr_reasoning = getattr(gr_output, "reasoning", "")
        gr_input = req.message
        gr_timestamp = time.time() * 1000
        for g in current_agent.input_guardrails:
            guardrail_checks.append(GuardrailCheck(
                id=uuid4().hex,
                name=_get_guardrail_name(g),
                input=gr_input,
                reasoning=(gr_reasoning if g == failed else ""),
                passed=(g != failed),
                timestamp=gr_timestamp,
            ))
        refusal = "Xin lỗi, tôi chỉ có thể hỗ trợ các chủ đề liên quan đến công ty và dịch vụ."
        state["input_items"].append({"role": "assistant", "content": refusal})

        if req.user_id:
            try:
                await _maybe_await(ChatHistoryService.save_chat(
                    conversation_id=conversation_id,
                    user_id=req.user_id,
                    question=req.message,
                    answer=refusal,
                    agent=current_agent.name,
                    context=state["context"].model_dump(),
                    events=[{"type": "guardrail_failed", "guardrail": _get_guardrail_name(failed)}]
                ))
            except Exception as e:
                logger.exception(f"Không thể lưu guardrail reply: {e}")

        return ChatResponse(
            conversation_id=conversation_id,
            current_agent=current_agent.name,
            messages=[MessageResponse(content=refusal, reply=refusal, agent=current_agent.name)],
            events=[],
            context=state["context"].model_dump(),
            agents=_build_agents_list(),
            guardrails=guardrail_checks,
            reply=refusal,
            metadata={}
        )

    messages: List[MessageResponse] = []
    events: List[AgentEvent] = []

    for item in result.new_items:
        if isinstance(item, MessageOutputItem):
            text = ItemHelpers.text_message_output(item)
            messages.append(MessageResponse(content=text, reply=text, agent=item.agent.name))
            events.append(AgentEvent(id=uuid4().hex, type="message", agent=item.agent.name, content=text))
        elif isinstance(item, HandoffOutputItem):
            events.append(AgentEvent(
                id=uuid4().hex, type="handoff",
                agent=item.source_agent.name,
                content=f"{item.source_agent.name} -> {item.target_agent.name}",
                metadata={"source_agent": item.source_agent.name, "target_agent": item.target_agent.name},
            ))
            current_agent = item.target_agent
        elif isinstance(item, ToolCallItem):
            tool_name = getattr(item.raw_item, "name", None)
            raw_args = getattr(item.raw_item, "arguments", None)
            try:
                import json
                tool_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            except Exception:
                tool_args = raw_args
            events.append(AgentEvent(
                id=uuid4().hex, type="tool_call", agent=item.agent.name,
                content=tool_name or "", metadata={"tool_args": tool_args},
            ))
        elif isinstance(item, ToolCallOutputItem):
            events.append(AgentEvent(
                id=uuid4().hex, type="tool_output", agent=item.agent.name,
                content=str(item.output), metadata={"tool_result": item.output},
            ))

    new_context = state["context"].model_dump()  # dùng thống nhất Pydantic v2
    changes = {k: new_context[k] for k in new_context if old_context.get(k) != new_context[k]}
    if changes:
        events.append(AgentEvent(
            id=uuid4().hex, type="context_update", agent=current_agent.name, content="", metadata={"changes": changes},
        ))

    state["input_items"] = result.to_input_list()
    state["current_agent"] = current_agent.name
    conversation_store.save(conversation_id, state)

    final_guardrails: List[GuardrailCheck] = []
    for g in getattr(current_agent, "input_guardrails", []):
        name = _get_guardrail_name(g)
        failed = next((gc for gc in guardrail_checks if gc.name == name), None)
        if failed:
            final_guardrails.append(failed)
        else:
            final_guardrails.append(GuardrailCheck(
                id=uuid4().hex, name=name, input=req.message, reasoning="", passed=True, timestamp=time.time() * 1000,
            ))

    # Lưu đúng 1 lần với question và câu trả lời cuối cùng
    main_reply = messages[-1].content if messages else ""
    if req.user_id and main_reply:
        try:
            last_agent = messages[-1].agent if messages else current_agent.name
            success = await _maybe_await(ChatHistoryService.save_chat(
                conversation_id=conversation_id,
                user_id=req.user_id,
                question=req.message,
                answer=main_reply,
                agent=last_agent,
                context=state["context"].model_dump(),
                events=[event.model_dump() for event in events]
            ))
            if success is False:
                logger.error("Lỗi khi lưu chat history")
        except Exception as e:
            logger.exception(f"Không thể lưu chat history: {e}")
    elif not req.user_id:
        logger.warning("Không có user_id, bỏ qua lưu chat history")

    metadata = {}
    if messages and any("support" in msg.content.lower() or "hỗ trợ" in msg.content.lower() for msg in messages):
        metadata["requires_support_form"] = True

    return ChatResponse(
        conversation_id=conversation_id,
        current_agent=current_agent.name,
        messages=messages,
        events=events,
        context=state["context"].model_dump(),
        agents=_build_agents_list(),
        guardrails=final_guardrails,
        reply=main_reply,
        metadata=metadata
    )

# Helper: chạy được cho cả sync & async save_chat
import inspect
async def _maybe_await(call):
    if inspect.isawaitable(call):
        return await call
    return call

@router.get("/history/conversation/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """
    Lấy lịch sử chat theo conversation_id
    """
    try:
        if not conversation_id or conversation_id.strip() == "":
            return {"error": "Conversation ID không hợp lệ", "history": []}
        
        db_chats = ChatHistoryService.get_conversation_history(conversation_id)
        
        if not db_chats:
            return {"history": [], "conversation_id": conversation_id}
        
        # Chuyển đổi format
        history = []
        for chat in db_chats:
            history.append({
                "role": "user",
                "content": chat.get("question", ""),
                "timestamp": chat.get("timestamp", None),
                "agent": chat.get("agent", "")
            })
            history.append({
                "role": "assistant",
                "content": chat.get("answer", ""),
                "timestamp": chat.get("timestamp", None),
                "agent": chat.get("agent", "")
            })
        
        # Tạo reply chính từ tin nhắn cuối cùng của assistant
        main_reply = ""
        if history:
            for msg in reversed(history):
                if msg["role"] == "assistant":
                    main_reply = msg["content"]
                    break
        
        # Tạo metadata để hỗ trợ requires_support_form
        metadata = {}
        if main_reply and ("support" in main_reply.lower() or "hỗ trợ" in main_reply.lower()):
            metadata["requires_support_form"] = True
        
        return {
            "history": history,
            "conversation_id": conversation_id,
            "total_messages": len(history),
            "reply": main_reply,
            "metadata": metadata
        }
        
    except Exception as e:
        logging.exception(f"Lỗi khi lấy lịch sử conversation {conversation_id}")
        return {"error": "Đã xảy ra lỗi khi lấy lịch sử conversation", "history": []}

@router.get("/debug/chat-history/{user_id}")
async def debug_chat_history(user_id: str):
    """
    Debug endpoint để kiểm tra chat history trong database
    """
    try:
        from app.data.database import chat_history_collection
        
        # Lấy tất cả chat history của user
        cursor = chat_history_collection.find({"user_id": user_id}).sort("timestamp", -1)
        chats = list(cursor)
        
        # Chuyển đổi ObjectId thành string
        for chat in chats:
            if "_id" in chat:
                chat["id"] = str(chat["_id"])
                del chat["_id"]
        
        return {
            "user_id": user_id,
            "total_chats": len(chats),
            "chats": chats
        }
        
    except Exception as e:
        logging.exception(f"Lỗi khi debug chat history cho user {user_id}")
        return {"error": f"Lỗi debug: {str(e)}"}

