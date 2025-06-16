from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import json
import os
import logging

app = Flask(__name__)

# Configure logging (optional but recommended)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

MAXIMO_URL = os.getenv('MAXIMO_URL')  # Maximo URL from .env
API_KEY = os.getenv('API_KEY')        # API Key from .env

@app.route('/get-jobplan', methods=['GET'])
def get_jobplan():
    try:
        # Get the job plan number from the query parameters
        jpnum = request.args.get('jpnum')
        status = request.args.get('status')
        if not jpnum:
            return jsonify({"error": "Job plan number 'jpnum' is required"}), 400

        # Build the Maximo API URL with query parameters
        maximo_api_url = f'{MAXIMO_URL}&oslc.where=jpnum=\"{jpnum}\" and status=\"{status}\"&oslc.select=*'

        print(f"maximo_api_url: {maximo_api_url}")

        # Make the GET request to the Maximo API
        response = requests.get(
            maximo_api_url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "apikey": API_KEY
            },
            verify=False  # Use verify=True if SSL verification is required
        )

        # Log the status and response from Maximo
        logger.debug(f"Maximo response status: {response.status_code}")
        #logger.info(f"maximo response : {response.content}")

        # If Maximo responded with 200 OK
        if response.status_code == 200:
            try:
                # Parse and return the JSON response
                maximo_response = response.json()
                # Extract the first member (assuming only one is returned)
                member = maximo_response.get('member', [])[0] if maximo_response.get('member') else {}
                #eatrcting the required feilds 
                jpnum=member.get('jpnum')
                status=member.get('status')
                description = member['jobtask'][0].get('description')
                pluscrevnum = member['pluscrevnum']
                jobplanid = member['jobplanid']
                #jpnum,jpstatus,jpdescription
                return jsonify({
                    #"maximo_response": maximo_response
                    "jpnum": jpnum,
                    "status": status,
                    "description": description,
                    "pluscrevnum": pluscrevnum,
                    "jobplanid":jobplanid,
                    "message": "Job plan fetched successfully",
                }), 200
            except ValueError:
                # Handle case where the response is not valid JSON
                return jsonify({
                    "error": "Invalid JSON response from Maximo",
                    "maximo_response": response.text
                }), 500
        else:
            # If the status code is not 200, return Maximo's response with an error message
            try:
                maximo_error_response = response.json()  # Attempt to decode JSON from error response
            except ValueError:
                # Handle case where error response is not JSON
                maximo_error_response = response.text  # Fallback to raw response text

            return jsonify({
                "error": "Failed to fetch job plan",
                "maximo_response": maximo_error_response
            }), response.status_code

    except Exception as e:
        # Log the exception details for debugging purposes
        logger.error(f"An error occurred: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
