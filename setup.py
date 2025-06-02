from setuptools import setup, find_packages

setup(
    name="chatterbox-server",
    description="A API for ChatterboxTTS",
    version="0.1.1",
    author="mrfakename",
    author_email="me@mrfake.name",
    url="https://github.com/neuralvox/chatterbox-api",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    extras_require={
        'server': [
            'waitress',
            'chatterbox-tts',
            'flask',
            'torch',
            'torchaudio',
        ]
    },
    entry_points={
        "console_scripts": [
            "chatterbox-server=chatterbox_api.cli:main",
        ],
    },
)