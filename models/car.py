import random

class SmartCarSimulator:
	def __init__(self):
		self.sensors = {
			'gps': {'lat': 0, 'lon': 0},
			'speed': 0,
			'battery': 100
		}
	
	def update_sensors(self):
		self.sensors['gps']['lat'] += random.uniform(-0.001, 0.001)
		self.sensors['gps']['lon'] += random.uniform(-0.001, 0.001)
		self.sensors['speed'] = max(0, min(120, self.sensors['speed'] + random.uniform(-5, 5)))
		self.sensors['battery'] = max(0, min(100, self.sensors['battery'] - random.uniform(0, 0.1)))