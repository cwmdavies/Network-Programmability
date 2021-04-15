from openpyxl import load_workbook, Workbook


class _excel:
    def __init__(self, name):
        self.name = name
        filename = self.name + ".xlsx"
        workbook = Workbook()
        workbook.save(filename=filename)
    def get_sheets(self):
        workbook = load_workbook(filename=self.name + ".xlsx")
        return workbook.sheetnames
    def add_columns(self, *col_name):
        i = 0
        workbook = load_workbook(filename=self.name + ".xlsx")
        for value in col_name:
            if value not in workbook.sheetnames:
                col_name = workbook.create_sheet(value, i)
                i += 1
            else:
                print(f"{value} already exists in {self.name}. Ignoring column creation!")
        if "Sheet" in workbook.sheetnames:
            del workbook["Sheet"]
        workbook.save(filename=self.name + ".xlsx")

book1 = _excel("Test")