from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import json
import os
import logging

app = Flask(__name__)

# Logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
MAXIMO_URL = os.getenv('MAXIMO_URL')
API_KEY = os.getenv('API_KEY')

@app.route('/update-job-tasks', methods=['POST'])
def update_job_tasks():
    try:
        # Load incoming JSON body
        data = request.get_json(force=True)
        logger.debug(f"Initial received data: {json.dumps(data, indent=2)}")

        # If 'body' is a string (i.e., JSON inside a string), parse it
        if isinstance(data, dict) and 'body' in data and isinstance(data['body'], str):
            try:
                data = json.loads(data['body'])
                logger.debug(f"Parsed body from 'body' field: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError as e:
                return jsonify({"error": f"Failed to parse 'body' JSON string: {str(e)}"}), 400

        # Extract jobplanid from JSON
        jobplanid = data.get("jobplanid")
        if not jobplanid:
            return jsonify({"error": "Missing 'jobplanid' in request body"}), 400


        # Step 1: Build URL to fetch current job plan details
        if '?lean=1' in MAXIMO_URL:
            base_path, query = MAXIMO_URL.split('?')
            get_url = f"{base_path.rstrip('/')}/{jobplanid}?{query}"
        else:
            get_url = f"{MAXIMO_URL.rstrip('/')}/{jobplanid}?lean=1"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "apikey": API_KEY
        }

        # Fetch current job plan details
        response = requests.get(get_url, headers=headers, verify=False)
        if response.status_code != 200:
            return jsonify({
                "error": "Failed to fetch job plan details",
                "status_code": response.status_code,
                "response": response.text
            }), response.status_code

        jobplan_details = response.json()
        current_status = jobplan_details.get("status")
        logger.debug(f"Current job plan status: {current_status}")

        if current_status != "PNDREV":
            return jsonify({
                "message": "Update skipped. Job plan is not in 'PNDREV' status.",
                "current_status": current_status
            }), 200

        # Prepare headers for PATCH
        patch_headers = headers.copy()
        patch_headers.update({
            "x-method-override": "PATCH",
            "patchtype": "MERGE",
            "properties": "jpnum,siteid,description,jobtask"
        })

        # POST with PATCH override to update tasks
        patch_response = requests.post(get_url, json=data, headers=patch_headers, verify=False)
        try:
            patch_response_json = patch_response.json()
        except ValueError:
            patch_response_json = {"raw_response": patch_response.text}

        if patch_response.status_code in [200, 204]:
            return jsonify({
                "message": "Job plan tasks updated successfully",
                "jobplanid": jobplanid,
                "maximo_response": patch_response_json
            }), 200

        return jsonify({
            "error": "Failed to update job plan tasks",
            "status_code": patch_response.status_code,
            "maximo_response": patch_response_json
        }), patch_response.status_code

    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
