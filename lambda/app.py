import sys
import os
import logging
import pymysql
import json

# Environment variables
rds_host, rds_port = os.environ['rds_endpoint'].split(":")
db_user = os.environ['db_username']
db_password = os.environ['db_password']
db_name = "DBLAMBDAMETRICS"

# Logger configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Connect to RDS instance
try:
    conn = pymysql.connect(host=rds_host, user=db_user, passwd=db_password, db=db_name, connect_timeout=5)
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
except Exception as e:
    logger.error(f"ERROR: Unable to connect to RDS MySQL instance: {e}")
    sys.exit()

# Lambda handler function
def handler(event, context):
    try:
        # Execute SQL query to create table if not exists
        with conn.cursor() as cursor:
            create_table_query = "CREATE TABLE IF NOT EXISTS mytable2 (customer_name VARCHAR(255), customer_id VARCHAR(255), payment_method VARCHAR(255))"
            logger.info(f"Executing SQL query: {create_table_query}")
            cursor.execute(create_table_query)
            conn.commit()

            # Sample data to insert into the table
            sample_data = [
                ("John Doe", "12345", "Credit Card"),
                ("Jane Smith", "67890", "PayPal"),
                ("Alice Johnson", "54321", "Debit Card"),
                
            ]

            # Execute SQL query to insert sample data into the table
            for data in sample_data:
                insert_query = "INSERT INTO mytable2 (customer_name, customer_id, payment_method) VALUES (%s, %s, %s)"
                logger.info(f"Executing SQL query: {insert_query} with data: {data}")
                cursor.execute(insert_query, data)
            conn.commit()

        # Execute SQL query to retrieve data from table
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM mytable2")
            rows = cursor.fetchall()
            logger.info(f"Fetched rows: {rows}")

        # Prepare response body with retrieved data
        response_body = {
            "message": "Data retrieved from RDS MySQL instance",
            "data": []
        }

        # Append each row of data to the response body
        for row in rows:
            response_body["data"].append({"customer_name": row[0], "customer_id": row[1], "payment_method": row[2]})

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response_body, indent=2)
        }

    except Exception as e:
        logger.error(f"ERROR: An unexpected error occurred: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal Server Error"})
        }
