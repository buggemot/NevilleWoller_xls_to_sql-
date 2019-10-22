import json
import pandas as pd
import os

from math import isnan

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

def get_cost_from_shipping_price(filter_shipp_by_suppliers, dropshipping, qty, suppl_price_stock):
    # dropshipping == False and qty >= filter_shipp_by_suppliers['order threshold EX GST '] ['Cost deliver to store above and equal to Threshold'] 
    # dropshipping == True and qty >= filter_shipp_by_suppliers['order threshold EX GST '] ['Cost dropshipequal or above threshold']
    # dropshipping == False and qty < filter_shipp_by_suppliers['order threshold EX GST '] ['Cost deliver to store below Threshold'] 
    # dropshipping == True and qty < filter_shipp_by_suppliers['order threshold EX GST '] ['Cost dropship below threshold']
    
    suppl_price_stock_for_ch = suppl_price_stock[:]
    for idx, item in enumerate(suppl_price_stock):
        temp_frame = filter_shipp_by_suppliers[filter_shipp_by_suppliers['Distributor'] == item[0]]
        if dropshipping & (temp_frame['Dropship'] == 'Y').all():
            if (qty >= temp_frame['order threshold EX GST ']).all():
                cost = temp_frame['Cost dropshipequal or above threshold'].item()
            elif (qty < temp_frame['order threshold EX GST ']).all():
                cost = temp_frame['Cost dropship below threshold'].item()
        else:
            if (qty >= temp_frame['order threshold EX GST ']).all():
                cost = temp_frame['Cost deliver to store above and equal to Threshold'].item()
            elif (qty < temp.frame['order threshold EX GST ']).all():
                cost = temp_frame['Cost deliver to store below Threshold'].item()
        suppl_price_stock_for_ch[idx].append(cost)
        # pdb.set_trace()
    suppl_price_stock_for_ch.sort(key=lambda x: x[1] + x[3])
    return suppl_price_stock_for_ch    

def get_suppl_price_stock_shprice(sku, dropshipping, shipping_price, qty):
    
    prefix_column_name = ('1st', '2nd', '3rd')
    suppl_price_stock = [[sku[i+'CheapestDistributorName'].item(), 
                            sku[i+'CheapestDistributorPrice'].item(),
                            sku[i+'CheapestDistributorStock'].item(),
                            ] for i in prefix_column_name if isinstance(sku[i+'CheapestDistributorName'].item(), str) and \
                            sku[i+'CheapestDistributorStock'].item() > 0
                        ]

    suppliers = [i[0] for i in suppl_price_stock]
    filter_shipp_by_suppliers = shipping_price[shipping_price['Distributor'].isin(suppliers)]

    suppl_price_stock_shprice = get_cost_from_shipping_price(filter_shipp_by_suppliers, dropshipping, qty, suppl_price_stock)
    return suppl_price_stock_shprice

def find_suppliers_by_qty(qty, suppl_price_stock):
    result = []
    while suppl_price_stock:
        supplier, price, stock, ship_cost = suppl_price_stock.pop(0)
        
        if stock >= qty:
            result.append((supplier, price, ship_cost, qty))
            qty = 0
            break
        elif stock < qty:
            result.append((supplier, price, ship_cost, stock))
            qty -= stock

    if qty > 0:
        return result, qty
    return result, 0

def get_orders(input_json, filter_country, price_file, shipping_price_obj):
    
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

        sku = price_file[price_file['SKU'] == item['sku']]

        if len(sku) > 0:
            suppl_price_stock_shprice = get_suppl_price_stock_shprice(sku, dropshipping, shipping_price_obj, item['qty'])
            best_suppl_by_cost, ok = find_suppliers_by_qty(item['qty'], suppl_price_stock_shprice)

            for line in best_suppl_by_cost:
                supplier, price, ship_cost, stock = line
                order = {'purchaseUUID': r'{generated}', 
                     'salesOrderUUID': input_json['salesOrderUUID'],
                     'dropShipping': dropshipping,
                     }
                order['supplier'] = supplier
                order['shippingCost'] = ship_cost
                order['totalCost'] = price * stock + ship_cost
                order['items'] = [{"sku":item['sku'], "qty":stock, "price":price}] 
                orders.append(order)

        else:
            print("There are not rows in price file for sku: {}".format(item['sku']))

            order = {'purchaseUUID': r'{generated}', 
                     'salesOrderUUID': input_json['salesOrderUUID'],
                     'dropShipping': '',
                     }
            order['supplier'] = ''
            order['shippingCost'] = ''
            order['totalCost'] = ''
            order['items'] = ["There are not rows in price file for sku: {}".format(item['sku'])]
            orders.append(order)

    return orders

def result_to_json_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def main():

    reader_input_json = Reader('test.json', 'json')
    reader_input_json.read_file()

    reader_price_file_csv = Reader('Products.csv', 'csv')
    reader_price_file_csv.read_file()

    reader_shipping_price_file_xls = Reader('supplier cost of shipping.xls', 'xls')
    reader_shipping_price_file_xls.read_file()
        
    # Is the order an Australian order (i.e. is the ship to country “Australia”) if it’s not we won’t be able to dropship.
    filter_country = 'Australia'
    orders= get_orders(reader_input_json.json_obj, filter_country, 
                        reader_price_file_csv.pd_csv_obj, reader_shipping_price_file_xls.pd_xls_obj)
    print(orders)
    result_to_json_file(orders, 'orders.json')

if __name__ == "__main__":
    main()
