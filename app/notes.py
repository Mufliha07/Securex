# app/notes.py
from fastapi import APIRouter, Depends, HTTPException
from app.utils import verify_access_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Temporary in-memory storage
notes_db = []

@router.post("/notes")
def create_note(
    content: str,
    token: str = Depends(oauth2_scheme)
):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    notes_db.append({
        "user": payload["sub"],
        "content": content
    })

    return {"message": "Note saved successfully"}

@router.get("/notes")
def get_notes(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_notes = [
        note["content"]
        for note in notes_db
        if note["user"] == payload["sub"]
    ]

    return {"notes": user_notes}