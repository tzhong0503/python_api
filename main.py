from flask import Flask, request, jsonify
import random
import hashlib
import logging

app = Flask(__name__)

logging.basicConfig(filename='main.log',level=logging.INFO)

# Merchant keys with their corresponding key index
merchant_keys = {
    "ueY9qi@U4B": 1,
    "LswE3H5qm": 2,
    "LswE3H5qm": 3,
}
used_reference_numbers = set()

@app.route('/create_payment_request', methods=['POST'])
# Create the request body
def create_payment_request():
    data = request.json

    logging.info(f"Incoming Data:{data}")   


    amount = data.get('amount')
    revpay_merchant_key = "MER00000003667"
    currency = data.get('currency')
    description = data.get('description')
    payment_type = data.get('payment_type')

    reference_number = generate_unique_reference_number()

    # Generate random key index with their corresponding merchant keys
    merchant_key = random.choice(list(merchant_keys.keys()))
    key_index = merchant_keys[merchant_key]

    # If the payment type is credit card then set payment id = 2
    if payment_type == "credit card":
        payment_id = "2"

    # Generate hash512 signature
    signature_value = (
        merchant_key +
        revpay_merchant_key +  
        reference_number +
        amount +
        currency
    )

    signature = hashlib.sha512(signature_value.encode()).hexdigest()

    # Create the response body
    response = {
        "Status" : "200",
        "Redirect_URL": "https://stg-mpg.revpay-sandbox.com.my/v1/payment",
        "Redirect_Body":{
        "Revpay_Merchant_ID": revpay_merchant_key,
        "Payment_ID": payment_id,
        "Reference_Number": reference_number,
        "Amount": amount,
        "Currency": currency,
        "Transaction_Description": description,
        "Key_Index": key_index,
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
