
import qrcode
from pathlib import Path

def generate_qr_code(data: str, output_path: str) -> str:
    """Generate QR code image from string data"""
    img = qrcode.make(data)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    return output_path
