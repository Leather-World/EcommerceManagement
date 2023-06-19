from flask import Flask, json, request, render_template, flash,  redirect, url_for, send_from_directory, send_file, session ,jsonify
import os
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import sys
from dateutil import parser

from logger import setup_logger

# Set up the logger
logger = setup_logger()


Inventory_report_db_path = os.path.join(os.getcwd(), 'Database', 'Inventory.db')
InventoryM_report_db_path = os.path.join(os.getcwd(), 'Database', 'InventoryM.db')
Order_report_db_path = os.path.join(os.getcwd(),'Database', 'Order.db')
Product_report_db_path = os.path.join(os.getcwd(),'Database', 'Product.db')
Return_report_db_path = os.path.join(os.getcwd(),'Database', 'Return.db')

def check_user():
    if 'user' not in session:
        return redirect('login.html')
    else:
        return session

# Helper function to get a dictionary of ProductID -> SubTitle mappings
def get_product_subtitles(product_data):
    return {product['ProductID']: product['SubTitle'] for product in product_data}

def InventoryHome():

    print(check_user())

    # ReadLatestInventory()

    rows = show_update_inventory_show()
    # Render the template with the rows

    if rows is not None:
        product_data = get_product_subtitles(rows)

    else:
        product_data = None

    m_invt_rows = m_inventory_show()

    # print(m_invt_rows)

    one_week_order_summary_dict = one_week_order_summary()


    return render_template('/inventorySite/inventoryHome.html',one_week_order_summary_dict=one_week_order_summary_dict, rows=rows, product_data=product_data, m_invt_rows=m_invt_rows)
    

def format_order_reports(result):

    order_report = []

    for platform, url in result.items():

        print(platform, url)

        logger.info('Formating platform: %s with url: %s' , platform, url)


        try:
            if platform == 'amazon_dor' and url[0] != '':
                amazon_order_report = pd.read_csv(url[0])
                amazon_order_report = amazon_order_report[['amazon-order-id','purchase-date','sku','quantity','order-status','asin']]
                amazon_order_report.rename(columns = {'amazon-order-id':'order_id','purchase-date':'order_date','asin':'platformID'}, inplace = True)
                amazon_order_report = amazon_order_report[~amazon_order_report['order-status'].isin(['Cancelled'])]
                amazon_order_report.drop(['order-status'], axis=1,  inplace=True)
                # convert the purchase-date column to a datetime object
                amazon_order_report['order_date'] = pd.to_datetime(amazon_order_report['order_date'])
                # extract the date from the datetime object
                amazon_order_report['order_date'] = amazon_order_report['order_date'].dt.strftime('%Y-%m-%d')

                # amazon_order_report['order_date'] = amazon_order_report['order_date'].dt.date
                amazon_order_report['platform'] = 'A'

                logger.info('Amazon OR: %s' , amazon_order_report.head(2))
                order_report.append(amazon_order_report)

            if platform == 'flipkart_dor' and url[0] != '':
                flipkart_order_report = pd.read_csv(url[0])
                flipkart_order_report = flipkart_order_report[['order_id','order_date','sku','quantity','order_item_status','fsn']]
                flipkart_order_report.rename(columns = {'fsn':'platformID'}, inplace = True)
                flipkart_order_report['order_item_status'].unique()
                flipkart_order_report = flipkart_order_report[~flipkart_order_report['order_item_status'].isin(['CANCELLED'])]
                flipkart_order_report.drop(['order_item_status'], axis=1,  inplace=True)

                flipkart_order_report['sku'] = flipkart_order_report['sku'].str.split(':').str[1].str.rstrip('"')

                print(flipkart_order_report.head(5))
                # convert the purchase-date column to a datetime object
                flipkart_order_report['order_date'] = pd.to_datetime(flipkart_order_report['order_date'])
                # extract the date from the datetime object
                # flipkart_order_report['order_date'] = flipkart_order_report['order_date'].dt.date

                # flipkart_order_report = flipkart_order_report['order_date'].split(' ')[0]
                flipkart_order_report['order_date'] = flipkart_order_report['order_date'].astype(str).str.split(' ').str[0]

                # flipkart_order_report['order_date'] = flipkart_order_report['order_date'].dt.strftime('%Y-%m-%d')



                flipkart_order_report['platform'] = 'F'
                logger.info('Flipkart OR: %s' , flipkart_order_report.head(2))


                order_report.append(flipkart_order_report)

            if platform == 'myntra_dor' and url[0] != '':
                myntra_order_report = pd.read_csv(url[0])
                myntra_order_report = myntra_order_report[['Order Release Id','Created On','Vendor Article Number','Order Status','Style ID']]
                myntra_order_report.rename(columns = {'Order Release Id':'order_id','Created On':'order_date', 
                                                    'Vendor Article Number':'sku','Style ID':'platformID'}, inplace = True)

                myntra_order_report['Order Status'].unique()
                myntra_order_report = myntra_order_report[~myntra_order_report['Order Status'].isin(['C'])]
                myntra_order_report.drop(['Order Status'], axis=1,  inplace=True)

                myntra_order_report['quantity'] = 1
                myntra_order_report['platform'] = 'M'
                reorder = ['order_id', 'order_date', 'sku', 'quantity', 'platformID', 'platform']
                myntra_order_report = myntra_order_report.reindex(columns=reorder)

                myntra_order_report['order_date'] = pd.to_datetime(myntra_order_report['order_date'])

                myntra_order_report['order_date'] = myntra_order_report['order_date'].dt.strftime('%Y-%m-%d')

                logger.info('Myntra OR: %s' , myntra_order_report.head(2))

                order_report.append(myntra_order_report)

            
            if platform == 'ajio_dor' and url[0] != '':
                ajio_order_report = pd.read_csv(url[0])
                ajio_order_report = ajio_order_report[['Cust Order No','Cust Order Date','Seller SKU','Order Qty','Status','JioCode']]
                ajio_order_report.rename(columns = {'Cust Order No':'order_id', 'Cust Order Date':'order_date', 
                                                    'Seller SKU':'sku', 'Order Qty':'quantity', 'JioCode':'platformID'}, inplace = True)

                ajio_order_report = ajio_order_report[~ajio_order_report['Status'].isin(['Cancelled'])]
                ajio_order_report.drop(['Status'], axis=1,  inplace=True)

                # parse the date strings using dateutil
                ajio_order_report['order_date'] = ajio_order_report['order_date'].apply(parser.parse)

                # convert to YYYY-MM-DD format
                ajio_order_report['order_date'] = ajio_order_report['order_date'].dt.strftime('%Y-%m-%d')

                ajio_order_report = ajio_order_report.sort_values(by='order_date')



                ajio_order_report['platform'] = 'AJ'
                logger.info('Ajio OR: %s' , ajio_order_report.head(2))


                order_report.append(ajio_order_report)


            if platform == 'snapdeal_dor' and url[0] != '':
                snapdeal_order_report = pd.read_csv(url[0])
                snapdeal_order_report = snapdeal_order_report[['ORDER CODE','ORDER DATE','SKU CODE','QTY','CURRENT ORDER STATE','SUPC']]

                snapdeal_order_report.rename(columns = {'ORDER CODE':'order_id', 'ORDER DATE':'order_date', 
                                                    'SKU CODE':'sku', 'QTY':'quantity', 'SUPC':'platformID'}, inplace = True)

                snapdeal_order_report = snapdeal_order_report[~snapdeal_order_report['CURRENT ORDER STATE'].isin(['Cancelled', 'Order Cancelled'])]
                snapdeal_order_report.drop(['CURRENT ORDER STATE'], axis=1,  inplace=True)
                # convert the purchase-date column to a datetime object
                snapdeal_order_report['order_date'] = pd.to_datetime(snapdeal_order_report['order_date'])
                # extract the date from the datetime object
                # snapdeal_order_report['order_date'] = snapdeal_order_report['order_date'].dt.date

                snapdeal_order_report['order_date'] = snapdeal_order_report['order_date'].dt.strftime('%Y-%m-%d')

                snapdeal_order_report['platform'] = 'SD'

                logger.info('Snapdeal OR: %s' , snapdeal_order_report.head(2))
                order_report.append(snapdeal_order_report)

            if platform == 'tataq_dor' and url[0] != '':
                tataq_order_report = pd.read_csv(url[0])

                tataq_order_report = tataq_order_report[['OrderId','OrderDate','SKU', 'OrderStatus ']]

                tataq_order_report.rename(columns = {'OrderId':'order_id', 'OrderDate':'order_date', 
                                                    'SKU':'sku'}, inplace = True)
                
                tataq_order_report = tataq_order_report[~tataq_order_report['OrderStatus '].isin(['Closed on cancellation', 'Order cancelled'])]

                tataq_order_report.drop(['OrderStatus '], axis=1,  inplace=True)


                tataq_order_report['quantity'] = 1
                tataq_order_report['platformID'] = 0
                tataq_order_report['platform'] = 'TQ'
                order_report.append(tataq_order_report)

                tataq_order_report['order_date'] = pd.to_datetime(tataq_order_report['order_date'])

                tataq_order_report['order_date'] = tataq_order_report['order_date'].dt.strftime('%Y-%m-%d')
                tataq_order_report = tataq_order_report.sort_values(by='order_date')

                tataq_order_report['order_id'] = tataq_order_report['order_id'].str.strip("'")

                logger.info('TatacliQ OR: %s' , tataq_order_report.head(2))
                order_report.append(tataq_order_report)

            
            if platform == 'NK_NKFSN_dor' and url[0] != '':
                print(platform)
                NK_NKFSN_order_report = pd.read_csv(url[0])
                # NK_NKFSN_order_report = NK_NKFSN_order_report[['or','Order Date','SKU','Order Qty', 'platforms']]
                # NK_NKFSN_order_report.rename(columns = {'Order No':'order_id','Order Date':'order_date','SKU':'sku','Order Qty':'quantity'}, inplace = True)

                # convert the purchase-date column to a datetime object
                NK_NKFSN_order_report['order_date'] = pd.to_datetime(NK_NKFSN_order_report['order_date'])
                # extract the date from the datetime object
                NK_NKFSN_order_report['order_date'] = NK_NKFSN_order_report['order_date'].dt.strftime('%Y-%m-%d')

                NK_NKFSN_order_report['platform'] = NK_NKFSN_order_report['platforms'].apply(lambda x: 'NK' if x == 'Nykaa' else 'NKFSN')

                NK_NKFSN_order_report.drop('platforms', axis=1, inplace=True)

                NK_NKFSN_order_report['platformID'] = 0

                reorder = ['order_id', 'order_date', 'sku', 'quantity', 'platformID', 'platform']
                NK_NKFSN_order_report = NK_NKFSN_order_report.reindex(columns=reorder)

                logger.info('Nykaa and Nykaa Fashion OR: %s' , NK_NKFSN_order_report.head(4))

                order_report.append(NK_NKFSN_order_report)

        except Exception as e:
            # print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

            logger.error('Error: %s', e)

            return None, 'error'    
    try:

        logger.info('Adding ProductID to each order')


        final_order_report = pd.concat(order_report)
        final_order_report = final_order_report.sort_values(by='order_date')
        
        inventory_report_db = Inventory_report_db_path
        inventory_report_table = "inventory_report"

    
        # create a connection to the inventory report database
        inventory_conn = sqlite3.connect(inventory_report_db)

        # create a cursor object to execute SQL commands
        inventory_cursor = inventory_conn.cursor()

        sku_not_found = []

        product_id_list = []

        # loop over each row in the order report dataframe
        for index, row in final_order_report.iterrows():
            # fetch the productid from the inventory report table using sku
            fetch_productid_sql = f"SELECT ProductID FROM {inventory_report_table} WHERE SKU = ?"
            inventory_cursor.execute(fetch_productid_sql, (row["sku"],))
            productid = inventory_cursor.fetchone()

            if productid:
                productid = productid[0]
            else:
                productid = None
                sku_not_found.append(row)
            
            product_id_list.append(productid)
        
        final_order_report['productid'] = product_id_list

        logger.info('ProductID Added')


        # final_order_report.to_csv('final_order_report.csv', index=False)

        sum_per_day = final_order_report.groupby(['productid'])['quantity'].sum().reset_index()

        # sum_per_day.to_csv('Quantity_SUM_Per_SKU_P.csv' ,index=False)

        logger.info('Final Order Repor Has been Created and Order Per Platform has been saved')


        return final_order_report, 'ok'
    
    except Exception as e:
        logger.error('Error: %s', e)

        return None, 'error'    

def insert_dor(order_report):
    
    # order_report = pd.read_csv("or_may_11_15.csv")
    order_report.drop_duplicates(keep='first', inplace=True)

    logger.info('Order Report: %s' , order_report.head(10))

    try:

        # define the name of the databases and tables
        order_report_db = Order_report_db_path
        # inventory_report_db = Inventory_report_db_path
        order_report_table = "order_report"
        # inventory_report_table = "inventory_report"

        # create a connection to the order report database
        order_conn = sqlite3.connect(order_report_db)

        # create a cursor object to execute SQL commands
        order_cursor = order_conn.cursor()

        # create the daily order report table if it doesn't exist
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {order_report_table} (
                order_id TEXT PRIMARY KEY,
                order_date TEXT,
                sku TEXT,
                quantity INTEGER,
                platformID TEXT,
                platform TEXT,
                productid TEXT,
                inv_updt_status INTEGER DEFAULT 0
            )
        """
        order_cursor.execute(create_table_sql)

        '''
        # create a connection to the inventory report database
        inventory_conn = sqlite3.connect(inventory_report_db)

        # create a cursor object to execute SQL commands
        inventory_cursor = inventory_conn.cursor()

        '''

        # sku_not_found = []

        # loop over each row in the order report dataframe
        for index, row in order_report.iterrows():

            # check if the order_id already exists in the daily order report database
            check_sql = f"SELECT * FROM {order_report_table} WHERE order_id = ?"
            order_cursor.execute(check_sql, (row["order_id"],))
            existing_data = order_cursor.fetchone()

            if existing_data:
                # if the order_id already exists, update the row
                update_sql = f"""
                    UPDATE {order_report_table}
                    SET order_date = ?,
                        sku = ?,
                        quantity = ?,
                        platformID = ?,
                        platform = ?,
                        productid = ?,
                        inv_updt_status = 1
                    WHERE order_id = ?
                """
                order_cursor.execute(update_sql, (
                    row["order_date"],
                    row["sku"],
                    row["quantity"],
                    row["platformID"],
                    row["platform"],
                    row["productid"],
                    row["order_id"]
                ))
            else:
                # if the order_id does not exist, insert the row
                insert_sql = f"""
                    INSERT INTO {order_report_table} (order_id, order_date, sku, quantity, platformID, platform, productid )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                order_cursor.execute(insert_sql, (
                    row["order_id"],
                    row["order_date"],
                    row["sku"],
                    row["quantity"],
                    row["platformID"],
                    row["platform"],
                    row["productid"],

                ))



        # commit the changes and close the connections
        order_conn.commit()

        order_conn.close()
        # inventory_conn.close()

        msg = "Order Report has been recorded"

        logger.info('Order Report has been recorded')

        return msg, 'success'

    except Exception as e:
        msg = f"Order Report is received but Couldn't be saved to the database because {e}"

        logger.error('Error: %s', e)

        return msg, 'error'

    
def download_latest_int_sheet():
    # Define your Google Sheets and their names
    SHEET_ID =  '1dWvrVa_F1arAywuC-PPo92LIcr6Ud290'

    SHEET_NAMES = ['DuffelBag', 'Hiking', 'LaptopBag', 'SlingBag', 'BackPack', 'Watchcase']


    COLUMNS_TO_READ = [0,7]
    # Define the output CSV file name
    OUTPUT_FILE = 'latest_stock_update_sheet.csv'

    # Loop through all the sheets and append their data to a single DataFrame
    inventory_report_list = []
    for sheet_name in  SHEET_NAMES:
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        # response = requests.get(url)
        temp_df = pd.read_csv(url,usecols=COLUMNS_TO_READ)

        print(temp_df)
        inventory_report_list.append(temp_df)


    inventory_report = pd.concat(inventory_report_list)



    inventory_report = inventory_report.rename(columns={'PRODUCT ID': 'ProductID'})
    inventory_report = inventory_report.rename(columns={'Unnamed: 7': 'Inventory'})
    
    # inventory_report = inventory_report.drop('Unnamed: 0', axis=1)

    # inventory_report.to_csv(OUTPUT_FILE, index=False)

    return inventory_report

'''
def download_inv_sheet():

    try:

        SHEET_ID = '1hnzzEf0SAyferMJIWvm6pa_TA5O3BX-0051Q0M_XMcs'
        SHEET_NAME = 'Sheet1'
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'

        product_report = pd.read_csv(url)

        product_report.columns = product_report.columns.str.replace(' ', '')
        product_report.rename(columns = {'SKUAmazon':'Amazon'}, inplace = True)

        product_report.fillna(0, inplace=True)

        inventory_report = product_report[['ProductID','Amazon','Flipkart','Myntra','Snapdeal','Tatacliq','Ajio','JioMart','Nykaa','Benchmark']]
        inventory_report.rename(columns = {'Amazon':'A', 'Flipkart':'F', 'Myntra':'M', 'Snapdeal':'SD', 'Ajio':'AJ', 'Tatacliq':'TQ', 'JioMart':'JM', 'Nykaa':'NK'}, inplace = True)


        latest_stock_update_df = download_latest_int_sheet()

        # print(latest_stock_update_df.head(2))

        inventory_report = pd.merge(inventory_report, latest_stock_update_df, on='ProductID', how='left')

        # print(inventory_report.head(2))

        inventory_report.fillna(0, inplace=True)

        inventory_report.to_csv('merged_inventory_reports.csv', index=False)




        # define a function to split the SKU and return the desired output
        def get_platform(row, platform):

            # zero_cols = row[:-2][row == 0].index.tolist()
            skus = str(row[platform]).split(',') if isinstance(row[platform], str) else []

            plat_with_sku = set(c for c in row.index[1:9] if len(str(row[c])))
            plat_with_no_sku = set(c for c in row.index[1:9] if row[c] == 0)
            num_platforms = len(plat_with_sku) - len(plat_with_no_sku)

            inventory_per_platform = int(row['Inventory'] / num_platforms)
            leftover_inventory = int(row['Inventory'] % num_platforms)

            if leftover_inventory > 0:
                if leftover_inventory >= num_platforms:
                    inventory_per_platform += leftover_inventory // num_platforms
                else:
                    platforms_to_add = list(plat_with_sku)[:leftover_inventory]
                    if platform in platforms_to_add:
                        inventory_per_platform += 1
            
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
            get_platform(inventory_report.iloc[i], c) for i in range(len(inventory_report)) for c in inventory_report.columns[1:11]
        ])


        # print('Inventory Report-----------',inventory_reports.head(20))

        # Read the sku_platformid
        sku_platformid = pd.read_csv('inventory_reports/inventory_report_M_NK_AJ_SD.csv')

        # Merge the inventory report with the sku_platformid on the 'SKU' column
        inventory_reports = pd.merge(inventory_reports, sku_platformid[['SKU', 'PlatformID', 'Platform']], on=['SKU', 'Platform'], how='left')

        inventory_reports = inventory_reports.fillna(value=0.0)

        inventory_reports.to_csv('inventory_reports.csv', index=False)


        product_details = product_report[['ProductID', 'Title', 'SubTitle', 'Description','Features','Dimensions','ImgURL','ProductCategory']]

        product_details.to_csv('product_details.csv', index=False)


        return inventory_reports, product_details ,'ok'

    except Exception as e:

        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        return None, None, f'{e}'
'''

def download_invt_product_details():
    try:

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

        inventory_report_filtered = inventory_report[inventory_report['InvAddStatus'] == 1]

        if inventory_report_filtered.empty:
            return 'not_found', None, product_details ,'ok'
        
        else:

            # define a function to split the SKU and return the desired output
            def get_platform(row, platform):

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

            final_inventory_reports = pd.concat([
                get_platform(inventory_report_filtered.iloc[i], c) for i in range(len(inventory_report_filtered)) for c in inventory_report_filtered.columns[1:11]
            ])



            # Read the sku_platformid
            sku_platformid = pd.read_csv('inventory_reports/inventory_report_M_NK_AJ_SD.csv')

            # Merge the inventory report with the sku_platformid on the 'SKU' column
            final_inventory_reports = pd.merge(final_inventory_reports, sku_platformid[['SKU', 'PlatformID', 'Platform']], on=['SKU', 'Platform'], how='left')

            final_inventory_reports = final_inventory_reports.fillna(value=0.0)

            # final_inventory_reports.to_csv('inventory_reports.csv', index=False)

            return 'found', final_inventory_reports, product_details ,'ok'

    except Exception as e:

        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        return None, None, f'{e}'


def update_product_details(product_details):
        
    try:

        # define the name of the database and table
        DATABASE_NAME = Product_report_db_path
        TABLE_NAME = "product_details"

        # create a connection to the database
        conn = sqlite3.connect(DATABASE_NAME)

        # create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # drop the table if it exists
        drop_table_sql = f"DROP TABLE IF EXISTS {TABLE_NAME}"
        cursor.execute(drop_table_sql)

        #'ProductID', 'Title', 'SubTitle', 'Description','Features','Dimensions','ImgURL','ProductCategory'

        # create the table
        create_table_sql = f"""
            CREATE TABLE {TABLE_NAME} (
                ProductID TEXT PRIMARY KEY,
                SubTitle TEXT,
                Title TEXT,
                Description TEXT,
                Features TEXT,
                Dimensions TEXT,
                ImgURL TEXT,
                ProductCategory TEXT
            )
        """
        cursor.execute(create_table_sql)

        for index, row in product_details.iterrows():
            insert_sql = f"""
                INSERT OR REPLACE INTO {TABLE_NAME} (ProductID, SubTitle, Title, Description, Features, Dimensions, ImgURL, ProductCategory)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_sql, (
                row["ProductID"],
                row["SubTitle"],
                row["Title"],
                row["Description"],
                row["Features"],
                row["Dimensions"],
                row["ImgURL"],
                row["ProductCategory"]
            ))

        # commit the changes and close the connection
        conn.commit()
        conn.close()

        return 'ok'
    
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        logger.error('Error while updating Product Details because: %s', e)

        return 'error'


def update_inventory_details(inventory_report):
    try:
        # Define the name of the database and table
        DATABASE_NAME = Inventory_report_db_path  # Replace with the actual path
        TABLE_NAME = "inventory_report"

        # Create a connection to the database
        conn = sqlite3.connect(DATABASE_NAME)

        # Create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                ProductID TEXT,
                SKU TEXT,
                PlatformID TEXT,
                Platform TEXT,
                Inventory INTEGER,
                TInventory INTEGER,
                Benchmark INTEGER
            )
        """
        cursor.execute(create_table_sql)

        # Iterate over the inventory_report DataFrame
        for _, row in inventory_report.iterrows():
            # Check if the record already exists
            check_existence_sql = f"SELECT 1 FROM {TABLE_NAME} WHERE ProductID = ? AND SKU = ? AND Platform = ?"
            cursor.execute(check_existence_sql, (row["ProductID"], row["SKU"], row["Platform"]))
            result = cursor.fetchone()

            if result:
                # Update the values if the record exists
                update_sql = f"""
                    UPDATE {TABLE_NAME}
                    SET Inventory = ?,
                        TInventory = ?,
                        Benchmark = ?
                    WHERE ProductID = ? AND SKU = ? AND Platform = ?
                """
                cursor.execute(update_sql, (
                    row["Inventory"],
                    row["TInventory"],
                    row["Benchmark"],
                    row["ProductID"],
                    row["SKU"],
                    row["Platform"]
                ))
            else:
                # Insert the values if the record doesn't exist
                insert_sql = f"""
                    INSERT INTO {TABLE_NAME} (ProductID, SKU, PlatformID, Platform, Inventory, TInventory, Benchmark)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(insert_sql, (
                    row["ProductID"],
                    row["SKU"],
                    row["PlatformID"],
                    row["Platform"],
                    row["Inventory"],
                    row["TInventory"],
                    row["Benchmark"]
                ))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        return 'ok'
    
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        return 'error'


def ReadLatestInventory():

    '''
    Read and Replace the inventory sheet in the database

    '''

    int_f_or_nf_status, inventory_report, product_details, msg_status = download_invt_product_details()

    invt_msg = ''

    pro_msg = ''


    if msg_status == 'ok' and int_f_or_nf_status == 'found' and inventory_report is not None:

        invt_msg = update_inventory_details(inventory_report)

    elif msg_status == 'ok' and int_f_or_nf_status == 'not_found':

        invt_msg = 'ok'


    if msg_status == 'ok' and product_details is not None:

        pro_msg = update_product_details(product_details)


    if invt_msg == 'ok' and pro_msg == 'ok':

        msg_status = 'Latest Inventory and Product Details has been recorded'

        return jsonify({'status': 'Success', 'message': msg_status})

    else:
        msg_status = 'Error in Updating Inventory and Product Details'

        return jsonify({'status': 'Error', 'message': msg_status})


    # else:
    #     return jsonify({'status': 'Error', 'message': msg_status})

def update_inventory():

    '''
         Update Inventory based on Daily Order Report from Different Platform
    '''
    try:

        # Connect to the order_report and inventory databases
        conn_order = sqlite3.connect(Order_report_db_path)
        conn_inv = sqlite3.connect(Inventory_report_db_path)

        cs_inv = conn_inv.cursor()

        # Define the start and end dates for the past week
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=2)

        date_format = '%Y-%m-%d'

        # Parse the start and end dates
        start_date = datetime.strptime(start_date.strftime('%Y-%m-%d'), date_format).date()
        end_date = datetime.strptime(end_date.strftime('%Y-%m-%d'), date_format).date()

        # Define the SQL query with the date filter
        query = f"SELECT * FROM order_report WHERE order_date >= '{start_date}' AND order_date <= '{end_date}' AND inv_updt_status = 0"

        # Execute the query and store the results in a pandas dataframe
        order_report = pd.read_sql_query(query, conn_order)

        inventory_report = pd.read_sql_query('SELECT * FROM inventory_report', conn_inv)


        def update_TInventory(cs_inv):

            try:
                # Get a list of distinct product IDs
                cs_inv.execute('''SELECT DISTINCT ProductID FROM inventory_report''')
                product_ids = [row[0] for row in cs_inv.fetchall()]

                # Loop over the product IDs and update the TInventory column
                for product_id in product_ids:
                    cs_inv.execute('''UPDATE inventory_report 
                                SET TInventory = (SELECT SUM(Inventory) 
                                                FROM (SELECT DISTINCT Platform, Inventory 
                                                        FROM inventory_report 
                                                        WHERE ProductID = ?) 
                                                AS distinct_platforms) 
                                WHERE ProductID = ?''', (product_id, product_id))
                
                
                return 'ok'
            
            except Exception as e:
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

                return 'error'


        '''
        # Define a function to find the best match SKU from the inventory_report
        def find_pid_best_match_sku(sku, inventory_report, platform=None):
            """
            Takes in an SKU, inventory_report dataframe, and an optional platform filter
            and returns the best match SKU and platform.
            """
            # Filter the inventory_report dataframe for SKUs that contain the given SKU
            filtered_inventory = inventory_report[inventory_report['SKU'].str.contains(sku)]
            
            if platform is not None:
                # If platform filter is given, filter the inventory_report for the given platform
                filtered_inventory = filtered_inventory[filtered_inventory['Platform'] == platform]
            
            # If there are no matches, return None
            if len(filtered_inventory) == 0:
                return None

            
            return filtered_inventory.iloc[0]['ProductID']
        
        '''

        # Loop through the order_report dataframe and subtract the quantity from the matching SKU in inventory_report
        for i in range(len(order_report)):
            sku = order_report.iloc[i]['sku']
            quantity = order_report.iloc[i]['quantity']
            platform = order_report.iloc[i]['platform']
            productid = order_report.iloc[i]['productid']

            # pid_best_match_sku = find_pid_best_match_sku(sku, inventory_report, platform)
            
            if productid is not None:

                print(productid, platform, quantity)

                # Subtract the quantity from the Quantity of the best match SKU for the given Product ID and Platform
                inventory_report.loc[(inventory_report['ProductID'] == productid) & (inventory_report['Platform'] == platform), 'Inventory'] -= quantity

                order_id = order_report.iloc[i]['order_id']
                conn_order.execute("UPDATE order_report SET inv_updt_status = 1 WHERE order_id = ?", (order_id,))
                # results = cs_inv.execute("SELECT * FROM inventory_report WHERE ProductID = ? AND Platform = ?", (pid_best_match_sku, platform)).fetchall()

                # print(results)

                conn_order.commit()

            


        inventory_report.to_sql('inventory_report', conn_inv, if_exists='replace', index=False)

        # conn_inv.execute('UPDATE inventory_report SET TInventory = (SELECT SUM(Inventory) FROM (SELECT DISTINCT ProductID, Platform, Inventory FROM inventory_report) WHERE ProductID = inventory_report.ProductID)')

        logger.info('Inventory has been Updated')

        update_TInventory(cs_inv)

        logger.info('Total Inventory column has been updated')


        conn_inv.commit()

        # Close the database connections
        conn_order.close()
        conn_inv.close()        

        return 'success','Inventory has been Updated'


    except Exception as e:

        logger.error('Error while updating Inventory because: %s', e)

        return 'error',f'Error while updating Inventory because {e}'


def DailyOrderReport():

    if request.method == "POST":
        
        result = request.form.to_dict(flat=False)


        logger.info('Daily Order Report FilePath Dictionary: %s', result)

        final_order_report, msg = format_order_reports(result)

        if msg == 'error':
            msg = 'Please provide correct path of order report of atleast one platform'
            return jsonify({'status': 'altert', 'message': msg})
        
        elif msg == 'ok':
            msg, msg_status = insert_dor(final_order_report)

            if msg_status == 'success':

                msg_st, msg = update_inventory()

                if msg_st == 'success':

                    return jsonify({'status': 'success', 'message': msg})

                else:
                    return jsonify({'status': 'error', 'message': msg})
               
            
    return render_template('/inventorySite/inventoryHome.html')


def estimate_stock_over():
    # Connect to the order_report database
    order_report_conn = sqlite3.connect(Order_report_db_path)

    # Get the orders from the past one week
    one_week_ago = datetime.now() - timedelta(days=30)
    query = f"SELECT * FROM order_report WHERE order_date >= '{one_week_ago.strftime('%Y-%m-%d')}'"
    orders = pd.read_sql_query(query, order_report_conn)

    # Calculate the sum of quantity per day for each product
    orders['order_date'] = pd.to_datetime(orders['order_date'], format='%Y-%m-%d')
    orders['day'] = orders['order_date'].dt.date
    sum_per_day = orders.groupby(['productid', 'day'])['quantity'].sum().reset_index()

    # Connect to the inventory_report database
    inventory_report_conn = sqlite3.connect(Inventory_report_db_path)

    # Get the inventory and join with the sum_per_day dataframe
    inventory_query = "SELECT ProductID, TInventory FROM inventory_report"
    inventory = pd.read_sql_query(inventory_query, inventory_report_conn)
    inventory.rename(columns = {'ProductID':'productid'}, inplace = True)
    inventory = inventory.merge(sum_per_day, on='productid')

    avg_qty_per_day = inventory.groupby('productid')['quantity'].mean().reset_index()
    avg_qty_per_day['quantity'] = avg_qty_per_day['quantity'].round(0).astype(int)

    inventory_subset = inventory[['productid', 'TInventory']]

    avg_qty_per_day = avg_qty_per_day.merge(inventory_subset[['productid', 'TInventory']], on='productid')

    avg_qty_per_day = avg_qty_per_day.drop_duplicates()
    avg_qty_per_day['days_until_empty'] = avg_qty_per_day['TInventory'] / avg_qty_per_day['quantity']
    avg_qty_per_day['days_until_empty'] = avg_qty_per_day['days_until_empty'].apply(lambda x: round(x + 0.5)).astype(int)

    avg_qty_per_day.rename(columns = {'productid':'ProductID','quantity':'Avg_Qty_Per_Day'}, inplace = True)

    return avg_qty_per_day[['ProductID', 'Avg_Qty_Per_Day','days_until_empty']]


def show_update_inventory_show():

    try:

        # Connect to the inventory_report database
        inv_conn = sqlite3.connect(Inventory_report_db_path)

        # Connect to the product_details database
        pro_conn = sqlite3.connect(Product_report_db_path)

        # Define the SQL query to fetch data from the inventory_report database
        query1 = '''
        SELECT ProductID, Platform, Inventory, TInventory, Benchmark
        FROM inventory_report
        GROUP BY ProductID, Platform
        '''

        # Define the SQL query to fetch data from the product_details database
        query2 = '''
        SELECT ProductID, SubTitle
        FROM product_details
        '''

        # Execute the queries and read the results into Pandas DataFrames
        df1 = pd.read_sql_query(query1, inv_conn)
        df2 = pd.read_sql_query(query2, pro_conn)

        # Merge the DataFrames on the ProductID column
        merged = pd.merge(df1, df2, on='ProductID', how='left')

        # merged.to_csv('merge_the_df_to_show_on_html.csv', index=False)

        # Pivot the table to display inventory by platform
        pivot = pd.pivot_table(merged, index=['ProductID', 'SubTitle', 'Benchmark', 'TInventory'],
                            columns='Platform', values='Inventory', fill_value=0)
        
        # pivot.to_csv('pivot_the_df_to_show_on_html.csv', index=False)

        # Compute the sum of each row and add it as a new column
        output = pivot.assign(Total=pivot.sum(axis=1))

        # Reset the index to flatten the table
        output = output.reset_index()

        df_days_left = estimate_stock_over()

        # df_days_left.rename(columns = {'productid':'ProductID'}, inplace = True)

        merged = pd.merge(output, df_days_left, on='ProductID', how='left')

        final_df = merged.sort_values(by=['days_until_empty'])

        # Convert the DataFrame to a list of dictionaries
        rows = final_df.to_dict('records')

        # Render the template with the rows
        return rows
    
    except Exception as e:
        logger.info('Error while showing inventory %s', e)

        return None


def UpdateInventory():

    data = request.get_json()
    product_id = data['ProductId']
    inventory_updates = {
        'A': data.get('A'),
        'F': data.get('F'),
        'M': data.get('M'),
        'SD' : data.get('SD'), 
        'AJ' : data.get ('AJ'),
        'JM' : data.get('JM'),
        'NK' : data.get('NK'),
        'TQ' : data.get('TQ')
    }


    logger.info('Updating Inventory for corresponding platforms: %s', inventory_updates)

    benchmark = data['Benchmark']

    try:
        conn = sqlite3.connect(Inventory_report_db_path)
        cur = conn.cursor()

        # Check if a row corresponding to the product_id and platform exists in the database
        for platform, qty in inventory_updates.items():
            if qty != '':
                cur.execute(f"SELECT * FROM inventory_report WHERE ProductID = '{product_id}' AND Platform = '{platform}'")
                row = cur.fetchone()
                if row is None:
                    return jsonify({'status': 'Error', 'message': f'No row exists for ProductID: {product_id} and Platform: {platform}. Please adjust your inventory to other platforms'})
                
                cur.execute(f"UPDATE inventory_report SET Inventory = {int(qty)}, Benchmark = {int(benchmark)} WHERE ProductID = '{product_id}' AND Platform = '{platform}'")

        # Set the benchmark same for all platforms of the product_id
        cur.execute(f"UPDATE inventory_report SET Benchmark = {int(benchmark)} WHERE ProductID = '{product_id}'")

        # Update the TInventory column based on the sum of inventory with respect to product id and distinct platform
        # Update the TInventory column
        cur.execute('''UPDATE inventory_report 
                    SET TInventory = (SELECT SUM(Inventory) 
                                    FROM (SELECT DISTINCT Platform, Inventory 
                                            FROM inventory_report 
                                            WHERE ProductID = ?) 
                                    AS distinct_platforms) 
                    WHERE ProductID = ?''', (product_id, product_id))



        conn.commit()
        conn.close()

        logger.info('Inventory Updated Successfully for corresponding platforms')
        
        return jsonify({'status': 'Success', 'message': 'Inventory Updated Successfully, Please refresh the page'})

    except Exception as e:
        # print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

        logger.error('Error while Updating Inventory for corresponding platforms: %s', e)
        
        return jsonify({'status': 'Error', 'message': f'Changed were not recorded because{e}'})



def AddInventoryM():

    try:

        productid = request.form.get("productid")
        subtitle = request.form.get("subtitle")
        manufacturer = request.form.get("manufacturer")
        quantity = request.form.get("quantity")
        current_date = datetime.today().date()

        # define the name of the database and table
        DATABASE_NAME = InventoryM_report_db_path
        TABLE_NAME = "InventoryM_report"

        # create a connection to the database
        conn = sqlite3.connect(DATABASE_NAME)

        # create a cursor object to execute SQL commands
        cursor = conn.cursor()

        # create the table if it doesn't exist
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                productid TEXT,
                subtitle TEXT,
                manufacturer TEXT,
                quantity INTEGER,
                date TEXT,
                inv_updt_status INTEGER DEFAULT 0

            )
        """
        cursor.execute(create_table_sql)

        # Insert data into "manufactures" table
        cursor.execute("INSERT INTO InventoryM_report (productid, subtitle, manufacturer, quantity, date) VALUES (?, ?, ?, ?, ?)", (productid, subtitle, manufacturer, quantity, current_date))
        
        conn.commit()
        conn.close()

        msg = 'Manufacture Inventory has been added, Please refresh and check the UPDATE tab'

        logger.info('Manufacture Inventory has been added')

        return jsonify({"status": "success", "message": msg})


    except Exception as e:
        msg = 'Manufacture Inventory not added'
        logger.error(f'Manufacture Inventory not added because {e}')
        return jsonify({"status": "success", "message": msg})




def m_inventory_show():

    # Connect to the inventory_report database
    conn1 = sqlite3.connect(InventoryM_report_db_path)

    # Define the SQL query to fetch data from the inventory_report database
    query1 = '''
    SELECT * FROM InventoryM_report
    '''

    # Execute the queries and read the results into Pandas DataFrames
    df1 = pd.read_sql_query(query1, conn1)

    # df1.drop('inv_updt_status', axis='columns', inplace=True)

    df1 = df1.sort_values(by=['date'],  ascending=False)


    # Convert the DataFrame to a list of dictionaries
    m_invt = df1.to_dict('records')

    # Render the template with the rows
    return m_invt



def InvtUpdateApprove():


    if request.method == 'POST':
        productid = request.form.get("u_productId")
        manufacturer = request.form.get("u_manufacturer")
        quantity = request.form.get("u_quantity")


        logger.info('Updating Manufacture Inventory to Inventory db with values %s, %s, %s', productid, manufacturer, quantity)

        
        inventory_updates = {
        'A': int(request.form.get('u_Amazon')),
        'F': int(request.form.get('u_Flipkart')),
        'M': int(request.form.get('u_Myntra')),
        'SD' : int(request.form.get('u_Snapdeal')), 
        'AJ' : int(request.form.get('u_Ajio')),
        'JM' : int(request.form.get('u_JioMart')),
        'NK' : int(request.form.get('u_Nykaa')),
        'TQ' : int(request.form.get('u_TatacliQ')),
        }

        try:
            conn = sqlite3.connect(Inventory_report_db_path)
            cur = conn.cursor()

            # Check if a row corresponding to the product_id and platform exists in the database
            for platform, qty in inventory_updates.items():
                if qty != 0:
                    cur.execute(f"SELECT * FROM inventory_report WHERE ProductID = '{productid}' AND Platform = '{platform}'")
                    row = cur.fetchone()
                    if row is None:
                        return jsonify({'status': 'error_t', 'message': f'No row exists for ProductID: {productid} for Platform: {platform}. Please adjust your inventory to other platforms'})
                    
                    cur.execute(f"UPDATE inventory_report SET Inventory = Inventory + {int(qty)} WHERE ProductID = '{productid}' AND Platform = '{platform}'")

            # Update the TInventory column based on the sum of inventory with respect to product id and distinct platform
            cur.execute('''UPDATE inventory_report 
                        SET TInventory = (SELECT SUM(Inventory) 
                                        FROM (SELECT DISTINCT Platform, Inventory 
                                                FROM inventory_report 
                                                WHERE ProductID = ?) 
                                        AS distinct_platforms) 
                        WHERE ProductID = ?''', (productid, productid))
            
            logger.info('Manufacture Inventory has been updated to Inventory db')

            
            conn_int_m = sqlite3.connect(InventoryM_report_db_path)
            conn_int_m.execute("UPDATE InventoryM_report SET inv_updt_status = 1 WHERE productid =? AND manufacturer =? AND quantity = ?", (productid,manufacturer,quantity))

            logger.info('inv_updt_status value is set to 1 in the InventoryM_report db')

            conn_int_m.commit()

            conn.commit()
            conn.close()
            conn_int_m.close()
            
            return jsonify({'status': 'success', 'message': 'Inventory Updated Successfully, Please refresh the page'})

        except Exception as e:
            logger.error(f'Inventory not updated because {e}')
            return jsonify({'status': 'error', 'message': f'Changes were not recorded becasue {e}'})
 

def InventoryChangeTab():

    functionName = request.args.get('functionName')
    if functionName == 'show_update_inventory':
        InventoryHome()
    else:
        return 'Error'
    return 'Success'   

def one_week_order_summary():

    order_report_conn = sqlite3.connect(Order_report_db_path)

    conn_product = sqlite3.connect(Product_report_db_path)
    cursor_product = conn_product.cursor()

     # Query the Product database to retrieve the subtitle names
    cursor_product.execute('SELECT ProductID, SubTitle FROM product_details')
    product_data = cursor_product.fetchall()

     # Create a dictionary to map product IDs to subtitle names
    product_map = {row[0]: row[1] for row in product_data}

    # Get the orders from the past one week
    one_week_ago = datetime.now() - timedelta(days=7)
    query = f"SELECT * FROM order_report WHERE order_date >= '{one_week_ago.strftime('%Y-%m-%d')}'"
    order_report = pd.read_sql_query(query, order_report_conn)

    summary = order_report.groupby(['order_date', 'platform', 'productid'])['quantity'].sum().reset_index()
    summary = summary.sort_values(by='platform')

    # Create the dictionary with order_date as key and platform/quantity as value
    result_dict = {}
    for _, row in summary.iterrows():
        order_date = row['order_date']
        order_date = datetime.strptime(order_date, '%Y-%m-%d').strftime('%d %B %Y')
        platform = row['platform']
        productid = row['productid']
        quantity = row['quantity']

        subtitle = product_map.get(productid, '')

        if order_date in result_dict:
            if platform in result_dict[order_date]:
                if subtitle in result_dict[order_date][platform]:
                    result_dict[order_date][platform][subtitle] += quantity
                else:
                    result_dict[order_date][platform][subtitle] = quantity
                result_dict[order_date][platform]['sum'] += quantity
            else:
                result_dict[order_date][platform] = {subtitle: quantity, 'sum': quantity}
        else:
            result_dict[order_date] = {platform: {subtitle: quantity, 'sum': quantity}}

    sorted_result = dict(sorted(result_dict.items(), key=lambda x: x[0], reverse=True))

         # Sort the result based on quantity for each product ID
    for order_date, data in sorted_result.items():
        for platform, values in data.items():
            sorted_result[order_date][platform] = dict(sorted(values.items(), key=lambda x: x[1], reverse=True))


    # Calculate the total quantity for each order_date
    for order_date, data in sorted_result.items():
        total_quantity = sum([platform_data['sum'] for platform_data in data.values()])
        sorted_result[order_date]['sum'] = total_quantity



    return sorted_result

    