import os
from datetime import datetime

# make sure a "reports" folder exists one level above
os.makedirs("../reports", exist_ok=True)
report_path = "../reports/data_drift_report.html"

# create a small HTML summary (or you can write your drift stats here)
with open(report_path, "w") as f:
    f.write("<html><body>")
    f.write("<h2>Data Drift Report</h2>")
    f.write(f"<p>Generated at: {datetime.now()}</p>")
    f.write("</body></html>")

print("☑ Drift report generated:", report_path)
