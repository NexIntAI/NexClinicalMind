import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Use Vertex AI with your GCP project credits
client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
)

def ask_gemini(prompt: str) -> str:
    """Send a prompt to Gemini 2.0 Flash via Vertex AI."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"Gemini error: {str(e)}"