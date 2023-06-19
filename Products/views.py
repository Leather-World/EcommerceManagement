from flask import json, request, render_template,redirect, url_for, session ,jsonify
import pandas as pd
from datetime import datetime, timedelta

import sqlite3
import os

Inventory_report_db_path = os.path.join(os.getcwd(), 'Database', 'Inventory.db')
InventoryM_report_db_path = os.path.join(os.getcwd(), 'Database', 'InventoryM.db')
Order_report_db_path = os.path.join(os.getcwd(),'Database', 'Order.db')
Product_report_db_path = os.path.join(os.getcwd(),'Database', 'Product.db')
Return_report_db_path = os.path.join(os.getcwd(),'Database', 'Return.db')


platforms = {'A' : 'Amazon',
                'F': 'Flipkart',
                'M': 'Myntra',
                'SD':'Snapdeal',
                'AJ': 'Ajio',
                'TQ': 'TataClicQ'}

backgroundColor = [
        'rgba(255, 153, 0, 0.2)',
    'rgba(54, 162, 235, 0.2)',
    'rgba(243, 25, 176, 0.2)',
    'rgba(227, 0, 71, 0.2)',
    'rgba(73, 99, 121, 0.2)',
    'rgba(171, 30, 64, 0.2)'
    ]
borderColor = [
        'rgba(255, 153, 0, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(243, 25, 176, 1)',
    'rgba(227, 0, 71, 1)',
    'rgba(73, 99, 121, 1)',
    'rgba(171, 30, 64, 1)'
    ]


def check_user():
    if 'user' not in session:
        return redirect(url_for('login'))


def ProductHome():
    check_user()

    return render_template('/productSite/productHome.html')


def ProductDB():

    OrderReport_LG = productdb_OR_line_graph()

    chart_data_RR  = generate_return_count_line_graph()

    top_medium_low_data, product_categories = top_medium_low_product()

    labels, first_15_days_quantities, second_15_days_quantities, platforms = productid_p_comparison()

    chart_data_return_report_pa = generate_return_category_PA_graph()


    return render_template('/productSite/productdb.html',top_medium_low_data=top_medium_low_data,platforms=platforms, 
                           chart_data_OR=json.dumps(OrderReport_LG),chart_data_return_report_pa=chart_data_return_report_pa, 
                           chart_data_RR=chart_data_RR,product_categories=product_categories,
                           labels=labels, first_15_days_quantities=first_15_days_quantities, 
                           second_15_days_quantities=second_15_days_quantities)

def productdb_OR_line_graph():
    conn = sqlite3.connect(Order_report_db_path)
    cur = conn.cursor()

    return_conn = sqlite3.connect(Return_report_db_path)
    return_cur = return_conn.cursor()

    chart_data = {}

    today = datetime.today().date()
    four_months_ago = today - timedelta(days=120)  # Assuming 30 days per month
    

    for platform in platforms.keys():

        query = "SELECT order_date, SUM(quantity) FROM order_report WHERE platform = ? AND order_date >= ? GROUP BY order_date"
        cur.execute(query, (platform, four_months_ago))
        order_data = cur.fetchall()

        query = "SELECT return_date, COUNT(*) FROM return_report WHERE platform = ? AND return_date >= ? GROUP BY return_date"
        return_cur.execute(query, (platform, four_months_ago))
        return_data = return_cur.fetchall()

        # Create a set of all dates within the range
        date_range = set()
        for row in order_data:
            date_range.add(row[0])
        for row in return_data:
            date_range.add(row[0])

        # Sort the date range
        sorted_dates = sorted(date_range)

        # Fill missing dates with 0 values
        filled_order_data = []
        filled_return_data = []
        for date in sorted_dates:
            order_quantity = next((row[1] for row in order_data if row[0] == date), 0)
            filled_order_data.append((date, order_quantity))
            return_quantity = next((row[1] for row in return_data if row[0] == date), 0)
            filled_return_data.append((date, return_quantity))

        if filled_order_data:
            filled_order_data.sort(key=lambda x: x[0])
            labels = [row[0] for row in filled_order_data]
            order_dataset = {
                'label': platforms[platform] + ' - Order Quantity',
                'data': [row[1] for row in filled_order_data],
                'backgroundColor': backgroundColor[list(platforms.keys()).index(platform)],
                'borderColor': borderColor[list(platforms.keys()).index(platform)],
                'borderWidth': 2
            }
            if platform in chart_data:
                chart_data[platform]['labels'].extend(labels)
                chart_data[platform]['datasets'].append(order_dataset)
            else:
                chart_data[platform] = {'labels': labels, 'datasets': [order_dataset]}

        if filled_return_data:
            filled_return_data.sort(key=lambda x: x[0])
            return_dataset = {
                'label': platforms[platform] + ' - Return Quantity',
                'data': [row[1] for row in filled_return_data],
                'backgroundColor': 'rgba(255, 26, 104, 0.2)',
                'borderColor': 'rgba(255, 26, 104, 1)',
                'borderWidth': 1
                # 'borderDash': [5, 5],
            }
            if platform in chart_data:
                chart_data[platform]['datasets'].append(return_dataset)
            else:
                chart_data[platform] = {'datasets': [return_dataset]}

    conn.close()

    return chart_data



def generate_return_count_line_graph():

    return_conn = sqlite3.connect(Return_report_db_path)
    return_cur = return_conn.cursor()

    conn_product = sqlite3.connect(Product_report_db_path)
    cursor_product = conn_product.cursor()

    cursor_product.execute('SELECT ProductID, SubTitle FROM product_details')
    product_data = cursor_product.fetchall()

    # Create a dictionary to map product IDs to subtitle names
    product_map = {row[0]: row[1] for row in product_data}

    chart_data = {}

    today = datetime.today().date()
    four_months_ago = today - timedelta(days=120)  # Assuming 30 days per month

    for platform in platforms.keys():
        query = "SELECT return_date, COUNT(*) FROM return_report WHERE platform = ? AND return_date >= ? GROUP BY return_date"
        return_cur.execute(query, (platform, four_months_ago))
        return_data = return_cur.fetchall()

        if return_data:
            return_data.sort(key=lambda x: x[0])
            return_dataset = {
                'label': platforms[platform] + ' - Return Quantity',
                'data': [row[1] for row in return_data],
                'backgroundColor': backgroundColor[list(platforms.keys()).index(platform)],
                'borderColor': borderColor[list(platforms.keys()).index(platform)],
                'borderWidth': 2
            }
            labels = [row[0] for row in return_data]
            
            # Get tooltip information for each return date
            tooltips = []
            for row in return_data:
                return_date = row[0]
                query = "SELECT productid, return_reason FROM return_report WHERE platform = ? AND return_date = ? AND productid IS NOT NULL"
                return_cur.execute(query, (platform, return_date))
                tooltip_data = return_cur.fetchall()
                tooltip = "Return Date:" + return_date + "\n" + "\n"
                for tooltip_row in tooltip_data:
                    product_id = tooltip_row[0]
                    return_reason = tooltip_row[1]
                    if product_id is not None and return_reason is not None:
                         # Replace the product ID with the subtitle name
                        subtitle = product_map.get(product_id, '')
                        tooltip += str(subtitle) + " - " + return_reason + "\n"
                tooltips.append(tooltip)


            chart_data[platform] = {'labels': labels, 'datasets': [return_dataset], 'tooltips': tooltips}


    return_conn.close()

    return chart_data




def top_medium_low_product():

    conn_order = sqlite3.connect(Order_report_db_path)

    # Define the start and end dates for the past week
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    date_format = '%Y-%m-%d'

    # Parse the start and end dates
    start_date = datetime.strptime(start_date.strftime('%Y-%m-%d'), date_format).date()
    end_date = datetime.strptime(end_date.strftime('%Y-%m-%d'), date_format).date()

    query = f"SELECT * FROM order_report WHERE order_date >= '{start_date}' AND order_date <= '{end_date}'"

    order_report = pd.read_sql_query(query, conn_order)

    # Group the data by 'platform' and 'productid', calculate the sum of 'quantity' for each group
    grouped = order_report.groupby(['platform', 'productid']).agg({'quantity': 'sum'}).reset_index()

    # Define the cutoffs for top, medium, and low selling
    top_cutoff = grouped['quantity'].quantile(0.90)
    low_cutoff = grouped['quantity'].quantile(0.70)

    # Function to categorize the products based on quantity
    def categorize(quantity):
        if quantity >= top_cutoff:
            return 'top selling'
        elif quantity <= low_cutoff:
            return 'low selling'
        else:
            return 'medium selling'

    # Apply the categorize function to create the 'trend_status' column
    grouped['trend_status'] = grouped['quantity'].apply(categorize)

    # Rename the 'quantity' column to 'SumOfQuantity' as mentioned in the desired table
    grouped.rename(columns={'quantity': 'SumOfQuantity'}, inplace=True)


    reorder = ['productid', 'SumOfQuantity', 'platform', 'trend_status']
    grouped = grouped.reindex(columns=reorder)


    conn_product = sqlite3.connect(Product_report_db_path)
    product_report = pd.read_sql_query('SELECT * FROM product_details', conn_product)
    product_report_subset = product_report[['ProductID', 'SubTitle', 'ImgURL', 'ProductCategory']]
    product_report_subset.rename(columns = {'ProductID':'productid'}, inplace = True)

    Top_Medium_Low = pd.merge(grouped[['productid', 'SumOfQuantity', 'platform', 'trend_status']], product_report_subset, on=['productid'], how='left')

    conn_inventory = sqlite3.connect(Inventory_report_db_path)
    invt_report = pd.read_sql_query('SELECT * FROM inventory_report', conn_inventory)
    invt_report_subset = invt_report[['ProductID', 'TInventory']]
    invt_report_subset.rename(columns = {'ProductID':'productid'}, inplace = True)
    invt_report_subset.drop_duplicates(keep='first', inplace=True)


    Top_Medium_Low = pd.merge(Top_Medium_Low, invt_report_subset, on=['productid'], how='left')

    Top_Medium_Low = Top_Medium_Low.sort_values(by=['SumOfQuantity'], ascending=False)




    # Top_Medium_Low.to_csv('top_medium_low.csv', index=False)

    product_categories = Top_Medium_Low['ProductCategory'].unique()


    Top_Medium_Low = Top_Medium_Low.to_dict('records')

    conn_order.close()
    conn_product.close()


    return Top_Medium_Low, product_categories



def productid_p_comparison():
    # Connect to the SQLite database
    conn_order  = sqlite3.connect(Order_report_db_path)
    conn_product = sqlite3.connect(Product_report_db_path)
    cursor_order = conn_order.cursor()
    cursor_product = conn_product.cursor()


    # Query the database to retrieve the quantities for each 15-day period and platform
    cursor_order.execute('''
        SELECT productid,
               platform,
               SUM(CASE WHEN order_date BETWEEN date('now', '-30 days') AND date('now', '-16 days') THEN quantity ELSE 0 END) AS first_15_days,
               SUM(CASE WHEN order_date BETWEEN date('now', '-15 days') AND date('now') THEN quantity ELSE 0 END) AS second_15_days
        FROM order_report
        GROUP BY productid, platform
        HAVING ABS(first_15_days - second_15_days) >= 10
    ''')
    data = cursor_order.fetchall()


    # Query the Product database to retrieve the subtitle names
    cursor_product.execute('SELECT ProductID, SubTitle FROM product_details')
    product_data = cursor_product.fetchall()

    # Get unique platforms from the data
    platforms = list(set(row[1] for row in data))


    # Close the database connections
    conn_order.close()
    conn_product.close()


    # Remove None values from the data
    data = [row for row in data if row[0] is not None]

    # Prepare the data for the bar chart
    labels = []
    first_15_days_quantities = {}
    second_15_days_quantities = {}

    # Create a dictionary to map product IDs to subtitle names
    product_map = {row[0]: row[1] for row in product_data}

    for row in data:
        
        product_id = row[0]
        platform = row[1]


         # Replace the product ID with the subtitle name
        subtitle = product_map.get(product_id, '')
        if subtitle not in labels:
            labels.append(subtitle)

        if subtitle not in first_15_days_quantities:
            first_15_days_quantities[subtitle] = {}

        if subtitle not in second_15_days_quantities:
            second_15_days_quantities[subtitle] = {}

        first_15_days_quantities[subtitle][platform] = row[2]
        second_15_days_quantities[subtitle][platform] = row[3]

    return labels, first_15_days_quantities, second_15_days_quantities, platforms



def ProductSearch():

    # Connect to the SQLite database
    inv_conn = sqlite3.connect(Inventory_report_db_path)
    inv_cursor = inv_conn.cursor()

    # Retrieve the distinct ProductID and Platform combinations from the table
    inv_cursor.execute("SELECT DISTINCT ProductID, Platform FROM inventory_report")
    rows = inv_cursor.fetchall()

    # Create a dictionary to store the ProductID and corresponding SKU for each platform
    product_dict = {}
    for row in rows:
        product_id = row[0]
        platform = row[1]

        # Retrieve the SKUs for the current ProductID and Platform combination
        inv_cursor.execute("SELECT SKU FROM inventory_report WHERE ProductID = ? AND Platform = ?", (product_id, platform))
        sku_rows = inv_cursor.fetchall()
        skus = [sku[0] for sku in sku_rows]

        # Add the platform and SKUs to the dictionary
        if product_id in product_dict:
            product_dict[product_id][platform] = skus
        else:
            product_dict[product_id] = {platform: skus}

    # Close the database connection
    inv_conn.close()

    # Create a dataframe from the dictionary
    inv_df = pd.DataFrame.from_dict(product_dict, orient='index')

    # Move the index as a column
    inv_df.reset_index(inplace=True)

    # Name the first column as 'ProductID'
    inv_df.rename(columns={'index': 'ProductID'}, inplace=True)


    # Remove square brackets '[' and ']' from values
    inv_df = inv_df.applymap(lambda x: ', '.join(x) if isinstance(x, list) else x)
    # Fill NaN values with an empty string
    inv_df.fillna('', inplace=True)


    # Connect to the product_details database
    product_conn = sqlite3.connect(Product_report_db_path)

        # Define the SQL query to fetch data from the product_details database
    product_query = '''
    SELECT ProductID, SubTitle, ImgURL
    FROM product_details
    '''

    # Execute the queries and read the results into Pandas DataFrames
    product_df = pd.read_sql_query(product_query, product_conn)

    invt_product_merged = pd.merge(inv_df, product_df, on='ProductID')


    # Convert the DataFrame to a list of dictionaries
    rows = invt_product_merged.to_dict('records')

    return render_template('/productSite/productSearch.html', data=rows)

def generate_product_order_graph(product_id):

    print(product_id)
    conn = sqlite3.connect(Order_report_db_path)
    cur = conn.cursor()

    chart_data = {}

    for platform in platforms.keys():
        # print(platform)
        query = "SELECT order_date, SUM(quantity) FROM order_report WHERE productid = ? AND platform = ? GROUP BY order_date"
        cur.execute(query, (product_id, platform))
        data = cur.fetchall()

        if data:
            data.sort(key=lambda x: x[0])
            labels = [row[0] for row in data]
            dataset = {
                'label': platforms[platform],
                'data': [row[1] for row in data],
                'backgroundColor': backgroundColor[list(platforms.keys()).index(platform)],
                'borderColor': borderColor[list(platforms.keys()).index(platform)],
                'borderWidth': 2
            }
            if platform in chart_data:
                chart_data[platform]['labels'].extend(labels)
                chart_data[platform]['datasets'].append(dataset)
            else:
                chart_data[platform] = {'labels': labels, 'datasets': [dataset]}
    
        
    conn.close()

    return chart_data




def Generate_productdb_OR_Polar():

    print('ss')
    # Connect to the database
    conn = sqlite3.connect(Order_report_db_path)
    cursor = conn.cursor()

    order_date = request.form.get('order_date')
    platform = request.form.get('platform')

    # SQL query to retrieve the sum of quantity based on filters
    query = '''
        SELECT productid, SUM(quantity) as total_quantity
        FROM order_report
        WHERE order_date = ? AND platform = ?
        GROUP BY productid
    '''
    cursor.execute(query, (order_date, platform))
    rows = cursor.fetchall()

    data = []
    for row in rows:
        data.append({'productid': row[0], 'quantity': row[1]})

    conn.close()

    return jsonify(data)


def generate_return_category_PA_graph():
    conn = sqlite3.connect(Return_report_db_path)
    cur = conn.cursor()

    conn_product = sqlite3.connect(Product_report_db_path)
    cur_product = conn_product.cursor()

    chart_data = {}

    for platform in platforms.keys():
        query = "SELECT reason_category, COUNT(*) FROM return_report WHERE platform = ? GROUP BY reason_category"
        cur.execute(query, (platform,))
        data = cur.fetchall()

        if data:
            data.sort(key=lambda x: x[0])
            labels = [row[0] for row in data]
            counts = [row[1] for row in data]
            product_info = []

            for label in labels:
                query = "SELECT productid, COUNT(*) FROM return_report WHERE platform = ? AND reason_category = ? GROUP BY productid"
                cur.execute(query, (platform, label))
                product_data = cur.fetchall()

                product_data = [[product_id, count] for product_id, count in product_data if product_id is not None]
                product_data.sort(key=lambda x: x[1], reverse=True)
                top_product_data = product_data[:10]

                # Fetch subtitle from product_details database
                subtitle_info = []
                for product_id, count in top_product_data:
                    cur_product.execute("SELECT SubTitle FROM product_details WHERE ProductID = ?", (product_id,))
                    subtitle = cur_product.fetchone()
                    if subtitle:
                        subtitle_info.append((subtitle[0], count))

                product_info.append(subtitle_info)

            dataset = {
                'label': platforms[platform],
                'data': counts,
                'backgroundColor': backgroundColor,
                'borderColor': borderColor,
                'borderWidth': 2,
                'productInfo': product_info
            }
            chart_data[platform] = {'labels': labels, 'datasets': [dataset]}

    conn.close()
    conn_product.close()

    return chart_data


def generate_product_return_graph(product_id):

    print(product_id)
    conn = sqlite3.connect(Return_report_db_path)
    cur = conn.cursor()

    chart_data = {}

    for platform in platforms.keys():
        # print(platform)
        query = "SELECT reason_category, COUNT(*) FROM return_report WHERE productid = ? AND platform = ? GROUP BY reason_category"
        cur.execute(query, (product_id, platform))
        data = cur.fetchall()

        # print(data)

        if data:
            data.sort(key=lambda x: x[0])
            labels = [row[0] for row in data]
            dataset = {
                'label': platforms[platform],
                'data': [row[1] for row in data],
                'backgroundColor': backgroundColor,
                'borderColor': borderColor,
                'borderWidth': 2
            }
            if platform in chart_data:
                chart_data[platform]['labels'].extend(labels)
                chart_data[platform]['datasets'].append(dataset)
            else:
                chart_data[platform] = {'labels': labels, 'datasets': [dataset]}
    
        
    conn.close()

    return chart_data


def geneate_product_return_line_graph(product_id):

    print(product_id)
    conn = sqlite3.connect(Return_report_db_path)
    cur = conn.cursor()

    chart_data = {}
 

    for platform in platforms.keys():
        # print(platform)
        query = "SELECT return_date, COUNT(*) FROM return_report WHERE productid = ? AND platform = ? GROUP BY return_date"
        cur.execute(query, (product_id, platform))
        data = cur.fetchall()

        if data:
            data.sort(key=lambda x: x[0])
            labels = [row[0] for row in data]
            dataset = {
                'label': platforms[platform],
                'data': [row[1] for row in data],
                'backgroundColor': backgroundColor[list(platforms.keys()).index(platform)],
                'borderColor': borderColor[list(platforms.keys()).index(platform)],
                'borderWidth': 2
            }
            if platform in chart_data:
                chart_data[platform]['labels'].extend(labels)
                chart_data[platform]['datasets'].append(dataset)
            else:
                chart_data[platform] = {'labels': labels, 'datasets': [dataset]}
    
        
    conn.close()

    return chart_data



def ProductPage(product_id):
    # Connect to inventory_report database and retrieve all SKUs for the product_id
    inv_conn = sqlite3.connect(Inventory_report_db_path)
    inv_c = inv_conn.cursor()
    inv_c.execute("SELECT SKU, Platform, PlatformID FROM inventory_report WHERE ProductID=?", (product_id,))
    sku_rows = inv_c.fetchall()
    sku_dict = {}
    # for row in sku_rows:
    #     if row[1] in sku_dict:
    #         sku_dict[row[1]] = sku_dict[row[1]] + ',' + row[0]
    #     else:
    #         sku_dict[row[1]] = row[0]

    sku_dict = {}
    for row in sku_rows:
        if row[1] in sku_dict:
            sku_dict[row[1]]['skus'].append(row[0])
            sku_dict[row[1]]['platform_ids'].append(row[2])
        else:
            sku_dict[row[1]] = {
                'skus': [row[0]],
                'platform_ids': [row[2]]
            }

    # Connect to product_report database and retrieve all data for the product_id
    prod_conn = sqlite3.connect(Product_report_db_path)
    prod_c = prod_conn.cursor()
    prod_c.execute("SELECT * FROM product_details WHERE ProductID=?", (product_id,))
    row = prod_c.fetchone()

    product_details = {
        'id': row[0],
        'Title': row[1],
        'SubTitle': row[2],
        'description': row[3],
        'features': row[4], #row[4].split(',')
        'dimensions': row[5],
        'skus': sku_dict,
        'image_url': row[6]
    }

    chart_data = generate_product_order_graph(product_id)
    chart_data_return = generate_product_return_graph(product_id)
    chart_data_line_return = geneate_product_return_line_graph(product_id)

    # print(chart_data_line_return)

    # print(chart_data_return)

    # Close database connections
    inv_conn.close()
    prod_conn.close()

    return render_template('/productSite/product.html', product=product_details, chart_data=[chart_data, chart_data_return, chart_data_line_return])
