from fastapi import APIRouter, Depends

from app.auth import get_current_user, AuthedUser
from app.core.engine import load_po_dataframe, answer_question
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, user: AuthedUser = Depends(get_current_user)):
    df = load_po_dataframe(org_id=user.org_id)
    answer = answer_question(df, req.question)
    return ChatResponse(answer=answer)
