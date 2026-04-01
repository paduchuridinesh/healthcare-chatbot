import requests
import json

# Test the chatbot with different scenarios
BASE_URL = "http://localhost:5000/chat"

def send_message(user_id, message):
    """Send a message to the chatbot and print the response."""
    response = requests.post(BASE_URL, json={
        "user_id": user_id,
        "message": message
    })
    return response.json()

def print_response(response):
    """Pretty print the chatbot response."""
    print(f"\n🤖 Bot: {response['reply']}")
    if 'decision' in response and response['decision']:
        print(f"📋 Decision: {response['decision']}")
    if 'dept' in response and response['dept']:
        print(f"🏥 Department: {response['dept']}")
    if 'options' in response and response['options']:
        print(f"⚡ Options: {response['options']}")
    print("-" * 80)

print("=" * 80)
print("HOSPITAL CHATBOT TESTING")
print("=" * 80)

# TEST 1: EMERGENCY DETECTION
print("\n\n🚨 TEST 1: EMERGENCY DETECTION")
print("=" * 80)
user1 = "emergency_test_user"
print("\n👤 User: I have severe chest pain and I can't breathe")
response = send_message(user1, "I have severe chest pain and I can't breathe")
print_response(response)

# TEST 2: MINOR ISSUE (Home Care)
print("\n\n✅ TEST 2: MINOR ISSUE - HOME CARE")
print("=" * 80)
user2 = "minor_test_user"

print("\n👤 User: I have a mild headache")
response = send_message(user2, "I have a mild headache")
print_response(response)

print("\n👤 User: Just started today")
response = send_message(user2, "Just started today")
print_response(response)

print("\n👤 User: Mild")
response = send_message(user2, "Mild")
print_response(response)

print("\n👤 User: It's in the front of my head")
response = send_message(user2, "It's in the front of my head")
print_response(response)

print("\n👤 User: No, it doesn't get worse with movement")
response = send_message(user2, "No, it doesn't get worse with movement")
print_response(response)

print("\n👤 User: No, I'm not experiencing any of those")
response = send_message(user2, "No, I'm not experiencing any of those")
print_response(response)

# TEST 3: CONSULTATION REQUIRED
print("\n\n🏥 TEST 3: CONSULTATION REQUIRED")
print("=" * 80)
user3 = "consultation_test_user"

print("\n👤 User: I have a fever")
response = send_message(user3, "I have a fever")
print_response(response)

print("\n👤 User: For 5 days now")
response = send_message(user3, "For 5 days now")
print_response(response)

print("\n👤 User: Moderate")
response = send_message(user3, "Moderate")
print_response(response)

print("\n👤 User: It's around 101 degrees")
response = send_message(user3, "It's around 101 degrees")
print_response(response)

print("\n👤 User: Yes, I have chills")
response = send_message(user3, "Yes, I have chills")
print_response(response)

print("\n👤 User: No breathing difficulty or stiff neck")
response = send_message(user3, "No breathing difficulty or stiff neck")
print_response(response)

print("\n\n" + "=" * 80)
print("TESTING COMPLETE!")
print("=" * 80)
