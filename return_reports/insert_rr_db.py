import pandas as pd
import sqlite3



def insert_rr():
    # read the return report CSV file
    return_report = pd.read_csv("ne/final_return_report.csv")

    # define the name of the databases and tables
    return_report_db = "../Database/Return.db"
    inventory_report_db = "../Database/Inventory.db"

    return_report_table = "return_report"
    inventory_report_table = "inventory_report"

    # create a connection to the return report database
    return_conn = sqlite3.connect(return_report_db)

    # create a cursor object to execute SQL commands
    return_cursor = return_conn.cursor()

    # create the daily return report table if it doesn't exist
    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {return_report_table} (
            order_id TEXT PRIMARY KEY,
            return_date TEXT,
            tracking_id TEXT,
            platformID TEXT,
            sku TEXT,
            return_reason TEXT,
            return_sub_reason TEXT,
            return_delivery_date TEXT,
            platform TEXT,
            reason_category TEXT,
            productid TEXT
        )
    """
    return_cursor.execute(create_table_sql)

    # create a connection to the inventory report database
    inventory_conn = sqlite3.connect(inventory_report_db)

    # create a cursor object to execute SQL commands
    inventory_cursor = inventory_conn.cursor()

    sku_not_found = []

    # fetch the productid and platformID from the inventory report table using sku or platformID
    fetch_productid_sql = f"SELECT ProductID, PlatformID FROM {inventory_report_table} WHERE SKU = ? OR PlatformID = ?"
    inventory_cursor.execute(fetch_productid_sql, (None, None))

    productid_platformid_map = {}
    for productid, platformid in inventory_cursor.fetchall():
        productid_platformid_map[platformid] = productid

    # loop over each row in the return report dataframe
    for index, row in return_report.iterrows():
        sku = row["sku"]
        platformid = row["platformID"]

        # fetch the productid from the inventory report table using sku or platformID
        if sku == '0':
            inventory_cursor.execute(fetch_productid_sql, (None, platformid))

        else:
            inventory_cursor.execute(fetch_productid_sql, (sku, None))


        productid = None
        for result in inventory_cursor.fetchall():
            if sku and result[0]:
                productid = result[0]
                break
            elif not sku and result[1]:
                platformid = result[1]
                productid = productid_platformid_map.get(platformid)
                break

        if not productid:
            sku_not_found.append(row)


        # check if the order_id already exists in the daily return report database
        check_sql = f"SELECT * FROM {return_report_table} WHERE order_id = ?"
        return_cursor.execute(check_sql, (row["order_id"],))
        existing_data = return_cursor.fetchone()

        if existing_data:
            # if the return_id already exists, update the row
            update_sql = f"""
                UPDATE {return_report_table}
                SET return_date = ?,
                    tracking_id = ?,
                    platformID = ?,
                    sku = ?,
                    return_reason = ?,
                    return_sub_reason = ?,
                    return_delivery_date = ?,
                    platform = ?,
                    reason_category = ?,
                    productid = ?

                WHERE order_id = ?
            """
            return_cursor.execute(update_sql, (
                row["return_date"],
                row["tracking_id"],
                row["platformID"],
                row["sku"],
                row["return_reason"],
                row["return_sub_reason"],
                row["return_delivery_date"],
                row["platform"],
                row["reason_category"],
                productid,
                row["order_id"]

            ))
        else:
            # if the return_id does not exist, insert the row
            insert_sql = f"""
                INSERT INTO {return_report_table} (order_id, return_date, tracking_id, platformID, sku, return_reason,return_sub_reason, return_delivery_date,platform,reason_category,productid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ? ,? ,?)
            """
            return_cursor.execute(insert_sql, (
                row["order_id"],
                row["return_date"],
                row["tracking_id"],
                row["platformID"],
                row["sku"],
                row["return_reason"],
                row["return_sub_reason"],
                row["return_delivery_date"],
                row["platform"],
                row["reason_category"],
                productid
            ))

    sku_not_found_df = pd.DataFrame(sku_not_found)

    # save the DataFrame to a file (e.g., CSV)
    sku_not_found_df.to_csv('sku_not_found.csv', index=False)

    # commit the changes and close the connections
    return_conn.commit()
    return_conn.close()
    inventory_conn.close()

insert_rr()