from pathlib import Path
import fitz


def exract_text_from_pdf(file_path: Path):
    pages = []
    with fitz.open(file_path) as doc:
        for page in doc:
            pages.append(page.get_text())

    text = "\n".join(pages)

    return text


# if __name__ == "__main__":
#     from backend.config import AppConfig

#     config = AppConfig()
#     text = exract_text_from_pdf(r"/home/leapfrog/final_mlops_project/JitenRaiCV.pdf")
#     chunks = split_text_into_chunks(text, config)
#     print(chunks)
