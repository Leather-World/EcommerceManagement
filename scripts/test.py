import pandas as pd


SHEET_ID = '1hnzzEf0SAyferMJIWvm6pa_TA5O3BX-0051Q0M_XMcs'
SHEET_NAME = 'Sheet1'
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'

product_report = pd.read_csv(url)

product_report.columns = product_report.columns.str.replace(' ', '')
product_report.rename(columns = {'SKUAmazon':'Amazon'}, inplace = True)

product_report.fillna(0, inplace=True)

product_details = product_report[['ProductID', 'Title', 'SubTitle', 'Description','Features','Dimensions','ImgURL','ProductCategory']]

# product_details.to_csv('product_details.csv', index=False)

inventory_report = product_report[['ProductID','Amazon','Flipkart','Myntra','Snapdeal','Tatacliq','Ajio','JioMart','Nykaa','Inventory','Benchmark', 'InvAddStatus']]
inventory_report.rename(columns = {'Amazon':'A', 'Flipkart':'F', 'Myntra':'M', 'Snapdeal':'SD', 'Ajio':'AJ', 'Tatacliq':'TQ', 'JioMart':'JM', 'Nykaa':'NK'}, inplace = True)


inventory_report.fillna(0, inplace=True)

inventory_report_filtered = inventory_report[inventory_report['InvAddStatus'] == 0]

if inventory_report_filtered.empty:
    print('ssssssssssss its empty')

else:

    print('not empty')

    # define a function to split the SKU and return the desired output
    def get_platform(row, platform):

        # print(row)

        # print('----------')

        # print(platform)

        # zero_cols = row[:-2][row == 0].index.tolist()
        skus = str(row[platform]).split(',') if isinstance(row[platform], str) else []

        inventory_per_platform = 0
        
        benchmark = int(row['Benchmark'])
        return pd.DataFrame({
            'ProductID': [row['ProductID']] * len(skus),
            'SKU': skus,
            'Platform': [platform] * len(skus),
            'Inventory': [inventory_per_platform] * len(skus),
            'TInventory': row['Inventory'],
            'Benchmark': [benchmark] * len(skus)
        })

    inventory_reports = pd.concat([
        get_platform(inventory_report_filtered.iloc[i], c) for i in range(len(inventory_report_filtered)) for c in inventory_report_filtered.columns[1:10]
    ])

print(inventory_reports.head(10))