import re
from dataclasses import dataclass, asdict
from typing import List, Optional

import pdfplumber


@dataclass
class DocumentChunk:
    text: str
    metadata: dict


def read_file(file_path: str) -> str:
    """
    Reads a PDF file and extracts its raw text content.
    """
    text_parts = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)

def clean_text(text: str) -> str:
    """
    Cleans text by normalizing whitespace and trimming leading/trailing spaces.
    """
    # Replace multiple whitespace with single space and trim
    text = re.sub(r"\s+", " ", text)
    return text.strip() # trims the strings


def parse_constitution(text: str) -> List[DocumentChunk]:
    """
    Parses constitution text into article-level chunks with metadata:
    section, chapter, article number, article title.
    """

    # Normalize line endings
    # \r\n means carriage return + newline (Windows), \r means carriage return (old Mac), \n means newline (Unix/Linux)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Match SECTION, Chapter, Article headings
    heading_pattern = re.compile(
        r"(?P<section>SECTION\s+[IVXLCDM]+:\s+.+)"
        r"|(?P<chapter>Chapter\s+[IVXLCDM]+\.\s+.+)"
        r"|(?P<article>Article\s+(?P<article_num>\d+)\.\s+(?P<article_title>.+))"
    )

    matches = list(heading_pattern.finditer(text))

    chunks = []

    current_section: Optional[str] = None
    current_chapter: Optional[str] = None

    article_start = None
    article_number = None
    article_title = None
    article_section = None
    article_chapter = None

    for i, match in enumerate(matches):
        if match.group("section"):
            current_section = clean_text(match.group("section"))

        elif match.group("chapter"):
            current_chapter = clean_text(match.group("chapter"))

        elif match.group("article"):
            # Save previous article before starting new one
            if article_start is not None:
                article_end = match.start()
                article_text = clean_text(text[article_start:article_end])

                chunks.append(
                    DocumentChunk(
                        text=article_text,
                        metadata={
                            "section": article_section,
                            "chapter": article_chapter,
                            "article_number": article_number,
                            "article_title": article_title,
                            "source": "constitution_en-1-10.pdf",
                        },
                    )
                )

            # Start new article
            article_start = match.start()
            article_number = int(match.group("article_num"))
            article_title = clean_text(match.group("article_title"))
            article_section = current_section
            article_chapter = current_chapter

    # Save final article
    if article_start is not None:
        article_text = clean_text(text[article_start:])

        chunks.append(
            DocumentChunk(
                text=article_text,
                metadata={
                    "section": article_section,
                    "chapter": article_chapter,
                    "article_number": article_number,
                    "article_title": article_title,
                    "source": "constitution_en-1-10.pdf",
                },
            )
        )

    return chunks

def main():
    file_path = "./data/constitution_en-1-10.pdf"
    text = read_file(file_path)
    chunks = parse_constitution(text)

    for chunk in chunks:
        print("-" * 80)
        print(asdict(chunk))
        print("-" * 80)

if __name__ == "__main__":
    main()