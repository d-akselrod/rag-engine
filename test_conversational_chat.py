"""Test conversational chat with history."""
import requests
import json

API_BASE_URL = "http://localhost:8000"

print("=" * 70)
print("Testing Conversational Chat with History")
print("=" * 70)

# Initialize conversation history
conversation_history = []

def send_message(message):
    """Send a message and update conversation history."""
    global conversation_history
    
    payload = {
        "message": message,
        "conversation_history": conversation_history,
        "search_type": "cosine",
        "top_k": 3,
        "temperature": 0.7
    }
    
    response = requests.post(
        f"{API_BASE_URL}/chat",
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": data["response"]})
        
        return data
    else:
        print(f"Error: {response.text}")
        return None

# Test conversation flow
print("\n[CONVERSATION 1] User: What is Python?")
data1 = send_message("What is Python?")
if data1:
    print(f"Assistant: {data1['response'][:150]}...")
    print(f"Context used: {data1['context_used']} chunks")

print("\n" + "-" * 70)
print("[CONVERSATION 2] User: What are its main uses?")
data2 = send_message("What are its main uses?")
if data2:
    print(f"Assistant: {data2['response'][:150]}...")
    print(f"Context used: {data2['context_used']} chunks")
    print("\nNote: This response should reference the previous Python question!")

print("\n" + "-" * 70)
print("[CONVERSATION 3] User: Can you tell me more about the web development aspect?")
data3 = send_message("Can you tell me more about the web development aspect?")
if data3:
    print(f"Assistant: {data3['response'][:150]}...")
    print(f"Context used: {data3['context_used']} chunks")
    print("\nNote: This should continue the conversation about Python!")

print("\n" + "=" * 70)
print(f"Conversation History ({len(conversation_history)} messages):")
print("=" * 70)
for i, msg in enumerate(conversation_history, 1):
    role = msg["role"].upper()
    content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
    print(f"{i}. [{role}]: {content}")

print("\n" + "=" * 70)
print("Conversational Chat Test Complete")
print("=" * 70)

