import pandas as pd
import mysql.connector
import os
import requests
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# File paths
csv_file_path = r'C:\\Users\\Catarina8bits\\Documents\\GitHub\\cpostal\\codigos_postais.csv'

# MySQL Database Configuration
db_config = {
    'host': '127.0.0.1',
    'port': "3306",
    'user': 'root',
    'password': 'cata',
    'database': 'postal_db'
}

# CTT API Configuration
CTT_API_URL = "https://www.cttcodigopostal.pt/api/v1"
CTT_API_KEY = "99603d2d326e4e8489f9d2d4d647db4c"

# Validate postal code (Portuguese format ####-###)
def validate_postal_code(postal_code):
    return bool(re.match(r'^\d{4}-\d{3}$', postal_code))

# Read the CSV file
def read_csv_file(csv_file):
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file, encoding='utf-8')
    logging.warning("CSV file does not exist.")
    return pd.DataFrame(columns=['cp7', 'concelho', 'distrito', 'postal_code','municipality','district'])

# Check for postal code in CSV
def check_csv_for_postal_code(csv_df, postal_code):
    return csv_df[csv_df['cp7'] == postal_code] if 'cp7' in csv_df.columns else None

def update_csv(file_path, new_data):
    try:
        if new_data.empty:
            logging.warning("No data to update in the CSV file.")
            return
        
        logging.info("Starting the CSV update process...")

        # Check if the CSV file exists
        if os.path.exists(file_path):
            logging.info("CSV file found. Reading existing data...")
            existing_data = pd.read_csv(file_path, encoding='utf-8')

            # Log the number of existing records
            logging.info(f"Existing CSV records count: {len(existing_data)}")
            logging.info(f"Existing CSV columns: {existing_data.columns.tolist()}")
            logging.info(f"New data columns: {new_data.columns.tolist()}")

            # Normalize column names
            existing_data.columns = existing_data.columns.str.strip().str.lower()
            new_data.columns = new_data.columns.str.strip().str.lower()

            # Check and add missing columns in new_data
            for column in existing_data.columns:
                if column not in new_data.columns:
                    logging.info(f"Adding missing column '{column}' to new data.")
                    new_data[column] = None  # Add missing columns with None values

            # Concatenate existing data with new data and drop duplicates based on 'cp7'
            merged_data = pd.concat([existing_data, new_data], ignore_index=True).drop_duplicates(subset=['cp7'], keep='last')
            logging.info(f"Merged data records count: {len(merged_data)}")
        else:
            # If the CSV file does not exist, use the new data directly
            logging.info("CSV file does not exist. Creating a new file with the new data.")
            merged_data = new_data

        # Write the merged data back to the CSV file
        merged_data.to_csv(file_path, index=False, encoding='utf-8')
        logging.info("CSV file updated successfully.")
        
    except Exception as e:
        logging.error(f"An error occurred while updating the CSV file: {e}")


# Check for postal code in MySQL database
def check_db_for_postal_code(postal_code):
    with mysql.connector.connect(**db_config) as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM postal_codes WHERE postal_code = %s", (postal_code,))
            result = cursor.fetchone()
    return pd.DataFrame([result]) if result else None

# Fetch postal code details from CTT API
def fetch_from_ctt_api(postal_code):
    url = f"{CTT_API_URL}/{CTT_API_KEY}/{postal_code}"
    response = requests.get(url)
    
    # Attempt to parse the response as JSON
    try:
        data = response.json()
    except ValueError:
        logging.error(f"Failed to decode JSON response for postal code {postal_code}. Status code: {response.status_code}")
        return None
    
    # Check if data is not empty and is a list
    if isinstance(data, list) and data:
        records = [{
            'cp7': record.get('codigo-postal'),
            'concelho': record.get('concelho', ''),
            'distrito': record.get('distrito', ''),
        } for record in data if 'codigo-postal' in record]
        
        logging.info(f"Data fetched from CTT API for postal code {postal_code}: {records}")
        print(pd.DataFrame(records))
        return pd.DataFrame(records)
    
    # Log a warning if no data was retrieved despite a successful request
    logging.warning(f"CTT API replied empty, meaning they dont have that postal code {postal_code}. Status code: {response.status_code}")
    return None



# Insert data into MySQL database
def insert_into_db(postal_code_data):
    # Replace NaN values with None
    postal_code_data = postal_code_data.where(pd.notnull(postal_code_data), None)

    if not postal_code_data.empty:
        with mysql.connector.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                query = '''INSERT INTO postal_codes (postal_code, municipality, district)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE 
                            municipality = VALUES(municipality), district = VALUES(district)'''
                for _, row in postal_code_data.iterrows():
                    cursor.execute(query, (row['cp7'], row['concelho'], row['distrito']))
                conn.commit()
                logging.info("Data inserted into MySQL database successfully.")
    else:
        logging.warning("No data to insert into the database.")


#function to handle the process
def find_postal_code_info(postal_code):
    if not validate_postal_code(postal_code):
        logging.error("Invalid postal code format.")
        return
    
    csv_df = read_csv_file(csv_file_path)
    result = check_csv_for_postal_code(csv_df, postal_code)
    
    if result is not None and not result.empty:
        logging.info("Postal code found in CSV!")
        additional_info = fetch_from_ctt_api(postal_code)
        if additional_info is not None:
            result = pd.concat([result, additional_info], ignore_index=True).drop_duplicates()
            insert_into_db(result)
            update_csv(csv_file_path, result)
            return

    # Check MySQL Database
    result = check_db_for_postal_code(postal_code)
    if result is not None and not result.empty:
        logging.info("Postal code found in MySQL database!")
        return
    
    # Fetch from CTT API if not found in CSV or DB
    result = fetch_from_ctt_api(postal_code)
    if result is not None:
        insert_into_db(result)
        update_csv(csv_file_path, result)
    else:
        logging.warning("Postal code not found anywhere.")

# Handle user input for postal code
def main():
    postal_code = input("Enter the postal code (format: ####-###): ")
    find_postal_code_info(postal_code)

if __name__ == '__main__':
    main()  # Runs the main application

