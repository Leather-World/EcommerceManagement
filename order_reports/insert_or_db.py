import pandas as pd
import sqlite3
from dateutil import parser


def format_order_reports(result):

    print(result)

    order_report = []

    for platform, url in result.items():

        print(platform, url)

    
        if platform == 'amazon_dor' and url != '':
            amazon_order_report = pd.read_csv(url)
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

            # logger.info('Amazon OR: %s' , amazon_order_report.head(2))
            order_report.append(amazon_order_report)

        if platform == 'amazon_lg_dor' and url != '':
            amazon_lg_order_report = pd.read_csv(url)
            
            amazon_lg_order_report = amazon_lg_order_report[['amazon-order-id','purchase-date','sku','quantity','order-status','asin']]
            amazon_lg_order_report.rename(columns = {'amazon-order-id':'order_id','purchase-date':'order_date','asin':'platformID'}, inplace = True)
            amazon_lg_order_report = amazon_lg_order_report[~amazon_lg_order_report['order-status'].isin(['Cancelled'])]
            amazon_lg_order_report.drop(['order-status'], axis=1,  inplace=True)
            # convert the purchase-date column to a datetime object
            amazon_lg_order_report['order_date'] = pd.to_datetime(amazon_lg_order_report['order_date'])
            # extract the date from the datetime object
            amazon_lg_order_report['order_date'] = amazon_lg_order_report['order_date'].dt.strftime('%Y-%m-%d')

            # amazon_lg_order_report['order_date'] = amazon_lg_order_report['order_date'].dt.date
            amazon_lg_order_report['platform'] = 'A_LG'

            print(amazon_lg_order_report.head(5))

            order_report.append(amazon_lg_order_report)

        if platform == 'flipkart_dor' and url != '':
            flipkart_order_report = pd.read_csv(url)
            flipkart_order_report = flipkart_order_report[['order_id','order_date','sku','quantity','order_item_status','fsn']]
            flipkart_order_report.rename(columns = {'fsn':'platformID'}, inplace = True)
            flipkart_order_report['order_item_status'].unique()
            flipkart_order_report = flipkart_order_report[~flipkart_order_report['order_item_status'].isin(['CANCELLED'])]
            flipkart_order_report.drop(['order_item_status'], axis=1,  inplace=True)

            flipkart_order_report['sku'] = flipkart_order_report['sku'].str.split(':').str[1].str.rstrip('"')

            # convert the purchase-date column to a datetime object
            flipkart_order_report['order_date'] = pd.to_datetime(flipkart_order_report['order_date'])
            # extract the date from the datetime object
            # flipkart_order_report['order_date'] = flipkart_order_report['order_date'].dt.date

            # flipkart_order_report = flipkart_order_report['order_date'].split(' ')[0]
            flipkart_order_report['order_date'] = flipkart_order_report['order_date'].astype(str).str.split(' ').str[0]

            # flipkart_order_report['order_date'] = flipkart_order_report['order_date'].dt.strftime('%Y-%m-%d')

            flipkart_order_report['platform'] = 'F'

            order_report.append(flipkart_order_report)
            print(flipkart_order_report.head(5))


        if platform == 'myntra_dor' and url != '':
            myntra_order_report = pd.read_csv(url)
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

            order_report.append(myntra_order_report)

        
        if platform == 'ajio_dor' and url != '':
            ajio_order_report = pd.read_csv(url)
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

            order_report.append(ajio_order_report)

            print(ajio_order_report.head(5))



        if platform == 'snapdeal_dor' and url != '':
            snapdeal_order_report = pd.read_csv(url)
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

            order_report.append(snapdeal_order_report)
            print(snapdeal_order_report.head(5))


        if platform == 'tataq_dor' and url != '':
            tataq_order_report = pd.read_csv(url)

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

            order_report.append(tataq_order_report)

            print(tataq_order_report.head(5))


    final_order_report = pd.concat(order_report, keys=['order_id', 'order_date', 'sku', 'quantity', 'platformID', 'platform'])
    final_order_report = final_order_report.sort_values(by='order_date')
    final_order_report.to_csv('final_order_report_flipkart.csv', index=False)
    

    return final_order_report   
    


report_path = {
# 'amazon_dor':'D:/LW/LWEcommerceManagement/order_reports/May-June/amazon.csv',
            #    'amazon_lg_dor':'D:/LW/LWEcommerceManagement/order_reports/amazon_lg_may_june.csv',
 'flipkart_dor':'D:/LW/LWEcommerceManagement/order_reports/flipkart.csv',
#  'ajio_dor':'D:/LW/LWEcommerceManagement/order_reports/May-June/ajio.csv',
#  'snapdeal_dor':'D:/LW/LWEcommerceManagement/order_reports/May-June/snapdeal.csv',
#  'myntra_dor':'D:\LW\LWEcommerceManagement\order_reports\May-June\myntra.csv',
#  'tataq_dor':'D:/LW/LWEcommerceManagement/order_reports/May-June/tata1.csv'
}

def insert_dor():
    # read the order report CSV file
    order_report = pd.read_csv("final_order_report_flipkart.csv")
    order_report.drop_duplicates(keep='first', inplace=True)

    # define the name of the databases and tables
    order_report_db = "../Database/Order.db"
    inventory_report_db = "../Database/Inventory.db"
    order_report_table = "order_report"
    inventory_report_table = "inventory_report"

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

    # create a connection to the inventory report database
    inventory_conn = sqlite3.connect(inventory_report_db)

    # create a cursor object to execute SQL commands
    inventory_cursor = inventory_conn.cursor()

    sku_not_found = []

    # loop over each row in the order report dataframe
    for index, row in order_report.iterrows():
        # fetch the productid from the inventory report table using sku
        fetch_productid_sql = f"SELECT ProductID FROM {inventory_report_table} WHERE SKU = ?"
        inventory_cursor.execute(fetch_productid_sql, (row["sku"],))
        productid = inventory_cursor.fetchone()

        if productid:
            productid = productid[0]
        else:
            productid = None
            sku_not_found.append(row)

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
                productid,
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
                productid
            ))

    sku_not_found_df = pd.DataFrame(sku_not_found)

    # save the DataFrame to a file (e.g., CSV)
    sku_not_found_df.to_csv('sku_not_found_may.csv', index=False)

    # commit the changes and close the connections
    order_conn.commit()
    order_conn.close()
    inventory_conn.close()

# format_order_reports(report_path)
insert_dor()