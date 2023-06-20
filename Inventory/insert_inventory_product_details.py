import pandas as pd
import sqlite3
import os


# When need to add additional platform data


def download_and_format_inventory_report():

    SHEET_ID = '1hnzzEf0SAyferMJIWvm6pa_TA5O3BX-0051Q0M_XMcs'
    SHEET_NAME = 'Sheet2'
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'

    product_report = pd.read_csv(url)

    product_report.columns = product_report.columns.str.replace(' ', '')
    product_report.rename(columns = {'SKUAmazon':'Amazon'}, inplace = True)

    inventory_report = product_report[['ProductID','AmazonLG','Inventory','Benchmark', 'InvAddStatus']]
    inventory_report.rename(columns = {'AmazonLG':'A_LG'}, inplace = True)


    inventory_report.fillna(0, inplace=True)

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
        get_platform(inventory_report.iloc[i], c) for i in range(len(inventory_report)) for c in inventory_report.columns[1:11]
    ])



    # Read the sku_platformid
    sku_platformid = pd.read_csv('../inventory_reports/inventory_report_M_NK_AJ_SD.csv')

    # Merge the inventory report with the sku_platformid on the 'SKU' column
    final_inventory_reports = pd.merge(final_inventory_reports, sku_platformid[['SKU', 'PlatformID', 'Platform']], on=['SKU', 'Platform'], how='left')

    final_inventory_reports = final_inventory_reports.fillna(value=0.0)

    # print(final_inventory_reports.head(10))


    return final_inventory_reports


def update_inventory_details(inventory_report):
    # Define the name of the database and table
    DATABASE_NAME = 'D:\LW\LWEcommerceManagement\Database\Inventory.db'  # Replace with the actual path
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
    print('done')
    

    

inventory_report= download_and_format_inventory_report()

update_inventory_details(inventory_report)