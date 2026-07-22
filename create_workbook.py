from io import BytesIO

from polars import DataFrame
from xlsxwriter import Workbook


def create_wb(df_meter_ridings: DataFrame) -> BytesIO:
    buffer = BytesIO()
    wb = Workbook(buffer, {"in_memory": True})
    ws = wb.add_worksheet("Быт")

    df_meter_ridings.write_excel(workbook=wb, worksheet=ws, position="A2")
    next_row = df_meter_ridings.height + 2
    ws.write(next_row, 10, f"Count={df_meter_ridings.height}")  # K column
    wb.close()

    return buffer
