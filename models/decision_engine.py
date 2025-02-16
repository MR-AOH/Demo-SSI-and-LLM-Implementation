import google.generativeai as genai

class LLMDecisionEngine:
	def __init__(self, car, wallet, api_key):
		self.car = car
		self.wallet = wallet
		genai.configure(api_key=api_key)
		self.model = genai.GenerativeModel('gemini-1.5-flash')

	def evaluate_request(self, request_type, requester, is_emergency, user_permissions, user_context):
		try:
			prompt = f"""Evaluate the following data access request:
			Request Type: {request_type}
			Requester: {requester}
			User Context: {user_context}
			Is Emergency: {is_emergency}
			User Permissions: {user_permissions}

			Rules:
			1. Mechanic Requests:
			   - Approve battery data requests if user permission is granted
			   - For speed data during emergency, require user approval
			   - Deny all other data types
			2. Roadside Assistance Requests:
			   - Approve GPS data requests if user permission is granted
			   - Deny all other data types
			3. Emergency Services:
			   - For emergency situations, recommend user approval for all requests
			4. For undefined cases, respond with "access_needed"
			5. Deny all other requests
			6. Always check user permissions before approving

			Provide your decision as:
			Decision: [approved/denied/needs_approval/access_needed]
			Response: [explanation]
			"""

			response = self.model.generate_content(prompt)
			
			if response.text:
				# Split response into lines and clean up
				lines = [line.strip() for line in response.text.strip().split('\n')]
				
				# Extract decision and response separately
				decision_line = next((line for line in lines if line.lower().startswith('decision:')), '')
				response_lines = [line for line in lines if line.lower().startswith('response:')]
				
				if decision_line:
					decision = decision_line.split(':', 1)[1].strip().lower()
					response_text = '\n'.join(response_lines).replace('Response:', '').strip()
					
					if decision == 'approved':
						return True, response_text
					elif decision == 'denied':
						return False, response_text
					elif decision in ['needs_approval', 'needs approval']:
						return "needs_approval", response_text
					elif decision == 'access_needed':
						return "access_needed", response_text
					else:
						return "needs_approval", f"Unclear decision ({decision}). Requiring user approval for safety."
				else:
					return "needs_approval", "No clear decision found. Requiring user approval for safety."
			else:
				return "needs_approval", "No response from LLM. Requiring user approval for safety."
		except Exception as e:
			print(f"Error in LLM evaluation: {str(e)}")
			return "needs_approval", f"Error in evaluation. Requiring user approval for safety."