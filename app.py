from flask import Flask, render_template, request, jsonify
import os
import pyaudio
import wave
from pydub import AudioSegment
import openai
from dotenv import load_dotenv
import base64

app = Flask(__name__)

# Path to store the recorded audio files
AUDIO_FOLDER = 'flask_app/recordings'
app.config['UPLOAD_FOLDER'] = AUDIO_FOLDER


# Load API key and organization from environment variables
load_dotenv("secrets.env")
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORGANIZATION")

client = openai.OpenAI(
    api_key=openai.api_key,
    organization=openai.organization
)


# Function to record audio and save it to a WAV file
def record_audio(file_name, duration=20, channels=1, sample_rate=44100, chunk_size=1024):
    audio = pyaudio.PyAudio()

    # Open the microphone stream
    stream = audio.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk_size)

    frames = []

    # Record audio frames
    for _ in range(0, int(sample_rate / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(data)

    # Close the microphone stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded audio to a WAV file
    wf = wave.open(file_name, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()


# Convert WAV to MP3
def convert_wav_to_mp3(input_file, output_file):
    sound = AudioSegment.from_wav(input_file)
    sound.export(output_file, format="mp3")


# Placeholder functions for Whisper, GPT-4, and TTS
def convert_audio_to_text(audio_file):
    """
    Converting audio to text using Whisper
    :param audio_file: format .mp3
    :return: String (text)
    """
    audio_file = open(audio_file, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="en"
    )
    print(transcription.text)
    return str(transcription.text)



conversation_history = []
def generate_response(input_text):
    """
    Generating response using GPT-4
    :param input_text: String (audio file that have been converted into text)
    :return: String (repsonse from GPT 4
    """

    initial_prompt = """
        You are a case interview preparation assistant. 
        You are going to conduct a case interview. The case interview will consist of a prompt about a business problem, 1 approach structuring question, 1 qualitative question, 1 quantitative question, and a request for a recommendation. 
        After the prompt about a business problem the candidate can ask clarifying questions about the case, but he doesn't have to. After that he is expected to come up with a structured approach to the problem. After he comes up with an approach, ask him a qualitative question related to the problem.
        As part of the quantitative question ask the candidate to calculate something related to the business problem.
        After the candidate provides a recommendation, you need to strictly evaluate how a candidate performed, explain why you evaluated him like that and suggest areas of improvement. Don't share with the candidate that you are going to evaluate his performance.
        """

    messages = [{'role': 'system', 'content': initial_prompt}]


    for msg in conversation_history:
        messages.append({'role': 'user', 'content': msg})

    messages.append({'role': 'user', 'content': input_text})

    response = client.chat.completions.create(
  model="ft:gpt-3.5-turbo-0125:personal::99Vw4GZW",
  messages=messages,
  max_tokens= 150,
)

    # Extract and print the model's reply
    reply = response.choices[0].message.content
    print(reply)

    # Update conversation history
    conversation_history.append(input_text)
    conversation_history.append(reply)
    return reply


def convert_text_to_speech(text):
    """
    Convert text to speech using TTS
    :param text: String by response of GPT-4
    :return: audio file (.mp3 format)
    """
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    return response.content


# Home route
@app.route('/')
def home():
    return render_template('index.html')


# Answer route to handle audio recording
@app.route('/answer', methods=['POST'])
def answer():
    if request.method == 'POST':
        # Record audio
        audio_file = os.path.join(app.config['UPLOAD_FOLDER'], 'input.wav')
        record_audio(audio_file)

        # Convert to MP3
        # mp3_file = os.path.join(app.config['UPLOAD_FOLDER'], 'output.mp3')
        # convert_wav_to_mp3(audio_file, mp3_file)

        # Convert audio to text using Whisper
        input_text = convert_audio_to_text(audio_file)

        # Generate response using GPT-4
        response_text = generate_response(input_text)

        # Convert response text to speech using TTS
        speech_response = convert_text_to_speech(response_text)
        speech_base64 = base64.b64encode(speech_response).decode('utf-8')

        return jsonify({'text_response': response_text, 'speech_response': speech_base64})


if __name__ == '__main__':
    app.run(debug=True)
