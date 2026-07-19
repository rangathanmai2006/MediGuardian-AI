from google import genai
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Create Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

try:
    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents="Say only: Hello"
    )

    print("✅ Success!")
    print(response.text)

except Exception as e:
    print("❌ Error:")
    print(e)