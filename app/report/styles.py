import string

from openpyxl.styles import Font, Border, Side


def num2col(col):
    return string.ascii_letters[col - 1].upper()


def adjust_columns_size(ws):
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 12
    ws.column_dimensions["D"].width = 40
    ws.column_dimensions["E"].width = 20


BOLD = Font(bold=True)
thin = Border(left=Side(style='thin'),
              right=Side(style='thin'),
              top=Side(style='thin'),
              bottom=Side(style='thin'))

top_thick = Border(left=Side(style='thin'),
                   right=Side(style='thin'),
                   top=Side(style='thick'),
                   bottom=Side(style='thin'))

r_top_corner_thick = Border(left=Side(style='thin'),
                            right=Side(style='thick'),
                            top=Side(style='thick'),
                            bottom=Side(style='thin'))

r_thick = Border(left=Side(style='thin'),
                 right=Side(style='thick'),
                 top=Side(style='thin'),
                 bottom=Side(style='thin'))

r_bottom_thick = Border(left=Side(style='thin'),
                        right=Side(style='thick'),
                        top=Side(style='thin'),
                        bottom=Side(style='thick'))

bottom_thick = Border(left=Side(style='thin'),
                      right=Side(style='thin'),
                      top=Side(style='thin'),
                      bottom=Side(style='thick'))
