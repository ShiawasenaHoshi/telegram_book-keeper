import os

from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Alignment

from app.report.styles import BOLD, r_bottom_thick, r_thick, bottom_thick, thin, adjust_columns_size, top_thick, \
    r_top_corner_thick
from config import Config


def generate_report(data, sheet_name="Выписка"):
    wb = Workbook(write_only=True)

    titles = ["Дата", "Сумма", "В валюте", "Описание", "Категория"]
    ws = wb.create_sheet(sheet_name)
    adjust_columns_size(ws)
    append_header(ws, titles)
    append_multiline(ws, data)
    return save_workbook(wb)

def save_workbook(workbook):
    path = os.path.join(Config.TEMP_FOLDER, f'report.xlsx')
    workbook.save(path)
    return path

def append_header(ws, titles):
    cells = []
    for i in range(len(titles)):
        cell = header_cell(ws, titles[i])
        cell.border = top_thick
        cell.alignment = Alignment(horizontal='center', vertical='bottom')
        if i == len(titles) - 1:
            cell.border = r_top_corner_thick
        cells.append(cell)

    ws.append(cells)


def header_cell(ws, data):
    cell = WriteOnlyCell(ws, value=data)
    cell.font = BOLD
    return cell

def append_multiline(ws, data):
    for line in data:
        cells = []
        last_index = len(line) - 1
        for i in range(0, len(line)):
            cell = WriteOnlyCell(ws, value=line[i])
            cell.alignment = Alignment(horizontal='center', vertical='bottom')
            if i == last_index:
                cell.border = r_thick
            else:
                cell.border = thin
            cells.append(cell)
        ws.append(cells)



