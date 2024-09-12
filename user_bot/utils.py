import qrcode
import os

def generate_qr_code(data):
    file_path = f'/tmp/{data}.png'
    img = qrcode.make(data)
    img.save(file_path)
    return file_path

def clean_up_qr_code(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
