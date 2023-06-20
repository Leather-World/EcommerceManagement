import sqlite3

conn = sqlite3.connect('D:\LW\LWEcommerceManagement\Database\Inventory.db')
cur = conn.cursor()

# Set the benchmark to 100 for all ProductID entries
cur.execute("UPDATE inventory_report SET Benchmark = 100")


# Get distinct ProductIDs
cur.execute("SELECT DISTINCT ProductID FROM inventory_report")
product_ids = cur.fetchall()

# Update TInventory column for each ProductID
for product_id in product_ids:
    product_id = product_id[0]  # Extract the ProductID from the fetched tuple

    cur.execute('''UPDATE inventory_report 
                    SET TInventory = (SELECT SUM(Inventory) 
                                    FROM (SELECT DISTINCT Platform, Inventory 
                                            FROM inventory_report 
                                            WHERE ProductID = ?) 
                                    AS distinct_platforms) 
                    WHERE ProductID = ?''', (product_id, product_id))

# Commit the changes to the database
conn.commit()

# Close the connection
conn.close()
