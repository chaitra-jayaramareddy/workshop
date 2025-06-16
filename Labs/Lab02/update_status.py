from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import json
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
MAXIMO_BASE_URL = os.getenv('MAXIMO_URL') 
API_KEY = os.getenv('API_KEY')

@app.route('/update-jobplan-status', methods=['POST'])  # No path param
def update_jobplan_status():
    try:
        data = request.get_json(force=True)

        if not isinstance(data, dict):
            logger.error("Expected JSON body to be a dict")
            return jsonify({"error": "Request body must be a JSON object"}), 400

        jobplanid = data.get("jobplanid")
        if not jobplanid:
            logger.error("Missing 'jobplanid' in request body")
            return jsonify({"error": "Missing 'jobplanid' in request body"}), 400

        logger.debug(f"Updating job plan ID {jobplanid} with data: {data}")

        # Properly insert jobplan ID before query string
        if '?lean=1' in MAXIMO_BASE_URL:
            base_path, query = MAXIMO_BASE_URL.split('?')
            url = f"{base_path.rstrip('/')}/{jobplanid}?{query}"
        else:
            url = f"{MAXIMO_BASE_URL.rstrip('/')}/{jobplanid}?lean=1"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "apikey": API_KEY,
            "x-method-override": "PATCH",
            "patchtype": "MERGE",
            "properties": "jpnum,status"
        }

        logger.debug(f"headers: {headers}")
        logger.debug(f"maximo url: {url}")

        response = requests.post(url, json=data, headers=headers, verify=False)
        logger.debug(f"Maximo response status: {response.status_code}")

        try:
            response_json = response.json()
        except ValueError:
            response_json = {"raw_response": response.text}

        if response.status_code in [200, 204]:
            return jsonify({
                "message": "Job plan status updated successfully",
                "jobplanid": jobplanid,
                "maximo_response": response_json
            }), 200

        return jsonify({
            "error": "Failed to update job plan",
            "status_code": response.status_code,
            "maximo_response": response_json
        }), response.status_code

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)