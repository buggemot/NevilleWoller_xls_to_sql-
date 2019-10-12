import os
import json
import pdb
import pymysql.cursors
from ftplib import FTP
from datetime import datetime


def is_file_changed(previous_time_of_file, current_time_of_file):

    d_previous_time_of_file = datetime.strptime(previous_time_of_file, '%b %d %H:%M %Y')
    d_current_time_of_file = datetime.strptime(current_time_of_file, '%b %d %H:%M %Y')

    return d_previous_time_of_file != d_current_time_of_file

def save_result_of_current_connection(result_of_connection, filename):

    try:
        fp = open(filename, 'w')
        json.dump(result_of_connection, fp)
        fp.close()
    except Exception as e:
        print("Error of saving result of connection with ftp: {}".format(e))
    return

def load_result_of_previous_connection(file_result):

    d_result_of_previous_connection = {}
    try:
        fp = open(file_result, 'r')
        d_result_of_previous_connection = json.load(fp)
        fp.close()
    except Exception as e:
        print("Error of load previous result from file: {}".format(e))

    return d_result_of_previous_connection

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

def load_csv_file_to_mysql(cfg_mysql, products_file):

    try:
        connection = pymysql.connect(host=cfg_mysql['host'],
                 user=cfg_mysql['user'],
                 password=cfg_mysql['password'],
                 db=cfg_mysql['db'],
                 #charset='utf8mb4',
                 #cursorclass=pymysql.cursors.DictCursor,
                 )
    except Exception as e:
        print("Error of connection to MySQL: {}".format(e))
        return

    table_name = products_file.split('.')[0]

    sql_delete_table = """DROP TABLE IF EXISTS `{}`;""".format(table_name)
    run_sql(connection, sql_delete_table)

    sql_create_table = """CREATE TABLE `{}` (
    `ID`                                 int DEFAULT NULL,
    `SKU`                                varchar(100) CHARACTER SET utf8 DEFAULT NULL,
    `BrandName`                          varchar(100) CHARACTER SET utf8 DEFAULT NULL,
    `Name`                               varchar(100) CHARACTER SET utf8 DEFAULT NULL,
    `Stock`                              int DEFAULT NULL,
    `Price`                              decimal(20, 4) DEFAULT NULL,
    `Cost`                               decimal(20, 4) DEFAULT NULL,
    `EANCodes`                           decimal(20, 4) DEFAULT NULL,
    `MainImageURL`                       varchar(100) CHARACTER SET utf8 DEFAULT NULL,
    `ThumbImageURL`                      varchar(100) CHARACTER SET utf8 DEFAULT NULL,
    `Specifications`                     varchar(100) CHARACTER SET utf8 DEFAULT NULL,
    `Description`                        varchar(300) CHARACTER SET utf8 DEFAULT NULL,
    `CategoryName`                       varchar(100) CHARACTER SET utf8 DEFAULT NULL,
    `SubCategoryName`                    varchar(100) CHARACTER SET utf8 DEFAULT NULL,
    `SubSubCategoryName`                 varchar(100) CHARACTER SET utf8 DEFAULT NULL,
    `1stCheapestDistributorID`           int DEFAULT NULL,
    `1stCheapestDistributorName`         varchar(300) CHARACTER SET utf8 DEFAULT NULL,
    `1stCheapestDistributorPrice`        decimal(20, 4) DEFAULT NULL,
    `1stCheapestDistributorStock`        int DEFAULT NULL,
    `1stCheapestDistributorProductName`  int DEFAULT NULL,
    `1stCheapestDistributorDeliveryCost` decimal(20, 4) DEFAULT NULL,
    `1stCheapestDistributorSKU`          int DEFAULT NULL,
    `2ndCheapestDistributorID`           decimal(20, 4) DEFAULT NULL,
    `2ndCheapestDistributorName`         int DEFAULT NULL,
    `2ndCheapestDistributorPrice`        decimal(20, 4) DEFAULT NULL,
    `2ndCheapestDistributorStock`        decimal(20, 4) DEFAULT NULL,
    `2ndCheapestDistributorProductName`  int DEFAULT NULL,
    `2ndCheapestDistributorDeliveryCost` decimal(20, 4) DEFAULT NULL,
    `2ndCheapestDistributorSKU`          int DEFAULT NULL,
    `3rdCheapestDistributorID`           decimal(20, 4) DEFAULT NULL,
    `3rdCheapestDistributorName`         int DEFAULT NULL,
    `3rdCheapestDistributorPrice`        decimal(20, 4) DEFAULT NULL,
    `3rdCheapestDistributorStock`        decimal(20, 4) DEFAULT NULL,
    `3rdCheapestDistributorProductName`  int DEFAULT NULL,
    `3rdCheapestDistributorDeliveryCost` decimal(20, 4) DEFAULT NULL,
    `3rdCheapestDistributorSKU`          int DEFAULT NULL,
    `4thCheapestDistributorID`           decimal(20, 4) DEFAULT NULL,
    `4thCheapestDistributorName`         int DEFAULT NULL,
    `4thCheapestDistributorPrice`        decimal(20, 4) DEFAULT NULL,
    `4thCheapestDistributorStock`        decimal(20, 4) DEFAULT NULL,
    `4thCheapestDistributorProductName`  int DEFAULT NULL,
    `4thCheapestDistributorDeliveryCost` decimal(20, 4) DEFAULT NULL,
    `4thCheapestDistributorSKU`          int DEFAULT NULL,
    `5thCheapestDistributorID`           decimal(20, 4) DEFAULT NULL,
    `5thCheapestDistributorName`         int DEFAULT NULL,
    `5thCheapestDistributorPrice`        decimal(20, 4) DEFAULT NULL,
    `5thCheapestDistributorStock`        decimal(20, 4) DEFAULT NULL,
    `5thCheapestDistributorProductName`  int DEFAULT NULL,
    `5thCheapestDistributorDeliveryCost` decimal(20, 4) DEFAULT NULL,
    `5thCheapestDistributorSKU`          int DEFAULT NULL,
    `CategoryID`                         int DEFAULT NULL,
    `Title`                              int DEFAULT NULL,
    `Weight`                             decimal(20, 4) DEFAULT NULL,
    `DescriptionType`                    int DEFAULT NULL,
    KEY `ID` (`ID`)
    ) ENGINE=InnoDB;""".format(table_name)
    run_sql(connection, sql_create_table)

    sql_load_csv = """LOAD DATA INFILE '{}' INTO TABLE {};""".format(products_file, table_name)
    run_sql(connection, sql_load_csv)

def check_and_download_file_from_ftp(files_ftp, ftp, result_of_previous_connection):
    current_year = datetime.now().year
    result_of_connection = {}
    is_changed = False

    for l_property_of_file in files_ftp:

        filename = l_property_of_file.split()[-1]
        str_time_file = "{} {}".format(' '.join(l_property_of_file.split()[5:8]), current_year)

        if filename in result_of_previous_connection:
            str_previous_time_of_file = result_of_previous_connection[filename]

            if is_file_changed(str_previous_time_of_file, str_time_file):
                is_changed = True
                try:
                    result_of_connection[filename] = str_time_file
                    with open(filename, 'wb') as f:
                        ftp.retrbinary('RETR ' + filename, f.write)
                except Exception as e:
                    print("Erorr of downloading file from ftp: {}".format(e))
            else:
                print("File {} not changed".format(filename))
        else:
            is_changed = True
            try:
                result_of_connection[filename] = str_time_file
                with open(filename, 'wb') as f:
                    ftp.retrbinary('RETR ' + filename, f.write)
            except Exception as e:
                print("Erorr of download file: {}".format(e))

    return result_of_connection, is_changed

def main():

    ftp_server = "ftp.au.stockinthechannel.com"
    ftp_username = "StoreProductsCSV14"
    ftp_password = "E46DBF46"

    cfg_mysql = {'host': '127.0.0.1',
            'user': 'root', 'password': 'sheerwood1522',
            'db': 'zudello', 'charset': 'utf8', 'cursorclass': 'pymysql.cursors.DictCursor'}

    products_file = 'products.csv'

    file_result = "rconnection.json"

    try:
        ftp = FTP(host=ftp_server)
        ftp.login(user=ftp_username, passwd=ftp_password)
    except Exception as e:
        print(e)
        os.exit(1)

    files_ftp = []
    ftp.dir(files_ftp.append)

    result_of_previous_connection = load_result_of_previous_connection(file_result)
    result_of_current_connection, is_changed = check_and_download_file_from_ftp(files_ftp, ftp, result_of_previous_connection)
    if is_changed:
        save_result_of_current_connection(result_of_current_connection, file_result)
    load_csv_file_to_mysql(cfg_mysql, products_file)

if __name__ == "__main__":
    main()
