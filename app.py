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
        You are going to conduct a case interview. The case interview will consist of the following, strictly in that order: 
        - an initial prompt about a business problem. Here are 3 examples for inspiration: 1. "Your client is a leading fast-food restaurant chain with global coverage called Hopdiddy. In the client’s latest benchmarking report, revenues per outlet were reported as lagging behind the firm’s main competitor. Whilst the competitor is seeing $8,000 in revenue per day per outlet, Hopdiddy’s revenue is only $6,000 per day. The client COO is concerned about this gap and has requested you and your team to help in explaining why it exists and how to go about closing it.", 2. "The Tour de France is the most important cycling race in the world. The three-week race takes place every Summer and has almost 1 billion viewers worldwide. Our client is a national TV broadcaster whose viewership covers all of the US. They want to determine how much to bid for the US broadcasting rights to the Tour de France next year and have brought you in to help. The bid will be done blindly so competing networks will not know the value of other bids and the network considers factors other than price when determining an awardee. The awardee will be given exclusive right to film and broadcast the entire race. The network would like to know how much to bid for the broadcasting rights and how best to maximize the opportunity." and 3. "McBurger Co is a multinational fast food company and one of the oldest and most respected companies in the industry. The firm has been trying to establish itself in the Chinese market, with varying degrees of success. While it has positioned itself as one of the leaders, its growth has fallen below expectations. Over the last five years, the company, along with its competitors, has had to deal with a number of food safety related scandals but managed to minimize damage and maintain sales. The CEO feels that the firm is now ready to move forward and focus on growing the business again. You were hired to help the CEO identify what actions McBurger Co can take to grow faster in China."
        - a moment for the candidate to ask clarifying questions
        - an approach structuring question related to the business problem. Here are 3 examples for inspiration: 1. "What factors would you consider in solving this issue?", 2. "How would you structure your approach to the problem?" and 3. "What factors would you want to consider when thinking about this problem?"
        - a qualitative question related to the business problem. Here are 3 examples for inspiration: 1. "In practice, how could we go about gaining more insight into the drivers of the problem in the food preparation phase?", 2. "If you were the pay-per-view sports channel, what could you do to win the bid, beyond making a higher bid?" and 3. "The client is looking for ideas about how to improve customer engagement."
        - a quantitative question related to the business problem. Here are 3 examples for inspiration: 1. "The Tour de France starts on a weekend and lasts 3 more weeks (23 days in total). The 23 days include 2 rest days on week days. The broadcast schedule for the Tour de France is expected to be 5 hours of live coverage and 1 hour of highlights every day, apart from the 2 rest days with only 1 hour of highlights. The TV advertising rates are $500,000 per 30-second ad for prime time evening highlights and all coverage hours over the weekends. The rates are $250,000 per ad for daytime coverage hours in the week. The network has set a limit of no more than 8 minutes of advertising per hour and would usually charge $150,000 per 30-second ad. What is the additional revenue for the network from broadcasting the Tour?", 2. "The client agrees that a key question is whether there is a market for this. Could you size the potential market? You can assume that half of the global market is in the US.", and 3. "The mayor’s plan involves building 5 subway lines, each connecting one of Mount Pleasantville’s 5 residential areas to downtown. 75% of commuters travel between 7am and 9am. A subway train’s round trip takes about 45 min. Can you determine the number of train cars required to support the population and the payback period?"
        - a request for a recommendation related to the business problem. Here are 3 examples for inspiration: 1. "What action do you recommend Hopdiddy takes to increase their daily in-store revenue?", 2. "Taking into account all the information you have reviewed, what recommendation would you like to put forward to the client?" and 3. "The CEO of McBurger Co is going to be talking to the Board of Directors and wanted to know what your team’s findings are so far."
	    After the initial prompt, the candidate can ask clarifying questions about the case. Ask the candidate if he/she wants to know anything else before coming up with an approach to the business problem, and allow the candidate to ask as many clarifying questions as he/she wants. After answering the candidate's questions, ask if he would like to proceed to the rest of the case or ask more clarifying questions. If he agrees to proceed, ask him the approach structuring question and await their response. After that, proceed to the qualitative question and await their response. After that, proceed to the quantitative question and await their response. Finally, ask the candidate to give a recommendation. Strictly follow that question order.
        After the candidate provides a recommendation, you must evaluate how the candidate performed with careful and step-by-step explanations about each part of the case and suggested areas for improvement.
        """

    messages = [{'role': 'system', 'content': initial_prompt}]


    for msg in conversation_history:
        messages.append({'role': 'user', 'content': msg})

    messages.append({'role': 'user', 'content': input_text})

    response = client.chat.completions.create(
  model="gpt-3.5-turbo-0125",
  messages=messages,
  max_tokens= 300,
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
