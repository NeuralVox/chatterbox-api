from chatterbox.tts import ChatterboxTTS
import torchaudio as ta
from flask import Flask, request, send_file, jsonify, render_template
from io import BytesIO
import os
import threading
import queue
import uuid
import time
import click
import torch
from waitress import serve
import json

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))

# Global variables for configuration
model = None
MAX_CONCURRENT_TASKS = 4
task_queue = queue.Queue()
semaphore = None
task_results = {}
task_status = {}

def detect_device():
    """Auto-detect the best available device"""
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    else:
        return "cpu"

def initialize_model():
    """Initialize the TTS model with auto-detected device"""
    global model
    device = detect_device()
    click.echo(f"Initializing TTS model on device: {device}")
    model = ChatterboxTTS.from_pretrained(device=device)

def process_task(text, audio_prompt_bytes, task_id, generation_params=None):
    try:
        task_status[task_id] = "processing"
        
        # Set default parameters
        default_params = {
            'exaggeration': 0.5,
            'cfg_weight': 0.5,
            'temperature': 0.8
        }
        
        # Merge with provided parameters
        if generation_params:
            default_params.update(generation_params)
        
        if audio_prompt_bytes:
            # Use the pre-read audio bytes
            wav = model.generate(
                text, 
                audio_prompt_path=BytesIO(audio_prompt_bytes),
                **default_params
            )
        else:
            wav = model.generate(text, **default_params)

        # Convert the waveform to a byte stream
        buffer = BytesIO()
        ta.save(buffer, wav, model.sr, format="wav")
        buffer.seek(0)

        task_results[task_id] = buffer
        task_status[task_id] = "completed"

    except Exception as e:
        task_status[task_id] = "error"
        task_results[task_id] = str(e)
    finally:
        semaphore.release()

def worker():
    while True:
        task_data = task_queue.get()
        if task_data is None:
            break
        
        task_id, text, audio_prompt_bytes, generation_params = task_data
        semaphore.acquire()
        threading.Thread(target=process_task, args=(text, audio_prompt_bytes, task_id, generation_params)).start()
        task_queue.task_done()

@app.route('/')
def index():
    return render_template('gui.html')

@app.route('/synthesize', methods=['POST'])
def synthesize():
    text = request.form['text']
    audio_prompt_file = request.files.get('audio_prompt')
    
    # Parse optional generation parameters from JSON
    generation_params = {}
    params_json = request.form.get('params')
    if params_json:
        try:
            generation_params = json.loads(params_json)
            # Validate parameter types and ranges
            for param, value in generation_params.items():
                if param in ['exaggeration', 'cfg_weight', 'temperature']:
                    if not isinstance(value, (int, float)):
                        return jsonify({'error': f'Parameter {param} must be a number'}), 400
                    if not (0.0 <= value <= 1.0):
                        return jsonify({'error': f'Parameter {param} must be between 0.0 and 1.0'}), 400
                else:
                    return jsonify({'error': f'Unknown parameter: {param}'}), 400
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON in params field'}), 400
    
    # Read the audio file content immediately while the request is still active
    audio_prompt_bytes = None
    if audio_prompt_file:
        audio_prompt_bytes = audio_prompt_file.read()
    
    task_id = str(uuid.uuid4())
    task_status[task_id] = "queued"
    
    # Add to queue with the pre-read bytes and parameters
    task_queue.put((task_id, text, audio_prompt_bytes, generation_params))
    
    # Calculate queue position
    queue_position = task_queue.qsize()
    
    return jsonify({
        'task_id': task_id,
        'queue_position': queue_position,
        'status': 'queued'
    })

@app.route('/status/<task_id>')
def get_status(task_id):
    status = task_status.get(task_id, "not_found")
    
    if status == "queued":
        # Calculate current position in queue
        queue_position = task_queue.qsize()
        return jsonify({
            'status': status,
            'queue_position': queue_position
        })
    elif status == "error":
        error_msg = task_results.get(task_id, "Unknown error")
        return jsonify({
            'status': status,
            'error': error_msg
        })
    else:
        return jsonify({'status': status})

@app.route('/download/<task_id>')
def download_audio(task_id):
    if task_id not in task_results:
        return "Task not found", 404
    
    if task_status.get(task_id) != "completed":
        return "Task not completed", 400
    
    buffer = task_results[task_id]
    buffer.seek(0)
    
    # Clean up
    del task_results[task_id]
    del task_status[task_id]
    
    return send_file(buffer, mimetype='audio/wav', as_attachment=True, download_name=f'speech_{task_id}.wav')

@click.command()
@click.option('--max-tasks', default=4, help='Maximum number of concurrent tasks')
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--gui/--no-gui', default=True, help='Enable or disable GUI')
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
@click.option('--threads', default=4, help='Number of server threads')
def main(max_tasks, host, port, gui, debug, threads):
    """ChatterboxTTS Web Server"""
    global MAX_CONCURRENT_TASKS, semaphore
    
    MAX_CONCURRENT_TASKS = max_tasks
    semaphore = threading.Semaphore(MAX_CONCURRENT_TASKS)
    
    click.echo(f"Starting ChatterboxTTS server...")
    click.echo(f"Max concurrent tasks: {max_tasks}")
    click.echo(f"Host: {host}")
    click.echo(f"Port: {port}")
    click.echo(f"GUI enabled: {gui}")
    click.echo(f"Debug mode: {debug}")
    
    # Initialize model
    initialize_model()
    
    # Start worker thread
    worker_thread = threading.Thread(target=worker, daemon=True)
    worker_thread.start()
    
    if not gui:
        # Remove the GUI route if GUI is disabled
        app.view_functions.pop('index', None)
    
    if debug:
        click.echo("Running in debug mode with Flask development server")
        app.run(host=host, port=port, debug=True)
    else:
        click.echo(f"Running production server with {threads} threads")
        serve(app, host=host, port=port, threads=threads)

if __name__ == '__main__':
    main()