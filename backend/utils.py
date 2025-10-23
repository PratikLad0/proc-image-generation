import os

def ensure_dirs():
    dirs = ["app/static/uploads", "app/static/outputs", "app/static/temp"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
