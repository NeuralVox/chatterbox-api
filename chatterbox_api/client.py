import requests
from io import BytesIO
from typing import Union, BinaryIO
import time

class ChatterboxAPIError(Exception):
    """Base class for exceptions in this module."""
    pass

class TaskFailedError(ChatterboxAPIError):
    """Raised when a task fails on the server."""
    pass


class ChatterboxAPI:
    def __init__(self, api_url: str, poll_interval: float = 1.0):
        """
        Initializes the ChatterboxAPI client.

        Args:
            api_url (str): The base URL of the Chatterbox API.
            poll_interval (float): Time in seconds between status checks.
        """
        self.api_url = api_url
        self.poll_interval = poll_interval

    def _lowlevel_synthesize(self, text: str, audio_prompt: Union[str, BinaryIO, bytes, None] = None) -> str:
        """
        Submits a synthesis task to the server and returns the task ID.  This is the low-level function.

        Args:
            text (str): The text to synthesize.
            audio_prompt (str, BinaryIO, bytes, optional): Path to an audio file, a BytesIO object, or audio bytes to use as a prompt. Defaults to None.

        Returns:
            str: The task ID.
        """
        url = f"{self.api_url}/synthesize"
        files = {}
        data = {'text': text}

        if audio_prompt:
            if isinstance(audio_prompt, str):
                # Read the file content into memory to avoid "I/O operation on closed file" error
                with open(audio_prompt, 'rb') as f:
                    audio_content = f.read()
                files['audio_prompt'] = ('audio_prompt.wav', BytesIO(audio_content))
            elif isinstance(audio_prompt, BytesIO):
                files['audio_prompt'] = ('audio_prompt.wav', audio_prompt)
            elif isinstance(audio_prompt, bytes):
                files['audio_prompt'] = ('audio_prompt.wav', BytesIO(audio_prompt))
            else:
                raise ValueError("audio_prompt must be a string (path), BytesIO, or bytes")

        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json()['task_id']

    def _get_status(self, task_id: str) -> dict:
        """
        Retrieves the status of a synthesis task.  This is the low-level function.

        Args:
            task_id (str): The ID of the task to check.

        Returns:
            dict: A dictionary containing the task status.
        """
        url = f"{self.api_url}/status/{task_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def _download(self, task_id: str) -> requests.Response:
        """
        Downloads the synthesized audio for a completed task.  This is the low-level function.

        Args:
            task_id (str): The ID of the task to download.

        Returns:
            requests.Response: The response from the API, containing the audio data.
        """
        url = f"{self.api_url}/download/{task_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response

    def synthesize(self, text: str, audio_prompt: Union[str, BinaryIO, bytes, None] = None) -> requests.Response:
        """
        Synthesizes speech from the given text, optionally using an audio prompt.  This function polls the server
        until the task is complete and then downloads the result.

        Args:
            text (str): The text to synthesize.
            audio_prompt (str, BinaryIO, bytes, optional): Path to an audio file, a BytesIO object, or audio bytes to use as a prompt. Defaults to None.

        Returns:
            requests.Response: The response from the API, containing the audio data.
        """
        task_id = self._lowlevel_synthesize(text, audio_prompt)

        while True:
            status = self._get_status(task_id)
            if status['status'] == 'completed':
                return self._download(task_id)
            elif status['status'] == 'error':
                raise TaskFailedError(f"Task {task_id} failed: {status.get('error', 'Unknown error')}")
            elif status['status'] == 'queued':
                print(f"Task {task_id} is queued. Position: {status.get('queue_position', 'Unknown')}")
            else:
                print(f"Task {task_id} status: {status['status']}")
            time.sleep(self.poll_interval)

    def get_status(self, task_id: str) -> dict:
        """
        Retrieves the status of a synthesis task.

        Args:
            task_id (str): The ID of the task to check.

        Returns:
            dict: A dictionary containing the task status.
        """
        return self._get_status(task_id)

    def download(self, task_id: str) -> requests.Response:
        """
        Downloads the synthesized audio for a completed task.

        Args:
            task_id (str): The ID of the task to download.

        Returns:
            requests.Response: The response from the API, containing the audio data.
        """
        return self._download(task_id)
