> [Join the waitlist for NeuralVox](https://forms.gle/HA4dvRB9nz2G1s2LA) - full-cast AI audiobooks!

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

If you are getting CUDA issues, you can try the experimental fork of Chatterbox TTS:

```
pip install "chatterbox-tts @ git+https://github.com/fakerybakery/better-chatterbox@fix-cuda-issue"
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
# Make sure you have a server running!

# If you want to pass custom headers (e.g. for authentication if you are running behind a proxy/load balancer), you can do so like this:
# api = ChatterboxAPI("http://localhost:5000", headers={"Authorization": "Bearer <your-token>"})

response = api.synthesize(text="Hello, world!", audio_prompt="path/to/audio_prompt.wav")

# Save the response to a file
with open("output.wav", "wb") as f:
    f.write(response.content)
```

## License

Copyright 2025 NeuralVox.

Licensed under the BSD-3-Clause license.

---

[NeuralVox](https://neuralvox.github.io/) &bull; [@neuralvox on X](https://x.com/neuralvox)
