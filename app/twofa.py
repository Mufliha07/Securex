import pyotp
import qrcode
import io
import base64

def generate_2fa(username: str):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=username, issuer_name="SecureApp")

    # Generate QR code as base64 image
    qr = qrcode.make(uri)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    img_b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    qr_data = f"data:image/png;base64,{img_b64}"

    return secret, qr_data