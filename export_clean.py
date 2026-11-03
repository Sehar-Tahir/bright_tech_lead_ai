import csv
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

CSV_IN = "bright_tech_qualified_leads.csv"
EXCEL_OUT = "Bright_Tech_Clean_Leads.xlsx"

# Sirf 8 sabse ahem aur readable columns jo client ko dekhne hain
CORE_COLUMNS = [
    ("company_name", "Company Name"),
    ("official_domain", "Website / Domain"),
    ("country", "Country"),
    ("industry", "Industry"),
    ("relevant_service", "Bright Tech Service Fit"),
    ("total_score", "Score (100)"),
    ("priority_band", "Priority Band"),
    ("official_contact_route", "Verified Contact Route"),
    ("review_status", "Human Review Status")
]

def generate_clean_excel():
    if not os.path.exists(CSV_IN):
        print(f"Error: '{CSV_IN}' nahi mili!")
        return

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Qualified Prospects"
    ws.views.sheetView[0].showGridLines = True

    # Styling definitions
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid") # Dark Blue
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF") # White Bold
    data_font = Font(name="Calibri", size=10)
    center_align = Alignment(horizontal="center", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")
    
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    # 1. Write Headers
    header_labels = [label for _, label in CORE_COLUMNS]
    ws.append(header_labels)
    
    for col_idx in range(1, len(header_labels) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align
        cell.border = thin_border
    ws.row_dimensions[1].height = 28

    # 2. Read and Write Clean Data
    with open(CSV_IN, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_idx, row in enumerate(reader, start=2):
            row_values = []
            for col_key, _ in CORE_COLUMNS:
                val = row.get(col_key, "")
                if col_key == "total_score":
                    try: val = int(val)
                    except: pass
                row_values.append(val)
            ws.append(row_values)

            # Styling data cells
            for col_idx in range(1, len(row_values) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font = data_font
                cell.border = thin_border
                
                # Alignments & Highlights
                if col_idx in [3, 6, 7, 9]:  # Country, Score, Band, Review
                    cell.alignment = center_align
                else:
                    cell.alignment = left_align
                    
                # Score Highlighting (Green for 80+)
                if col_idx == 6 and isinstance(cell.value, int) and cell.value >= 80:
                    cell.fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
                    cell.font = Font(name="Calibri", size=10, bold=True, color="166534")

            ws.row_dimensions[row_idx].height = 22

    # 3. Auto-fit column widths
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                if len(str(cell.value)) > max_len:
                    max_len = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(EXCEL_OUT)
    print("=" * 60)
    print(f"SUCCESS: Clean & Professional Excel created: '{EXCEL_OUT}'")
    print("Headers are BOLD with styling, and only core columns are included.")
    print("=" * 60)

if __name__ == "__main__":
    generate_clean_excel()