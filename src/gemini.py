import google.generativeai as genai
from config import config

# Configure the generative AI model with the API key from environment variables
genai.configure(api_key=config.GEMINI_API_KEY)

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction=config.JARVIS_MODEL_CONFIG,
)

# Start a chat session with the generative AI model
chat = model.start_chat(history=[])
