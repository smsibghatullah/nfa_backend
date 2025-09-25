from io import BytesIO
import os
import urllib.parse
from django.conf import settings
from xhtml2pdf import pisa
from datetime import date

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


QUALIFICATION_ORDER = {
    "matric": 1,
    "intermediate": 2,
    "bachelors": 3,
    "masters": 4,
}

def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def get_highest_qualification(profile):
    degrees = [edu.degree for edu in profile.educations.all()]
    if not degrees:
        return None
    return max(degrees, key=lambda d: QUALIFICATION_ORDER.get(d, 0))

def calculate_total_experience(profile):
    total_days = 0
    for work in profile.work_histories.all():
        start = work.start_date
        end = work.end_date or date.today()
        total_days += (end - start).days
        
    total_years = round(total_days / 365, 1)
    return total_years

