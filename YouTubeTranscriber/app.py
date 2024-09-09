import os
import speech_recognition as sr
import pyttsx3
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables for Google Gemini API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the recognizer
r = sr.Recognizer()

# Set up prompt for summary
prompt = """You are a YouTube video summarizer. You will take the transcript text
and summarize the entire video, providing important points within 250 words. Please provide the summary of the text given here: """

# Initialize pyttsx3 engine for text-to-speech
def SpeakText(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()

# Extract video ID from YouTube link
def extract_video_id(youtube_url):
    if "v=" in youtube_url:
        return youtube_url.split("v=")[1]
    elif "youtu.be/" in youtube_url:
        return youtube_url.split("youtu.be/")[1]
    return None

# Get transcript using YouTubeTranscriptApi
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception:
        return None

# Use Gemini model to generate content summary
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Speech-to-text fallback
def generate_speech_to_text():
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.2)
            print("Listening...")
            audio = r.listen(source)
            MyText = r.recognize_google(audio)
            MyText = MyText.lower()
            return MyText
    except sr.RequestError:
        print("Could not request results from speech recognition service.")
    except sr.UnknownValueError:
        print("Speech not recognized.")
    return None

# Main program using Streamlit for UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if not transcript_text:
        st.write("No transcript found. Please speak the video content.")
        SpeakText("No transcript available, switching to speech-to-text.")
        transcript_text = generate_speech_to_text()

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary)
    else:
        st.write("Unable to generate transcript or speech-to-text output.")
