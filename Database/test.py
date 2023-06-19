import sqlite3
from datetime import datetime


# Connect to the database
conn = sqlite3.connect('Order.db')
cursor = conn.cursor()

# Update the rows
cursor.execute("UPDATE order_report SET inv_updt_status = 1")


# Delete rows with order_date as "2023-05-30" or "2023-05-29"
# delete_query = "DELETE FROM order_report WHERE order_date IN (?, ?)"
# order_dates = ('2023-05-30', '2023-05-29')
# cursor.execute(delete_query, order_dates)

# # Delete rows with order_date between '2023-05-13' and '2023-05-29'
# delete_query = "DELETE FROM order_report WHERE order_date BETWEEN ? AND ?"
# start_date = '2023-05-13'
# end_date = '2023-05-29'
# cursor.execute(delete_query, (start_date, end_date))



# cursor.execute("SELECT order_id, return_date FROM return_report")
# rows = cursor.fetchall()

# for row in rows:
#     row_id = row[0]
#     old_date = row[1]
    
#     # Convert the date to the desired format
#     try:
#         new_date = datetime.strptime(old_date, '%Y-%m-%d').strftime('%Y-%m-%d')
#     except ValueError:
#         new_date = datetime.strptime(old_date, '%d-%m-%Y').strftime('%Y-%m-%d')
    
#     # Update the row in the database
#     cursor.execute("UPDATE return_report SET return_date = ? WHERE order_id = ?", (new_date, row_id))


# Commit the changes
conn.commit()

# Close the connection
conn.close()


