from openpyxl import *


class _excel:
    def __init__(self, name):
        self.name = name
        filename = self.name + ".xlsx"
        workbook = Workbook()
        workbook.save(filename=filename)
    def get_sheet(self):
        workbook = load_workbook(filename=self.name + ".xlsx")
        return workbook.sheetnames
    def add_col(self, col_name):
        workbook = load_workbook(filename=self.name + ".xlsx")
        col_name = workbook.create_sheet(col_name, 0)
        workbook.save(filename=self.name + ".xlsx")

sheet1 = _excel("Test")