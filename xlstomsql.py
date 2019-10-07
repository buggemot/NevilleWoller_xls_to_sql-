import pymysql.cursors
import xlrd
import pdb
from datetime import datetime
import time
import os
import re

def run_sql(connection, sql_query, values = False, close_connection = False):
    try:
        with connection.cursor() as cursor:
            if values:
                cursor.execute(sql_query, values)
            else:
                cursor.execute(sql_query)
        connection.commit()
    except Exception as e:
        print(e)
    finally:
        if close_connection:
            connection.close()

def from_excel_to_sql(connection, sheet, table_name):
#`Supplier_Name`, `Order_Date_DD_MM_YYYY`, `Purchase_Order_No`, `Tax_Invoice_No`, `Tax_Invoice_Issue_Date`, `Despatch_Date`, `Hospital`, `Contractor_Product_Code`, `Manufacturer_Product_Code`, `Product_Description`, `Brand_Name`, `GTIN_Code`, `Procedure_Type_if_applicable`, `SESLHD_Category_Tier_1`, `SESLHD_Category_Tier_2`, `SESLHD_Category_Tier_3`, `SESLHD_Category_Tier_4`, `Unit_of_Measure_UOM`,`Quantity_per_UOM`, `Unit_Cost_per_UOM_Ex_GST`, `Number_of_Units_Purchased_UOM`, `Total_Cost_Ex_GST`, `Comments_Optional`

    query = """INSERT INTO `{}` (`Supplier_Name`, `Order_Date_DD_MM_YYYY`, `Purchase_Order_No`, `Tax_Invoice_No`, `Tax_Invoice_Issue_Date`, `Despatch_Date`, `Hospital`, `Contractor_Product_Code`, `Manufacturer_Product_Code`, `Product_Description`, `Brand_Name`, `GTIN_Code`, `Procedure_Type_if_applicable`, `SESLHD_Category_Tier_1`, `SESLHD_Category_Tier_2`, `SESLHD_Category_Tier_3`, `SESLHD_Category_Tier_4`, `Unit_of_Measure_UOM`,`Quantity_per_UOM`, `Unit_Cost_per_UOM_Ex_GST`, `Number_of_Units_Purchased_UOM`, `Total_Cost_Ex_GST`, `Comments_Optional`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""".format(table_name)

    for i in range(10, sheet.nrows):
        no = sheet.cell(i, 1)
        Supplier_Name = sheet.cell(i, 2).value
        Order_Date = sheet.cell(i, 3).value
        if isinstance(Order_Date, float):
            Order_Date = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(Order_Date) - 2).strftime("%#d/%#m/%Y")

        Purchase_Order_No = sheet.cell(i, 4).value
        if isinstance(Purchase_Order_No, float):
             Purchase_Order_No = str(Purchase_Order_No)[:-2]

        Tax_Invoice_No = sheet.cell(i, 5).value

        Tax_Invoice_Issue_Date = sheet.cell(i, 6).value
        if isinstance(Tax_Invoice_Issue_Date, float):
            try:
                Tax_Invoice_Issue_Date= datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(Tax_Invoice_Issue_Date) - 2).strftime("%#d/%#m/%Y")
            except Exception as e:
                print('')

        Despatch_Date = sheet.cell(i, 7).value
        if isinstance(Despatch_Date, float):
            try:
                Despatch_Date = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(Despatch_Date) - 2).strftime("%#d/%#m/%Y")
            except Exception as e:
                Despatch_Date = 'N/A'
        Hospital = sheet.cell(i, 8).value
        Contractor_Product_Code = sheet.cell(i, 9).value
        Manufacturer_Product_Code = sheet.cell(i, 10).value
        Product_Description = sheet.cell(i, 11).value
        Brand_Name = sheet.cell(i, 12).value
        GTIN_Code = sheet.cell(i, 13).value
        Procedure_Type = sheet.cell(i, 14).value
        SESLHD_Category_Tier_1 = sheet.cell(i, 15).value
        SESLHD_Category_Tier_2 = sheet.cell(i, 16).value
        SESLHD_Category_Tier_3 = sheet.cell(i, 17).value
        SESLHD_Category_Tier_4 = sheet.cell(i, 18).value
        Unit_of_Measure = sheet.cell(i, 19).value
        Quantity_per_UOM = sheet.cell(i, 20).value
        Unit_Cost_per_UOM = sheet.cell(i, 21).value
        if isinstance(Unit_Cost_per_UOM, float):
            Unit_Cost_per_UOM = round(Unit_Cost_per_UOM, 2)
        Number_of_Units_Purchased_UOM = sheet.cell(i, 22).value
        Total_Cost_ex_GST = sheet.cell(i, 23).value
        Comments = sheet.cell(i, 24).value

        values = (Supplier_Name, Order_Date, Purchase_Order_No, Tax_Invoice_No, Tax_Invoice_Issue_Date, Despatch_Date, Hospital, Contractor_Product_Code, Manufacturer_Product_Code,Product_Description, Brand_Name, GTIN_Code, Procedure_Type, SESLHD_Category_Tier_1, SESLHD_Category_Tier_2, SESLHD_Category_Tier_3, SESLHD_Category_Tier_4, Unit_of_Measure, Quantity_per_UOM, Unit_Cost_per_UOM, Number_of_Units_Purchased_UOM, Total_Cost_ex_GST, Comments)
        #pdb.set_trace()

        if len([i for i in values if i]) <= 4:
            break

        run_sql(connection, query, values)

def main():
#folder of excel files    
    dir_cardio_excel_files = r"e:\upwork\2019-10-07\2019\Cardio\Build Data"
    dir_trauma_excel_files = r"e:\upwork\2019-10-07\2019\Trauma\Build Data"
    cardio_excel_files = [i for i in os.listdir(dir_cardio_excel_files) if i.endswith('xlsx')]
    trauma_excel_files = [i for i in os.listdir(dir_trauma_excel_files) if i.endswith('xlsx')]
    sheet_name = "1. Usage Report"

# Connect to the database
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='sheerwood1522',
                                 db='zudello',
                                 #charset='utf8mb4',
                                 #cursorclass=pymysql.cursors.DictCursor,
                                 )

    #cardio_table_name = "cardio-{}".format(time.strftime('%Y-%m-%d'))
    table_name = 'invoices'
    sql_delete_table = """DROP TABLE IF EXISTS `{}`;""".format(table_name)
    run_sql(connection, sql_delete_table)

    sql_create_table = """CREATE TABLE `{}` (
  `Supplier_Name` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `Order_Date_DD_MM_YYYY` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `Purchase_Order_No` varchar(23) CHARACTER SET utf8 DEFAULT NULL,
  `Tax_Invoice_No` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `Tax_Invoice_Issue_Date` varchar(10) CHARACTER SET utf8 DEFAULT NULL,
  `Despatch_Date` varchar(30) CHARACTER SET utf8 DEFAULT NULL,
  `Hospital` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `Contractor_Product_Code` varchar(16) CHARACTER SET utf8 DEFAULT NULL,
  `Manufacturer_Product_Code` varchar(50) CHARACTER SET utf8 DEFAULT NULL,
  `Product_Description` varchar(176) CHARACTER SET utf8 DEFAULT NULL,
  `Brand_Name` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `GTIN_Code` varchar(25) CHARACTER SET utf8 DEFAULT NULL,
  `Procedure_Type_if_applicable` varchar(30) CHARACTER SET utf8 DEFAULT NULL,
  `SESLHD_Category_Tier_1` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `SESLHD_Category_Tier_2` varchar(250) CHARACTER SET utf8 DEFAULT NULL,
  `SESLHD_Category_Tier_3` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `SESLHD_Category_Tier_4` varchar(100) CHARACTER SET utf8 DEFAULT NULL,
  `Unit_of_Measure_UOM` varchar(20) CHARACTER SET utf8 DEFAULT NULL,
  `Quantity_per_UOM` int(11) DEFAULT NULL,
  `Unit_Cost_per_UOM_Ex_GST` decimal(13,8) DEFAULT NULL,
  `Number_of_Units_Purchased_UOM` decimal(4,1) DEFAULT NULL,
  `Total_Cost_Ex_GST` decimal(7,2) DEFAULT NULL,
  `Comments_Optional` varchar(57) CHARACTER SET utf8 DEFAULT NULL,
  `Normalized_Contractor_Product_Code` varchar(255) DEFAULT NULL,
  `Normalized_Manufacturer_Product_Code` varchar(255) DEFAULT NULL,
  KEY `Supplier_Name` (`Supplier_Name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;""".format(table_name)

    run_sql(connection, sql_create_table)

#    for f in cardio_excel_files:
#        print(f)
#        excel =  xlrd.open_workbook(os.path.join(dir_cardio_excel_files, f))
#        sheet = excel.sheet_by_name(sheet_name)
#        from_excel_to_sql(connection, sheet, table_name)

    for f in trauma_excel_files[::-1]:
        print(f)
        excel =  xlrd.open_workbook(os.path.join(dir_trauma_excel_files, f))
        sheet = excel.sheet_by_name(sheet_name)
        from_excel_to_sql(connection, sheet, table_name)

#    f = trauma_excel_files[::-1][0]
#    print(f)
#    excel =  xlrd.open_workbook(os.path.join(dir_trauma_excel_files, f))
#    sheet = excel.sheet_by_index(1)
#    from_excel_to_sql(connection, sheet, table_name)

if __name__ == "__main__":
    main()

