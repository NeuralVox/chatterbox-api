# Chatterbox Server

A API for Chatterbox TTS.

This library consists of two components:

* A client library for interacting with the Chatterbox TTS API.
* The API server itself that wraps the Chatterbox TTS model.

## Installation

```bash
pip install chatterbox-server
```

To install with support for the API server, run:

```bash
pip install chatterbox-server[server]
```

## Usage

Start the API server:

```bash
chatterbox-server
```

## Client Usage

```python
from chatterbox_api import ChatterboxAPI

api = ChatterboxAPI("http://localhost:5000")

response = api.synthesize(text="Hello, world!", audio_prompt="path/to/audio_prompt.wav")

# Save the response to a file
with open("output.wav", "wb") as f:
    f.write(response.content)
```

## License

BSD-3-Clause

---

[NeuralVox](https://neuralvox.github.io/)