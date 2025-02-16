import requests
import time
from datetime import datetime

def send_request(request_type, requester, is_emergency=False, user_context=None):
    url = "http://localhost:5000/request_data"
    data = {
        "type": request_type,
        "requester": requester,
        "user_context": user_context or "Car is driving on the road",
        "is_emergency": is_emergency,
        "user_ssi_key": "user_ssi_key",
        "requester_ssi_key": f"{requester}_ssi_key"
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()
        print(f"\nRequest sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Type: {request_type}, Requester: {requester}, Emergency: {is_emergency}")
        
        if result['status'] == 'pending_approval':
            approval_id = result['data']['approval_id']
            print(f"\nApproval required. Approval ID: {approval_id}")
            print("Please approve or deny the request on the dashboard.")
            
            # Wait for approval with timeout
            max_retries = 60  # 5 minutes timeout (60 * 5 seconds)
            retries = 0
            
            while retries < max_retries:
                try:
                    check_response = requests.post(
                        "http://localhost:5000/check_approval", 
                        json={"approval_id": approval_id}
                    )
                    check_result = check_response.json()
                    
                    if check_result['status'] == 'approved by user':
                        print("\n✅ Request approved!")
                        print("Received data:", check_result['data'])
                        return check_result['data']
                    elif check_result['status'] == 'denied by user':
                        print("\n❌ Request denied.")
                        return None
                    else:
                        print("Waiting for approval... (Press Ctrl+C to cancel)")
                        retries += 1
                        time.sleep(5)
                except requests.exceptions.RequestException as e:
                    print(f"Error checking approval status: {e}")
                    time.sleep(5)
                    
            print("\n⚠️ Approval request timed out after 5 minutes")
            return None
        else:
            print(f"\nStatus: {result['status']}")
            if result['status'] == 'approved':
                print("Received data:", result['data'])
                return result['data']
            elif 'reason' in result:
                print("Reason:", result['reason'])
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error sending request: {e}")
        return None

def test_all_sensors():
    """Test function to demonstrate all possible sensor requests"""
    sensors = [
        ("gps", "emergency", True),
        ("speed", "mechanic", False),
        ("battery", "roadside_assistance", False),
        ("battery", "mechanic", False),
        ("speed", "emergency", True),
    ]
    
    print("\n=== Starting Sensor Request Tests ===\n")
    for sensor_type, requester, is_emergency in sensors:
        print(f"\n--- Testing {sensor_type} request from {requester} ---")
        send_request(sensor_type, requester, is_emergency)
        time.sleep(2)  # Wait between requests

if __name__ == "__main__":
    # Example usage
    test_all_sensors()