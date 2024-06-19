from io import BytesIO
import openpyxl
import openpyxl.workbook
import pandas as pd

def create_excel_object(records: dict):
    buffer = BytesIO()
    df = pd.DataFrame(records)
    df.to_excel(buffer, index=False)

    workbook = openpyxl.load_workbook(buffer)
    worksheet = workbook.active

    dims = {}
    for row in worksheet.rows:
        for cell in row:
            if cell.value:
                dims[cell.column_letter] = max((dims.get(cell.column_letter, 0), len(str(cell.value))))

    for col, value in dims.items():
        worksheet.column_dimensions[col].width = value
    final_buffer = BytesIO()
    workbook.save(final_buffer)

    return final_buffer

def adjust_excel_column_widths(workbook: openpyxl.Workbook) -> openpyxl.Workbook:
    for sheetname in workbook.sheetnames:
        worksheet = workbook[sheetname]

        dims = {}
        for row in worksheet.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column_letter] = max((dims.get(cell.column_letter, 0), len(str(cell.value))))

        for col, value in dims.items():
            worksheet.column_dimensions[col].width = value
    return workbook

