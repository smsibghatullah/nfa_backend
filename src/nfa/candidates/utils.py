from io import BytesIO
import os
import urllib.parse
from django.conf import settings
from xhtml2pdf import pisa

BASE_WRAPPER = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Advertisement</title>
  <style>
    @page { size: A4; margin: 20mm; }
    body { font-family: DejaVu Sans, sans-serif; font-size: 12px; }
    h1,h2,h3 { margin: 0.4em 0; }
    img { max-width: 100%%; }
    table { border-collapse: collapse; width: 100%%; }
    th, td { border: 1px solid #999; padding: 4px 6px; }
    .ck-content {
      line-height: 1.35;
    }
  </style>
</head>
<body>
  <div class="ck-content">
    %s
  </div>
</body>
</html>
"""

def link_callback(uri, rel):
    uri = urllib.parse.unquote(uri)

    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        return uri

    if not os.path.isfile(path):
        raise Exception(f"Media URI does not exist: {path}")
    return path

def html_to_pdf_bytes(html: str) -> bytes:
    wrapped_html = BASE_WRAPPER % (html or "")
    result = BytesIO()
    status = pisa.CreatePDF(
        src=wrapped_html,
        dest=result,
        encoding='utf-8',
        link_callback=link_callback,
    )
    if status.err:
        raise ValueError("Failed to generate PDF from HTML content.")
    return result.getvalue()
