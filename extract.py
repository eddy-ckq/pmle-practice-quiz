import fitz
import sys

def extract_text(pdf_path, txt_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + chr(10)
    
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        extract_text(sys.argv[1], sys.argv[2])
    else:
        extract_text("Professional Machine Learning Engineer_with_discussion.pdf", "extracted.txt")
