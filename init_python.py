import asyncio
import os
from dotenv import load_dotenv
from twikit import Client

load_dotenv()

async def main():
    print("🔐 Attempting to log in to Twitter to generate cookies...")
    
    username = os.getenv("TWITTER_USERNAME")
    email = os.getenv("TWITTER_EMAIL")
    password = os.getenv("TWITTER_PASSWORD")

    if not username or not password:
        print("❌ Error: Missing credentials in .env file")
        return

    # Initialize client with English locale
    client = Client('en-US')

    try:
        # Using auth_info_2 (email) helps avoid "unusual activity" challenges
        await client.login(
            auth_info_1=username,
            auth_info_2=email,
            password=password
        )
        
        client.save_cookies('twitter_cookies.json')
        print("✅ Success! 'twitter_cookies.json' has been created.")
        print("You can now run your main app, and it will use this session.")
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        print("---------------------------------------------------")
        print("⚠️  IF THIS FAILED WITH '403' OR 'CLOUDFLARE':")
        print("1. Delete this script.")
        print("2. Log in to Twitter in your browser (Chrome/Edge).")
        print("3. Use 'Cookie-Editor' extension to Export JSON.")
        print("4. Create 'twitter_cookies.json' manually and paste the JSON.")
        print("---------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())