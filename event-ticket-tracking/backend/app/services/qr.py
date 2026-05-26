import segno
import io
import base64

def generate_qr_base64(data: str) -> str:
    """
    Generates a QR code image from the provided data string using segno (pure Python, compile-free),
    saves it as a PNG, and returns the base64-encoded string.
    """
    qr = segno.make(data)
    buffered = io.BytesIO()
    qr.save(buffered, kind="png", scale=10)
    
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"
