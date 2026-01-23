<<<<<<< HEAD
# app/utils.py
import pyotp
import qrcode
import io
from passlib.context import CryptContext

# -------- Password hashing --------
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

# -------- Password validation --------
def validate_password(password: str):
    """
    Raises ValueError if password does not meet requirements:
    - At least 8 characters
    - At least 1 uppercase
    - At least 1 lowercase
    - At least 1 digit
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least 1 uppercase letter")
    if not any(c.islower() for c in password):
        raise ValueError("Password must contain at least 1 lowercase letter")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least 1 number")

# -------- 2FA (TOTP) --------
def generate_totp_secret():
    return pyotp.random_base32()

def get_totp_uri(secret, username, issuer_name="SecurexApp"):
    return pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer_name)

def generate_qr_code(uri):
    """
    Generates a PNG QR code in-memory for the TOTP URI
    """
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
=======
import hashlib
from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "securex-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password, hashed_password):
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def validate_password(password: str):
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")
>>>>>>> 1b6ef31a93ee65efef2c1777e29ba8e2a9f931ac
