from chatterbox_api import ChatterboxAPI
import requests

AUDIO_PROMPT_URL = "https://storage.googleapis.com/chatterbox-demo-samples/prompts/male_petergriffin.wav"

# Download sample audio
response = requests.get(AUDIO_PROMPT_URL)
response.raise_for_status()
audio_prompt_bytes = response.content

api = ChatterboxAPI("http://localhost:5000")

# Example 1: Basic synthesis with default parameters
print("Example 1: Basic synthesis with default parameters")
response = api.synthesize(text="Hello, world!", audio_prompt=audio_prompt_bytes)
with open("output_default.wav", "wb") as f:
    f.write(response.content)
print("Saved to output_default.wav")

# Example 2: Synthesis with custom parameters
print("\nExample 2: Synthesis with custom parameters")
response = api.synthesize(
    text="This is a test with custom parameters!", 
    audio_prompt=audio_prompt_bytes,
    exaggeration=0.8,
    cfg_weight=0.3,
    temperature=0.6
)
with open("output_custom.wav", "wb") as f:
    f.write(response.content)
print("Saved to output_custom.wav")

# Example 3: Synthesis without audio prompt but with parameters
print("\nExample 3: Synthesis without audio prompt but with parameters")
response = api.synthesize(
    text="No voice cloning, just custom generation parameters.",
    exaggeration=0.2,
    cfg_weight=0.7,
    temperature=0.9
)
with open("output_no_prompt.wav", "wb") as f:
    f.write(response.content)
print("Saved to output_no_prompt.wav")

print("\nAll examples completed successfully!")