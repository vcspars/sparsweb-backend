from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

from services.chatbot_service import ChatbotService

router = APIRouter()
chatbot_service = ChatbotService()

class ChatMessage(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None

class ChatResponse(BaseModel):
    response: str
    success: bool

@router.post("/chatbot", response_model=ChatResponse)
async def chat_with_bot(chat_message: ChatMessage):
    """Handle chatbot messages"""
    try:
        if not chat_message.message or not chat_message.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty"
            )
        
        response = await chatbot_service.get_response(
            chat_message.message,
            chat_message.conversation_history
        )
        
        return ChatResponse(
            response=response,
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )

