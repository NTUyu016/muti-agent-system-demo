
import sys
import importlib.util

def try_extract(path):
    # Try pypdf (newer)
    if importlib.util.find_spec("pypdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return "SUCCESS: pypdf", text
        except Exception as e:
            return f"FAIL: pypdf error {e}", ""

    # Try PyPDF2 (older)
    if importlib.util.find_spec("PyPDF2"):
        try:
            import PyPDF2
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return "SUCCESS: PyPDF2", text
        except Exception as e:
            return f"FAIL: PyPDF2 error {e}", ""
            
    return "FAIL: No suitable library found (pypdf, PyPDF2)", ""

if __name__ == "__main__":
    file_path = r"c:\Users\20151\OneDrive\桌面\tsmc\tsmc_hackthon\Report_agent\2026 TSMC CareerHack_ 智慧產業分析 Multi-Agent System 架構.pdf"
    status, text = try_extract(file_path)
    with open("extracted_content.txt", "w", encoding="utf-8") as f:
        f.write(status + "\n")
        f.write("-" * 20 + "\n")
        f.write(text)
    print("Done writing to extracted_content.txt")
