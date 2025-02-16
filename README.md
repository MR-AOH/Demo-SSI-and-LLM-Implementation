# Demonstration of concept How can we Enhancing Privacy and Security of Smart Vehicles using Self-Sovereign Identity (SSI) and LLM

A Flask-based web application that simulates a smart car's data access control system using Google's Gemini AI for decision-making. The system leverages **Self-Sovereign Identity (SSI)** to give users full control over their data, ensuring privacy and security while managing access to car sensor data based on user context, requester type, and predefined policies.

## Features

- **Real-time sensor data simulation** (GPS, Speed, Battery)
- **AI-powered access control decisions** using Google's Gemini AI
- **Dynamic user context management**
- **Self-Sovereign Identity (SSI) integration** for decentralized identity and data control
- **User-controlled privacy policies** via SSI wallet
- **Real-time dashboard** with request history and access logs
- **User approval system** for sensitive data access
- **Secure, decentralized identity management** for smart vehicle ecosystems

## How SSI Enhances Privacy and Security in Smart Vehicles

The system integrates **Self-Sovereign Identity (SSI)** to empower users with full control over their data. Here's how it works:

1. **Decentralized Identity**: Users manage their identity and access policies through an SSI wallet, eliminating reliance on centralized authorities.
2. **User-Controlled Privacy**: The SSI wallet allows users to define granular access policies for different data types (GPS, Speed, Battery) and requesters (Emergency Services, Mechanics, Roadside Assistance).
3. **Selective Disclosure**: Users can share only the necessary data with requesters, ensuring minimal data exposure.
4. **Consent Management**: All data access requests require explicit user consent, which is managed through the SSI wallet.
5. **Tamper-Proof Logs**: All access requests and approvals are recorded on a decentralized ledger, ensuring transparency and auditability.

## Project Structure
   ```bash
   Demo-SSI-and-LLM-Implementation/
   ├── app.py                 # Main Flask application
   ├── requester.py           # Test client for sending requests
   ├── models/
   │   ├── __init__.py
   │   ├── car.py            # Smart car simulator
   │   ├── wallet.py         # SSI wallet implementation
   │   └── decision_engine.py # LLM-based decision engine
   └── README.md
```





## Prerequisites

- Python 3.8 or higher
- Flask
- Google GenerativeAI Python SDK
- Requests library

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/smart-car-access-control.git
   cd smart-car-access-control
   
2. Install required packages:

`pip install flask google-generativeai requests `

3. Set up your Google API key:

- Get an API key from Google AI Studio (https://makersuite.google.com/app/apikey)

- Replace the API_KEY in app.py:

` API_KEY = "Your-API-Key-Here" `


## Start the Flask server:

` flask run `

## Access the dashboard:

- Open http://localhost:5000 in your web browser

The dashboard shows real-time sensor data and access requests

## Test requests using requester.py:

` python requester.py `

## User Context:

The system's behavior changes based on the user context. Available contexts:

| User Context           | Behavior Changes                         |
| ---------------------- | ---------------------------------------- |
| 🚗 Driving on the road | Standard access rules apply              |
| 🏠 Parked at home      | Minimal data access granted              |
| 🛠️ At the mechanic     | Mechanics may request battery/speed data |
| ⚡ Charging station    | Charging-related data accessible         |
| 🚨 In an accident      | Emergency services get priority access   |

Important: Changing the user context may affect access control decisions. For example:

Emergency services might get priority access during accidents

Mechanics might get easier access when the car is at the service center

## 🚗 User Contexts & Access Control Rules:

| Requester Type          | GPS                    | Speed                 | Battery |
| ----------------------- | ---------------------- | --------------------- | ------- |
| **Mechanic**            | ❌                     | 🔒 (Emergencies only) | ✅      |
| **Roadside Assistance** | ✅                     | ❌                    | ❌      |
| **Emergency Services**  | 🔒 (Approval required) | 🔒                    | 🔒      |

✅ = Allowed | ❌ = Denied | 🔒 = Requires Approval

## 🛠️ SSI Wallet Configuration

Users can define access policies for different data types in the dashboard:

- Data Types: GPS, Speed, Battery
- Requesters: Emergency Services, Mechanics, Roadside Assistance

## 🧪 Testing

Use requester.py to test different scenarios:

```
send_request("gps", "emergency", is_emergency=True)
send_request("speed", "mechanic", is_emergency=False)
send_request("battery", "roadside_assistance", is_emergency=False)
```

## ⚠️ Security Notes

- Keep your API key secure and never commit it to version control.
- Use environment variables in production.
- This implementation is for demonstration purposes only; secure deployments should use encrypted storage.

## 🤝 Contributing

- Fork the repository
- Create a feature branch

🎯 Questions? Issues?

Feel free to open an issue or reach out!


📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
