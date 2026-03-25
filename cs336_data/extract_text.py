import resiliparse.extract.html2text
import resiliparse.parse.encoding

def extract_text_from_html_bytes(html_bytes: bytes) -> str | None:
    try:
        encoding = resiliparse.parse.encoding.detect_encoding(html_bytes)
        if not encoding:
            encoding = 'utf-8'
        html_str = html_bytes.decode(encoding, errors='replace')
        return resiliparse.extract.html2text.extract_plain_text(html_str)
    except Exception:
        return None
