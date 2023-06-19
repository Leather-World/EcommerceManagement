import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('Inventory.db')
cursor = conn.cursor()

# Retrieve the distinct ProductID and Platform combinations from the table
cursor.execute("SELECT DISTINCT ProductID, Platform FROM inventory_report")
rows = cursor.fetchall()

# Create a dictionary to store the ProductID and corresponding SKU for each platform
product_dict = {}
for row in rows:
    product_id = row[0]
    platform = row[1]

    # Retrieve the SKUs for the current ProductID and Platform combination
    cursor.execute("SELECT SKU FROM inventory_report WHERE ProductID = ? AND Platform = ?", (product_id, platform))
    sku_rows = cursor.fetchall()
    skus = [sku[0] for sku in sku_rows]

    # Add the platform and SKUs to the dictionary
    if product_id in product_dict:
        product_dict[product_id][platform] = skus
    else:
        product_dict[product_id] = {platform: skus}

# Close the database connection
conn.close()

# Create a dataframe from the dictionary
df = pd.DataFrame.from_dict(product_dict, orient='index')

# Move the index as a column
df.reset_index(inplace=True)

# Name the first column as 'ProductID'
df.rename(columns={'index': 'ProductID'}, inplace=True)


# Remove square brackets '[' and ']' from values
df = df.applymap(lambda x: ', '.join(x) if isinstance(x, list) else x)
# Fill NaN values with an empty string
df.fillna('', inplace=True)

# Print the resulting dataframe
print(df.head(5))


# Connect to the product_details database
conn2 = sqlite3.connect('Product.db')

    # Define the SQL query to fetch data from the product_details database
query2 = '''
SELECT ProductID, SubTitle, ImgURL
FROM product_details
'''

# Execute the queries and read the results into Pandas DataFrames
df2 = pd.read_sql_query(query2, conn2)

merged = pd.merge(df, df2, on='ProductID')




print(merged.head(5))
