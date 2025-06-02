from chatterbox_api import ChatterboxAPI
import requests

AUDIO_PROMPT_URL = "https://storage.googleapis.com/chatterbox-demo-samples/prompts/male_petergriffin.wav"

# Download sample audio
response = requests.get(AUDIO_PROMPT_URL)
response.raise_for_status()
audio_prompt_bytes = response.content

api = ChatterboxAPI("http://localhost:5000")

# Pass audio bytes directly instead of using a temporary file
response = api.synthesize(text="Hello, world!", audio_prompt=audio_prompt_bytes)

# Save the response to a file
with open("output.wav", "wb") as f:
    f.write(response.content)