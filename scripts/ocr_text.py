# keywords: ocr, picture text, read text from picture, text from image, image to text, scan to text, read screenshot, extract text from image
# desc: Read the text in a picture or screenshot (read text from scan.png; needs pip install pytesseract pillow and the Tesseract program)
# category: media
# usage: read text from <picture>
# rawargs: full
# patterns: \b(read|get|extract)\s+(the\s+)?text\s+(from|in|of)\s+(an?\s+|the\s+|my\s+)?(image|picture|photo|screenshot|scan|pic)\b ;; \b(image|picture|photo|scan)\s+to\s+text\b ;; \bocr\b ;; \btext\s+(from|in|of)\s+\S+\.(png|jpe?g|webp|bmp|tiff?|gif)\b
# priority: 1
import re, shutil
from _lib import args_text, fail, need
from _files import path_arg, unique_path
t = re.sub(r"^\s*(?:please\s+)?(?:(?:read|extract|get|ocr|convert)\b\s*)?(?:the\s+)?(?:text\b\s*)?(?:(?:from|in|of)\b\s*)?(?:(?:an?|the)\b\s*)?(?:(?:image|picture|photo|screenshot|scan|pic)\b(?![\w./-])\s*)?(?:to\s+text\b\s*)?", "", args_text(), flags=re.I).strip()
if not t:
    fail("Usage: read text from <picture>   e.g. read text from scan.png")
src = path_arg(t)
need("PIL", "pillow")
need("pytesseract")
if not shutil.which("tesseract"):
    fail("The Tesseract program is not installed. Windows: github.com/UB-Mannheim/tesseract/wiki  |  Mac: brew install tesseract  |  Linux: sudo apt install tesseract-ocr")
from PIL import Image
import pytesseract
try:
    with Image.open(src) as im:
        text = pytesseract.image_to_string(im)
except Exception as ex:
    fail(f"Could not read that picture: {type(ex).__name__}")
if not text.strip():
    fail("No text found in that picture.")
out = unique_path(src.with_suffix(".txt"))
out.write_text(text, encoding="utf-8")
print(text.strip()[:1500])
print(f"\nSaved all {len(text):,} characters to {out}")
