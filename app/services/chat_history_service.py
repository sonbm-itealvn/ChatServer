from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.data.database import chat_history_collection
import logging

logger = logging.getLogger(__name__)

class ChatHistoryService:
    @staticmethod
    def save_chat(
        conversation_id: str,
        user_id: str,
        question: str,
        answer: str,
        agent: str,
        context: Dict[str, Any] = None,
        events: List[Dict[str, Any]] = None
    ) -> bool:
        """
        Lưu một cuộc hội thoại vào database
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
            logger.error(f"Lỗi khi lưu chat history: {e}")
            return False

    @staticmethod
    def get_user_history(
        user_id: str, 
        limit: int = 50, 
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Lấy lịch sử chat của user với filter theo thời gian
        """
        try:
            query = {"user_id": user_id}
            
            # Thêm filter theo thời gian nếu có
            if start_date or end_date:
                time_filter = {}
                if start_date:
                    time_filter["$gte"] = start_date
                if end_date:
                    time_filter["$lte"] = end_date
                query["timestamp"] = time_filter
            
            cursor = chat_history_collection.find(query).sort("timestamp", -1).skip(offset).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Lỗi khi lấy user history: {e}")
            return []

    @staticmethod
    def get_conversation_history(conversation_id: str) -> List[Dict[str, Any]]:
        """
        Lấy toàn bộ lịch sử của một conversation
        """
        try:
            cursor = chat_history_collection.find(
                {"conversation_id": conversation_id}
            ).sort("timestamp", 1)
            return list(cursor)
        except Exception as e:
            logger.error(f"Lỗi khi lấy conversation history: {e}")
            return []

    @staticmethod
    def get_user_statistics(user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Lấy thống kê chat của user trong N ngày gần đây
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Tổng số tin nhắn
            total_messages = chat_history_collection.count_documents({
                "user_id": user_id,
                "timestamp": {"$gte": start_date}
            })
            
            # Số conversation
            conversations = chat_history_collection.distinct("conversation_id", {
                "user_id": user_id,
                "timestamp": {"$gte": start_date}
            })
            
            # Agent được sử dụng nhiều nhất
            pipeline = [
                {"$match": {"user_id": user_id, "timestamp": {"$gte": start_date}}},
                {"$group": {"_id": "$agent", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            top_agents = list(chat_history_collection.aggregate(pipeline))
            
            # Tin nhắn theo ngày
            daily_pipeline = [
                {"$match": {"user_id": user_id, "timestamp": {"$gte": start_date}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            daily_stats = list(chat_history_collection.aggregate(daily_pipeline))
            
            return {
                "total_messages": total_messages,
                "total_conversations": len(conversations),
                "top_agents": top_agents,
                "daily_stats": daily_stats,
                "period_days": days
            }
        except Exception as e:
            logger.error(f"Lỗi khi lấy user statistics: {e}")
            return {}

    @staticmethod
    def delete_user_history(user_id: str) -> bool:
        """
        Xóa toàn bộ lịch sử chat của user
        """
        try:
            result = chat_history_collection.delete_many({"user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Lỗi khi xóa user history: {e}")
            return False

    @staticmethod
    def delete_conversation_history(conversation_id: str) -> bool:
        """
        Xóa lịch sử của một conversation
        """
        try:
            result = chat_history_collection.delete_many({"conversation_id": conversation_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Lỗi khi xóa conversation history: {e}")
            return False

    @staticmethod
    def search_chat_history(
        user_id: str,
        search_term: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm trong lịch sử chat của user
        """
        try:
            # Tìm kiếm trong cả question và answer
            query = {
                "user_id": user_id,
                "$or": [
                    {"question": {"$regex": search_term, "$options": "i"}},
                    {"answer": {"$regex": search_term, "$options": "i"}}
                ]
            }
            
            cursor = chat_history_collection.find(query).sort("timestamp", -1).skip(offset).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm chat history: {e}")
            return [] 