import sys
try:
    import pypdf
except ImportError:
    print("PyPDF2 is not installed. Please install it by running: pip install pypdf")
    sys.exit(1)

import os

def extract_text_from_pdf(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    try:
        with open(file_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            print(text)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        extract_text_from_pdf(sys.argv[1])
    else:
        print("Please provide the path to the PDF file as a command-line argument.")
