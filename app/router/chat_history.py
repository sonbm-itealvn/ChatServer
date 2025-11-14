from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime
from app.services.chat_history_service import ChatHistoryService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history", tags=["Chat History"])

@router.get("/{user_id}")
async def get_user_chat_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    try:
        # Parse dates if provided
        start_dt = None
        end_dt = None
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                # Set to end of day
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
        
        db_chats = ChatHistoryService.get_user_history(
            user_id=user_id,
            limit=limit,
            offset=offset,
            start_date=start_dt,
            end_date=end_dt
        )
        
        if not db_chats:
            return {
                "history": [],
                "total": 0,
                "has_more": False,
                "user_id": user_id
            }
        
        # Convert to display format
        history = []
        for chat in db_chats:
            history.append({
                "role": "user",
                "content": chat.get("question", ""),
                "timestamp": chat.get("timestamp", None),
                "conversation_id": chat.get("conversation_id", ""),
                "agent": chat.get("agent", "")
            })
            history.append({
                "role": "assistant",
                "content": chat.get("answer", ""),
                "timestamp": chat.get("timestamp", None),
                "conversation_id": chat.get("conversation_id", ""),
                "agent": chat.get("agent", "")
            })
        
        # Reverse to show oldest first
        history.reverse()
        
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
            "total": len(history),
            "has_more": len(db_chats) == limit,
            "user_id": user_id,
            "limit": limit,
            "offset": offset,
            "reply": main_reply,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.exception(f"Error getting chat history for user {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/conversation/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    try:
        db_chats = ChatHistoryService.get_conversation_history(conversation_id)
        
        if not db_chats:
            return {
                "history": [],
                "conversation_id": conversation_id,
                "total_messages": 0
            }
        
        # Convert to display format
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
        logger.exception(f"Error getting conversation history for {conversation_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/{user_id}/statistics")
async def get_user_statistics(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    try:
        stats = ChatHistoryService.get_user_statistics(user_id, days)
        
        if not stats:
            return {
                "user_id": user_id,
                "total_messages": 0,
                "total_conversations": 0,
                "top_agents": [],
                "daily_stats": [],
                "period_days": days
            }
        
        return {
            "user_id": user_id,
            **stats
        }
        
    except Exception as e:
        logger.exception(f"Error getting statistics for user {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user/{user_id}/search")
async def search_chat_history(
    user_id: str,
    q: str = Query(..., description="Search term"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    try:
        if not q.strip():
            raise HTTPException(status_code=400, detail="Search term cannot be empty")
        
        db_chats = ChatHistoryService.search_chat_history(
            user_id=user_id,
            search_term=q,
            limit=limit,
            offset=offset
        )
        
        if not db_chats:
            return {
                "results": [],
                "total": 0,
                "search_term": q,
                "user_id": user_id
            }
        
        # Convert to display format
        results = []
        for chat in db_chats:
            results.append({
                "role": "user",
                "content": chat.get("question", ""),
                "timestamp": chat.get("timestamp", None),
                "conversation_id": chat.get("conversation_id", ""),
                "agent": chat.get("agent", "")
            })
            results.append({
                "role": "assistant",
                "content": chat.get("answer", ""),
                "timestamp": chat.get("timestamp", None),
                "conversation_id": chat.get("conversation_id", ""),
                "agent": chat.get("agent", "")
            })
        
        # Tạo reply chính từ tin nhắn cuối cùng của assistant
        main_reply = ""
        if results:
            for msg in reversed(results):
                if msg["role"] == "assistant":
                    main_reply = msg["content"]
                    break
        
        # Tạo metadata để hỗ trợ requires_support_form
        metadata = {}
        if main_reply and ("support" in main_reply.lower() or "hỗ trợ" in main_reply.lower()):
            metadata["requires_support_form"] = True
        
        return {
            "results": results,
            "total": len(results),
            "search_term": q,
            "user_id": user_id,
            "limit": limit,
            "offset": offset,
            "reply": main_reply,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.exception(f"Error searching chat history for user {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{user_id}")
async def delete_user_history(user_id: str):
    try:
        success = ChatHistoryService.delete_user_history(user_id)
        
        if success:
            return {
                "message": "User chat history deleted successfully",
                "user_id": user_id
            }
        else:
            raise HTTPException(status_code=404, detail="User not found or no history to delete")
            
    except Exception as e:
        logger.exception(f"Error deleting chat history for user {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/conversation/{conversation_id}")
async def delete_conversation_history(conversation_id: str):
    try:
        success = ChatHistoryService.delete_conversation_history(conversation_id)
        
        if success:
            return {
                "message": "Conversation history deleted successfully",
                "conversation_id": conversation_id
            }
        else:
            raise HTTPException(status_code=404, detail="Conversation not found or no history to delete")
            
    except Exception as e:
        logger.exception(f"Error deleting conversation history for {conversation_id}")
        raise HTTPException(status_code=500, detail="Internal server error") 