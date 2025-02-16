from datetime import datetime

class SSIWallet:
	def __init__(self):
		self.policies = {
			'gps': {'emergency': True, 'mechanic': False, 'roadside_assistance': False},
			'speed': {'emergency': False, 'mechanic': False, 'roadside_assistance': True},
			'battery': {'emergency': False, 'mechanic': True, 'roadside_assistance': False}
		}
		self.pending_approvals = {}
		self.valid_keys = set(['user_ssi_key', 'mechanic_ssi_key', 'roadside_assistance_ssi_key', 'emergency_ssi_key'])
	
	def request_approval(self, data_type, requester, is_emergency=False):
		approval_id = f"{data_type}_{requester}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
		self.pending_approvals[approval_id] = {
			"data_type": data_type,
			"requester": requester,
			"is_emergency": is_emergency,
			"status": "pending"
		}
		return approval_id
	
	def is_valid_key(self, key):
		return key in self.valid_keys

	def approve_request(self, approval_id):
		if approval_id in self.pending_approvals:
			self.pending_approvals[approval_id]['status'] = 'approved by user'
			return True
		return False

	def deny_request(self, approval_id):
		if approval_id in self.pending_approvals:
			self.pending_approvals[approval_id]['status'] = 'denied by user'
			return True
		return False