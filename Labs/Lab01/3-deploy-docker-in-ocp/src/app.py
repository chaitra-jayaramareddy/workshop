from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime
import requests
import json
import os
app = Flask(__name__)
import logging
# Configure logging (optional but recommended)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

MAXIMO_URL = os.getenv('MAXIMO_URL')  # Maximo URL from .env
API_KEY = os.getenv('API_KEY')        # API Key from .env

@app.route('/create-jobplan', methods=['POST'])
def create_jobplan():
    try:
        incoming = request.get_json(force=True)
        raw_body = incoming.get('body')
        if not raw_body:
            return jsonify({"error": "No 'body' field provided"}), 400
        data = request.get_json(force=True)
        
        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError as json_err:
            logger.error(f"JSON decode error: {json_err}")
            return jsonify({"error": "Invalid JSON inside 'body' field"}), 400

        logger.debug(f"Parsed job plan data: {data}")
        
        # Generate dynamic jpnum
        now = datetime.utcnow()
        jpnum_dynamic = "JP" + now.strftime("%d%m%y%H%M")
        data["jpnum"] = jpnum_dynamic  # overwrite whatever was in original
        
        # Now you can log or print to confirm
        logger.debug(f"Updated jpnum: {data['jpnum']}")

        # Send the data as JSON in the POST request to Maximo
        response = requests.post(
            MAXIMO_URL,
            json=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "apikey": API_KEY
            },
            verify=False  # Use verify=True if SSL verification is required
        )

        # Log the status and response from Maximo
        logger.debug(f"Maximo response status: {response.status_code}")
        
        # Check if Maximo responded with 201 Created
        if response.status_code == 201:
            # If there's no body (empty response), handle it accordingly
            if not response.content:  # Check if the response body is empty
                return jsonify({
                    "message": "Job plan created successfully"
                }), 201

            # If there is a response body, try to parse the JSON response
            try:
                maximo_response = response.json()
                return jsonify({
                    "message": "Job plan created successfully",
                    "maximo_response": maximo_response  # Assuming Maximo sends back JSON with job plan details
                }), 201
            except ValueError:
                # If response body is not valid JSON, return raw text instead
                return jsonify({
                    "message": "Job plan created successfully, but no valid JSON response returned from Maximo.",
                    "maximo_response": response.text  # Return raw response text if not JSON
                }), 201
        
        # If the status code is not 201, return Maximo's response with appropriate message
        try:
            maximo_error_response = response.json()  # Attempt to decode JSON from error response
        except ValueError:
            # Handle case where error response is not JSON
            maximo_error_response = response.text  # Fallback to raw response text

        return jsonify({
            "error": "Failed to create job plan",
            "maximo_response": maximo_error_response  # Include the response from Maximo for debugging
        }), response.status_code

    except Exception as e:
        # Log the exception details for debugging purposes
        logger.error(f"An error occurred: {e}" ,exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)
