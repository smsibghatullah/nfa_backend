import openpyxl
import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Candidate, JobPost, TestSchedule


def parse_excel_date(value):
    if isinstance(value, datetime.date):
        return value
    value_str = str(value).strip()
    for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(value_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {value_str}")


@staff_member_required
def upload_schedule(request):
    if request.method == 'POST' and request.FILES.get('xlsx_file'):
        file = request.FILES['xlsx_file']

        if not file.name.endswith('.xlsx'):
            messages.error(request, "Invalid file format. Please upload a .xlsx file.")
            return redirect(request.path)

        try:
            wb = openpyxl.load_workbook(file)
            ws = wb.active
        except Exception as e:
            messages.error(request, f"Error reading Excel file: {str(e)}")
            return redirect(request.path)

        expected_columns = [
            'Roll No', 'Name', 'Father Name', 'CNIC', 'Post Applied For', 'Postal Address',
            'Mobile No.', 'Paper', 'Test Date', 'Session', 'Reporting Time', 'Conduct Time'
        ]
        headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
        if headers != expected_columns:
            messages.error(request, "Excel format is invalid. Ensure headers match the required structure.")
            return redirect(request.path)

        for row in ws.iter_rows(min_row=2, values_only=True):
            try:
                roll_no, name, father_name, cnic, post_title, postal_address, mobile_no, paper, test_date, session, reporting_time, conduct_time = row

                test_date = parse_excel_date(test_date)

                code_value = post_title.strip().upper().replace(" ", "_")[:20]

                job_post, _ = JobPost.objects.update_or_create(
                    code=code_value,
                    defaults={"title": post_title}
                )

                candidate, _ = Candidate.objects.update_or_create(
                    roll_no=roll_no,
                    defaults={
                        'name': name,
                        'father_name': father_name,
                        'cnic': cnic,
                        'postal_address': postal_address,
                        'mobile_no': mobile_no
                    }
                )

                TestSchedule.objects.create(
                    candidate=candidate,
                    job_post=job_post,
                    paper=paper,
                    test_date=test_date,
                    session=session,
                    reporting_time=reporting_time,
                    conduct_time=conduct_time
                )

            except Exception as e:
                messages.error(request, f"Error processing row: {row}. Error: {str(e)}")

        messages.success(request, "File uploaded successfully.")
        return redirect(request.path)

    return render(request, 'admin/candidates/upload.html')
