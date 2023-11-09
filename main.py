from flask import Flask, request, jsonify
import random
import hashlib
import logging
import mysql.connector

app = Flask(__name__)

logging.basicConfig(filename='main.log', level=logging.INFO)

mysql_config = {
    'host' : '127.0.0.1',
    'user' : 'root',
    'password' : 'root',
    'database' : 'transaction_status'
}

# Merchant keys with their corresponding key index
merchant_keys = {
    "ueY9qi@U4B": 1,
    "LswE3H5qm": 2,
    "LswE3H5qm": 3,
}
used_reference_numbers = set()

@app.route('/create_payment_request', methods=['POST'])
def create_payment_request():

    data = request.json

    # log incoming data
    logging.info(f"Incoming Data: {data}")
    
    # Validate incoming data
    validate_data = ['amount', 'currency', 'description', 'payment_type']
    if not all(key in data for key in validate_data):
        logging.error("Validation Error: Missing required fields")
        return jsonify({"Error": "Missing required fields"})
    
    amount = data['amount']
    revpay_merchant_key = "MER00000003667"
    currency = data['currency']
    description = data['description']
    payment_type = data['payment_type']
    reference_number = generate_unique_reference_number()

    merchant_key = random.choice(list(merchant_keys.keys()))
    key_index = merchant_keys[merchant_key]

    # If payment type is credit card then set payment id = 2
    if payment_type == "credit card":
        payment_id = "2"

    # Calculate signature
    signature_value = (
        merchant_key +
        revpay_merchant_key +
        reference_number +
        amount +
        currency
    )
    # Hash signature
    signature = hashlib.sha512(signature_value.encode()).hexdigest()

     # MYSQL connection
    connection = mysql.connector.connect(**mysql_config)
    cursor = connection.cursor()

    # Insert transaction data into MySQL
    insert_query = """
        INSERT INTO transactions (reference_number, amount, currency, description, payment_type, signature)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    insert_data = (
            reference_number,
            amount,
            currency,
            description,
            payment_type,
            signature,
    )
    cursor.execute(insert_query, insert_data)
    connection.commit()

    # Close the MySQL connection
    cursor.close()
    connection.close()
    

    # Create the response body
    response = {
        "Status": "200",
        "Redirect_URL": "https://stg-mpg.revpay-sandbox.com.my/v1/payment",
        "Redirect_Body": {
            "Revpay_Merchant_ID": revpay_merchant_key,
            "Key_Index": key_index,
            "Merchant_key" : merchant_key,
            "Payment_ID": payment_id,
            "Reference_Number": reference_number,
            "Amount": amount,
            "Currency": currency,
            "Transaction_Description": description,
            "Signature": signature
        }
    }

    
    

    return jsonify(response)

def generate_unique_reference_number():
    # Generate a new reference number until it's unique
    while True:
        reference_number = f"RF{random.randint(1, 999999999):09d}"
        if reference_number not in used_reference_numbers:
            used_reference_numbers.add(reference_number)
            return reference_number

if __name__ == '__main__':
    app.run(debug=True)
