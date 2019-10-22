import json
import pandas as pd
import os
import pdb

class Reader:

    def __init__(self, filename, type_of_file):

        self.filename = filename
        if not os.path.isfile(self.filename):
            raise IOError("File {} does not exist".format(self.filename))
        self.type_of_file = type_of_file

    def read_file(self):
        if self.type_of_file == "json":
            with open(self.filename, 'r') as f:
                self.json_obj = json.load(f)
        elif self.type_of_file == "xls":
            self.pd_xls_obj = pd.read_excel(self.filename)
        elif self.type_of_file == "csv":
            self.pd_csv_obj = pd.read_csv(self.filename)

class Writer:
    pass


def get_price_by_condition(row, qty):
    data = {}
    data['Supplier'] = row['Distributor']
    if row['Dropship'] == "Y":
        data['cost'] = 500
#         if qty >= filter_shipp_by_suppliers['order threshold EX GST ']:
#             data['cost'] = row['Cost dropshipequal or above threshold']
#         else:
#             data['cost'] = row['Cost dropship below threshold']
#     else:
        if filter_shipp_by_suppliers['order threshold EX GST '] > qty:
            data['cost'] = row['Cost deliver to store above and equal to Threshold']
#         else:
#             data['cost'] = row['Cost deliver to store below Threshold']
    return data


def get_supplier_with_low_price(sku, dropshipping, shipping_price, qty):
    
    prefix_column_name = ('1st', '2nd', '3rd')
    suppl_price_stock = [(sku[i+'CheapestDistributorName'].item(), 
                            sku[i+'CheapestDistributorPrice'].item(),
                            sku[i+'CheapestDistributorStock'].item(),
                            ) for i in prefix_column_name
                        ]

    suppliers = [i[0] for i in suppl_price_stock]
    filter_shipp_by_suppliers = shipping_price[shipping_price['Distributor'].isin(suppliers)]


    # dropshipping == False and qty >= filter_shipp_by_suppliers['order threshold EX GST '] ['Cost deliver to store above and equal to Threshold'] 
    # dropshipping == True and qty >= filter_shipp_by_suppliers['order threshold EX GST '] ['Cost dropshipequal or above threshold']
    # dropshipping == False and qty < filter_shipp_by_suppliers['order threshold EX GST '] ['Cost deliver to store below Threshold'] 
    # dropshipping == True and qty < filter_shipp_by_suppliers['order threshold EX GST '] ['Cost dropship below threshold']


    filter_shipp_by_suppliers 

    pdb.set_trace()
    return 

def pick_best_price(input_json, filter_country, price_file, shipping_price):
    
    orders = []
    

    dropshipping = True
    # Is the order an Australian order (i.e. is the ship to country “Australia”) if it’s not we won’t be able to dropship.
    if input_json['address']['country'].strip() != filter_country:
        print('We won’t be able to dropship')
        dropshipping = False
        
        # "supplier": "XiT Distribution",
        # "shippingCost": {calculated},
        # "totalCost": {shipping cost + total line item cost},
        # "items": [
            # {
            #     "sku": "VX3276-2K",
            #     "qty": 1,
            #     "price": 282
            # }

    for item in input_json['items']:

        order = {'purchaseUUID': r'{generated}', 
                 'salesOrderUUID': input_json['salesOrderUUID'],
                 'dropShipping': dropshipping,
                 'items': [],
                 }

        sku = price_file[price_file['SKU'] == item['sku']]

        if len(sku) > 0:
            get_supplier_with_low_price(sku, dropshipping, shipping_price, item['qty'])        
        else:
            print("There are not rows in price file for sku: {}".format(item['sku']))
            order['supplier'] = ''
            order['shippingCost'] = ''
            order['totalCost'] = ''

        orders.append(order)

    return orders

def main():

    reader_input_json = Reader('test.json', 'json')
    reader_input_json.read_file()

    reader_price_file_csv = Reader('Products.csv', 'csv')
    reader_price_file_csv.read_file()

    reader_shipping_price_file_xls = Reader('supplier cost of shipping.xls', 'xls')
    reader_shipping_price_file_xls.read_file()
        
    # Is the order an Australian order (i.e. is the ship to country “Australia”) if it’s not we won’t be able to dropship.
    filter_country = 'Australia'
    result = pick_best_price(reader_input_json.json_obj, filter_country, reader_price_file_csv.pd_csv_obj, reader_shipping_price_file_xls.pd_xls_obj)

    print('e')

if __name__ == "__main__":
    main()
