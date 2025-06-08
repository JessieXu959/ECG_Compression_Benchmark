#!/usr/bin/env python3
"""
Debug JWT token decoding issue
"""

import json
import base64

def debug_jwt_token(token):
    """Debug JWT token decoding"""
    print("🔍 Debugging JWT Token")
    print("=" * 50)

    print(f"📄 Token: {token}")
    print(f"📏 Token length: {len(token)}")

    # Remove Bearer prefix if present
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")
        print(f"🧹 Cleaned token: {token}")

    # Check if it looks like JWT
    parts = token.split(".")
    print(f"🔧 Token parts: {len(parts)}")

    if len(parts) != 3:
        print("❌ Not a valid JWT format (should have 3 parts)")
        return False

    # Try to decode each part
    for i, part in enumerate(parts):
        part_name = ["Header", "Payload", "Signature"][i]
        print(f"\n📦 {part_name}: {part}")

        if i < 2:  # Don't decode signature
            try:
                # Add padding for base64
                padding = 4 - len(part) % 4
                if padding != 4:
                    padded_part = part + "=" * padding
                else:
                    padded_part = part

                print(f"🔧 Padded: {padded_part}")

                # Decode base64
                decoded_bytes = base64.b64decode(padded_part)
                decoded_str = decoded_bytes.decode('utf-8')

                print(f"📄 Decoded string: {decoded_str}")

                # Parse JSON
                data = json.loads(decoded_str)
                print(f"✅ Parsed JSON: {json.dumps(data, indent=2)}")

                if i == 1:  # Payload
                    if "teamName" in data:
                        print(f"👤 Team Name: {data['teamName']}")
                        return True
                    else:
                        print("❌ No teamName in payload")
                        return False

            except Exception as e:
                print(f"❌ Decoding error: {e}")
                return False

    return False

def test_token_creation():
    """Test our token creation"""
    print("\n🧪 Testing Token Creation")
    print("=" * 50)

    # Simulate what create_jwt_token does
    import time

    payload = {
        "teamName": "string",
        "email": "string",
        "iat": int(time.time()),
        "exp": int(time.time()) + (24 * 60 * 60)
    }

    header = {"alg": "HS256", "typ": "JWT"}

    # Encode
    header_b64 = base64.b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature = "signature"

    token = f"{header_b64}.{payload_b64}.{signature}"

    print(f"🔨 Created token: {token}")

    # Test decoding
    return debug_jwt_token(token)

if __name__ == "__main__":
    # Test the token from your API call
    your_token = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ0ZWFtTmFtZSI6ICJzdHJpbmciLCAiZW1haWwiOiAic3RyaW5nIiwgImlhdCI6IDE3NDk0MTYzNDUsICJleHAiOiAxNzQ5NTAyNzQ1fQ.signature"

    print("Testing your token from API:")
    success1 = debug_jwt_token(your_token)

    print("\nTesting our token creation:")
    success2 = test_token_creation()

    print(f"\n📊 Results:")
    print(f"  Your token valid: {'✅' if success1 else '❌'}")
    print(f"  Our token valid: {'✅' if success2 else '❌'}")

    if not success1:
        print("\n🔧 Recommended fix: The token format may need adjustment")