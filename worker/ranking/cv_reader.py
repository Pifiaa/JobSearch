import os
import pdfplumber
from core.logger import log


CV_PATH = os.environ.get("CV_PATH", "/app/data/cv.pdf")


def read_cv_text() -> str:
    if not os.path.exists(CV_PATH):
        log(f"[ranking] CV no encontrado en {CV_PATH}")
        return ""

    text = ""
    with pdfplumber.open(CV_PATH) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    log(f"[ranking] CV leído — {len(text)} caracteres")
    return text