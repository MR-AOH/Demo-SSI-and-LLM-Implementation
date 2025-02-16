from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from datetime import datetime
import os
from models.car import SmartCarSimulator
from models.wallet import SSIWallet
from models.decision_engine import LLMDecisionEngine
import threading
import time

app = Flask(__name__)

API_KEY = "Place you APi key here"
user_context = "Car is driving on the road"  


car = SmartCarSimulator()
wallet = SSIWallet()
decision_engine = LLMDecisionEngine(car, wallet, API_KEY)

# Maximum size for request history
MAX_HISTORY_SIZE = 100
request_history = []

def update_sensors_periodically():
    while True:
        with app.app_context():
            car.update_sensors()
            time.sleep(1)  # Update every second

# Start the background thread
sensor_thread = threading.Thread(target=update_sensors_periodically, daemon=True)
sensor_thread.start()



@app.route('/')
def dashboard():
    global user_context
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Car Data Access Dashboard</title>
        <style>
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .wallet { border: 1px solid black; padding: 10px; margin-top: 20px; }
            .context-selector { margin-bottom: 20px; }
            .pending-approvals { 
                background-color: #fff3cd; 
                padding: 15px; 
                margin-bottom: 20px; 
                border: 1px solid #ffeeba;
            }
            .shared-data {
                background-color: #d4edda;
                padding: 10px;
                margin: 5px 0;
                border-radius: 4px;
            }
        </style>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script>
            function updateDashboard() {
                $.get('/get_latest_history', function(data) {
                    var tableBody = $('#requestHistoryTable tbody');
                    tableBody.empty();
                    data.forEach(function(req) {
                        var row = '<tr>' +
                            '<td>' + req.timestamp + '</td>' +
                            '<td>' + req.type + '</td>' +
                            '<td>' + req.requester + '</td>' +
                            '<td>' + req.user_context + '</td>' +
                            '<td>' + req.llm_decision + '</td>' +
                            '<td>' + req.llm_response + '</td>' +
                            '<td>' + req.status + '</td>';
                        if (req.shared_data) {
                            row += '<td><div class="shared-data">' + JSON.stringify(req.shared_data) + '</div></td>';
                        } else {
                            row += '<td>-</td>';
                        }
                        row += '</tr>';
                        tableBody.append(row);
                    });
                });

                // Update pending approvals
                $.get('/get_pending_approvals', function(data) {
                    var pendingDiv = $('#pendingApprovals');
                    pendingDiv.empty();
                    data.forEach(function(approval) {
                        var approvalHtml = '<div class="approval-item">' +
                            '<p>' + approval.requester + ' is requesting access to ' + approval.data_type + ' data.</p>' +
                            '<form action="/approve_request" method="post">' +
                            '<input type="hidden" name="approval_id" value="' + approval.id + '">' +
                            '<input type="submit" name="action" value="Approve">' +
                            '<input type="submit" name="action" value="Deny">' +
                            '</form></div>';
                        pendingDiv.append(approvalHtml);
                    });
                });
            }

            function updateUserContext() {
                var context = $('#userContext').val();
                $.post('/update_user_context', {context: context}, function(response) {
                    $('#currentContext').text(context);
                    showMessage('User context updated successfully!');
                });
                return false;
            }

            $(document).ready(function() {
                // Initial update
                updateDashboard();
                // Update every 5 seconds
                setInterval(updateDashboard, 5000);
            });
        </script>
    </head>
    <body>
        <h1>Smart Car Data Access Dashboard</h1>
        <div class="flash-message success"></div>
        <div class="context-selector">
            <h2>Set User Context</h2>
            <select id="userContext">
                <option value="Car is driving on the road" {% if user_context == "Car is driving on the road" %}selected{% endif %}>Car is driving on the road</option>
                <option value="Car is parked at home" {% if user_context == "Car is parked at home" %}selected{% endif %}>Car is parked at home</option>
                <option value="Car is at the mechanic" {% if user_context == "Car is at the mechanic" %}selected{% endif %}>Car is at the mechanic</option>
                <option value="Car is at a charging station" {% if user_context == "Car is at a charging station" %}selected{% endif %}>Car is at a charging station</option>
                <option value="Car is in an accident" {% if user_context == "Car is in an accident" %}selected{% endif %}>Car is in an accident</option>
            </select>
            <button onclick="return updateUserContext()">Update Context</button>
        </div>

    <h2>Current User Context: <span id="currentContext">{{ user_context }}</span></h2>
        <h2>Request History</h2>
        <table id="requestHistoryTable">
        <thead>
            <tr>
                <th>Timestamp</th>
                <th>Request Type</th>
                <th>Requester</th>
                <th>User Context</th>
                <th>LLM Decision</th>
                <th>LLM Response</th>
                <th>Final Status</th>
            </tr>
        </thead>
        <tbody>
            {% for req in request_history %}
            <tr>
                <td>{{ req.timestamp }}</td>
                <td>{{ req.type }}</td>
                <td>{{ req.requester }}</td>
                <td>{{ req.user_context }}</td>
                <td>{{ req.llm_decision }}</td>
                <td>{{ req.llm_response }}</td>
                <td>{{ req.status }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
        <div class="wallet">
            <h2>SSI Wallet Configuration</h2>
            <form action="/update_wallet" method="post">
                {% for data_type in wallet.policies %}
                    <h3>{{ data_type }}</h3>
                    {% for requester in wallet.policies[data_type] %}
                        <label>
                            <input type="checkbox" name="{{ data_type }}_{{ requester }}" 
                                   {% if wallet.policies[data_type][requester] %}checked{% endif %}>
                            {{ requester }}
                        </label><br>
                    {% endfor %}
                {% endfor %}
                <input type="submit" value="Update Wallet">
            </form>
        </div>
        <div class="pending-approvals">
            <h2>Pending Approvals</h2>
            {% for approval_id, approval in wallet.pending_approvals.items() %}
                {% if approval.status == "pending" %}
                    <div>
                        <p>{{ approval.requester }} is requesting access to {{ approval.data_type }} data.</p>
                        <form action="/approve_request" method="post">
                            <input type="hidden" name="approval_id" value="{{ approval_id }}">
                            <input type="submit" name="action" value="Approve">
                            <input type="submit" name="action" value="Deny">
                        </form>
                    </div>
                {% endif %}
            {% endfor %}
        </div>
    </body>
    </html>
    ''', request_history=request_history, wallet=wallet, user_context=user_context)

@app.route('/get_latest_history', methods=['GET'])
def get_latest_history():
    return jsonify(request_history)

@app.route('/get_pending_approvals', methods=['GET'])
def get_pending_approvals():
    pending = [
        {'id': approval_id, 'data_type': data['data_type'], 'requester': data['requester']}
        for approval_id, data in wallet.pending_approvals.items()
        if data['status'] == 'pending'
    ]
    return jsonify(pending)


@app.route('/update_wallet', methods=['POST'])
def update_wallet():
    for data_type in wallet.policies:
        for requester in wallet.policies[data_type]:
            wallet.policies[data_type][requester] = f"{data_type}_{requester}" in request.form
    return redirect(url_for('dashboard'))

@app.route('/approve_request', methods=['POST'])
def approve_request():
    approval_id = request.form['approval_id']
    action = request.form['action']
    
    if approval_id in wallet.pending_approvals:
        if action == 'Approve':
            wallet.pending_approvals[approval_id]['status'] = 'approved by user'
        else:
            wallet.pending_approvals[approval_id]['status'] = 'denied by user'
    
    return redirect(url_for('dashboard'))

@app.route('/request_data', methods=['POST'])
def request_data():
    try:
        data = request.json
        request_type = data.get('type')
        requester = data.get('requester')
        is_emergency = data.get('is_emergency', False)
        requester_ssi_key = data.get('requester_ssi_key')

        # Validate required fields
        if not all([request_type, requester, requester_ssi_key]):
            return jsonify({"error": "Missing required fields"}), 400

        if not wallet.is_valid_key(requester_ssi_key):
            return jsonify({"error": "Invalid SSI key"}), 403

        try:
            llm_decision, llm_response = decision_engine.evaluate_request(
                request_type, requester, is_emergency, wallet.policies, user_context
            )
        except Exception as e:
            print(f"LLM Error: {str(e)}")
            return jsonify({"error": "Error processing request"}), 500

        request_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": request_type,
            "requester": requester,
            "user_context": user_context,
            "llm_decision": str(llm_decision),
            "llm_response": llm_response,
            "status": None,
            "shared_data": None
        }

        if llm_decision == True:
            request_entry["status"] = "approved"
            request_entry["shared_data"] = car.sensors[request_type]
            response_data = car.sensors[request_type]
        elif llm_decision == "needs_approval" or (is_emergency and llm_decision == False):
            approval_id = wallet.request_approval(request_type, requester, is_emergency)
            request_entry["status"] = "pending_approval"
            response_data = {"approval_id": approval_id}
        elif llm_decision == "access_needed":
            request_entry["status"] = "access_needed"
            response_data = {"message": "Undefined case, further evaluation needed"}
        else:
            request_entry["status"] = "denied"
            response_data = {"reason": llm_response}

        request_history.insert(0, request_entry)
        return jsonify({
            "status": request_entry["status"],
            "data": response_data
        })

    except Exception as e:
        print(f"Error in request_data: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

    

@app.route('/check_approval', methods=['POST'])
def check_approval():
    data = request.json
    approval_id = data['approval_id']
    
    if approval_id in wallet.pending_approvals:
        approval = wallet.pending_approvals[approval_id]
        if approval['status'] == 'approved by user':
            sensor_data = car.sensors[approval['data_type']]
            # Update the corresponding request in request_history
            for req in request_history:
                if req['type'] == approval['data_type'] and req['requester'] == approval['requester']:
                    req['status'] = 'approved by user'
                    req['shared_data'] = sensor_data
                    break
            return jsonify({
                "status": "approved by user",
                "data": sensor_data
            })
        elif approval['status'] == 'denied by user':
            # Update the corresponding request in request_history
            for req in request_history:
                if req['type'] == approval['data_type'] and req['requester'] == approval['requester']:
                    req['status'] = 'denied by user'
                    break
            return jsonify({
                "status": "denied by user",
                "reason": "User denied the request"
            })
        else:
            return jsonify({
                "status": "pending",
                "message": "Approval is still pending"
            })
    else:
        return jsonify({
            "status": "error",
            "message": "Invalid approval ID"
        }), 400

@app.route('/update_user_context', methods=['POST'])
def update_user_context():
    global user_context
    user_context = request.form['context']
    return jsonify({"status": "success", "context": user_context})

if __name__ == "__main__":
    app.run(debug=True, port=5000)