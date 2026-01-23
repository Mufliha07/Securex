import os, re, pyotp
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

from app.db.database import (
    init_db, create_user, get_user, save_2fa_secret, enable_2fa
)
from app.twofa import generate_2fa

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@app.on_event("startup")
def startup():
    init_db()

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

def valid_password(password: str):
    if len(password) < 8: return "Password must be at least 8 characters"
    if not re.search(r"[A-Z]", password): return "Password must contain 1 uppercase"
    if not re.search(r"[a-z]", password): return "Password must contain 1 lowercase"
    if not re.search(r"[0-9]", password): return "Password must contain 1 number"
    return None

# ---------------- ROUTES ----------------

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup", response_class=HTMLResponse)
def signup(request: Request, username: str = Form(...), password: str = Form(...)):
    error = valid_password(password)
    if error:
        return templates.TemplateResponse("signup.html", {"request": request, "error": error})

    try:
        create_user(username, hash_password(password))
    except:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username already exists"})

    return RedirectResponse("/", status_code=302)

# ---------------- LOGIN ----------------

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = get_user(username)
    if not user or not verify_password(password, user[2]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    # If 2FA enabled → show OTP input only
    if user[3] == 1:
        return templates.TemplateResponse("otp.html", {"request": request, "username": username})

    # 1FA success → show Enable 2FA
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": username, "show_2fa": True})

# ---------------- ENABLE 2FA ----------------

@app.post("/enable-2fa", response_class=HTMLResponse)
def enable_2fa_route(request: Request, username: str = Form(...)):
    user = get_user(username)
    if not user:
        return {"error": "User not found"}

    secret, qr = generate_2fa(username)
    save_2fa_secret(username, secret)

    return templates.TemplateResponse("otp.html", {"request": request, "qr": qr, "username": username})

# ---------------- VERIFY OTP ----------------

@app.post("/verify-2fa", response_class=HTMLResponse)
def verify_2fa_route(request: Request, username: str = Form(...), otp: str = Form(...)):
    user = get_user(username)
    if not user or not user[4]:
        return templates.TemplateResponse("login.html", {"request": request, "error": "2FA not initialized"})

    totp = pyotp.TOTP(user[4])
    if not totp.verify(otp):
        return templates.TemplateResponse("otp.html", {"request": request, "username": username, "error": "Invalid OTP"})

    enable_2fa(username)
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": username, "show_2fa": False})

# ---------------- RUN ----------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))