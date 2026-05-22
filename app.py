from flask import Flask, request, send_file, render_template_string
from pathlib import Path
import tempfile
import os
import traceback

from aircon_check_final import reconcile

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

UPLOAD_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Aircon Rental Checker</title>
</head>
<body style="font-family: Arial; max-width: 700px; margin: 50px auto;">
    <h1>Aircon Rental Cross-Checker</h1>

    <p>Upload all Form F PDFs and the landlord Excel .xlsx file together.</p>

    <form action="/run" method="post" enctype="multipart/form-data">
        <input type="file" name="files" multiple required>
        <br><br>
        <button type="submit">Run Checker</button>
    </form>

    <p><b>Required:</b> At least one PDF and exactly one .xlsx file.</p>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(UPLOAD_PAGE)

@app.route("/run", methods=["POST"])
def run_checker():
    uploaded_files = request.files.getlist("files")

    if not uploaded_files:
        return "No files uploaded.", 400

    work_dir = tempfile.mkdtemp()

    pdf_count = 0
    xlsx_count = 0

    for file in uploaded_files:
        if not file.filename:
            continue

        filename = Path(file.filename).name
        lower_name = filename.lower()

        if lower_name.endswith(".pdf"):
            pdf_count += 1
        elif lower_name.endswith(".xlsx"):
            xlsx_count += 1
        else:
            continue

        save_path = os.path.join(work_dir, filename)
        file.save(save_path)

    if pdf_count == 0:
        return "Please upload at least one PDF file.", 400

    if xlsx_count == 0:
        return "Please upload the landlord Excel .xlsx file.", 400

    if xlsx_count > 1:
        return "Please upload only one landlord Excel .xlsx file.", 400

    try:
        summary, output_path = reconcile(work_dir)

        return send_file(
            output_path,
            as_attachment=True,
            download_name=Path(output_path).name,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception:
        error_details = traceback.format_exc()
        return f"<h2>Reconciliation failed</h2><pre>{error_details}</pre>", 500
