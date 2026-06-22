from openai import OpenAI
import base64
import gradio as gr # oh yeah!

client = OpenAI(api_key="YOUR_API_KEY_HERE")

# --------------------------------------
# Dummy Exhibition Data (context)
# --------------------------------------
EXHIBITION_DATA = {
    "name": "FutureTech Expo 2025",
    "location": "Hall 3, Expo Center Karachi",
    "timing": "10 AM to 7 PM",
    "booths": [
        "AI & Robotics Hall",
        "AR/VR Immersion Zone",
        "3D Avatar Interaction Booth",
        "Green Energy Innovations",
        "Next-Gen Gaming Arena"
    ],
    "special_events": [
        {"time": "2:00 PM", "event": "Keynote: The Future of AI Agents"},
        {"time": "4:00 PM", "event": "VR/AR Demo Live Show"}
    ]
}

CONTEXT = f"""
You are an AI Exhibition Guide at **{EXHIBITION_DATA['name']}**.
Location: {EXHIBITION_DATA['location']}
Timings: {EXHIBITION_DATA['timing']}.

Available Booths:
- """ + "\n- ".join(EXHIBITION_DATA['booths']) + """

Today's Events:
""" + "\n".join([f"- {e['time']}: {e['event']}" for e in EXHIBITION_DATA['special_events']]) + """

Your job:
- Greet visitors
- Answer exhibition-related questions
- Use only the info above
- Respond short, friendly, helpful
"""


# --------------------------------------
# Speech-to-Text (Whisper)
# --------------------------------------
def speech_to_text(audio_file):
    print("Transcribing audio...")

    with open(audio_file, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-tts",  # Whisper API
            file=f
        )

    return transcript["text"]


# --------------------------------------
# LLM Query
# --------------------------------------
def ask_llm(question):
    prompt = f"{CONTEXT}\n\nVisitor: {question}\nGuide:"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a friendly exhibition guide."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message["content"]


# --------------------------------------
# Text-to-Speech (OpenAI)
# --------------------------------------
def text_to_speech(text):
    print("Generating speech...")

    audio_res = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
        format="wav"
    )

    audio_bytes = audio_res.read()
    return audio_bytes


# --------------------------------------
# Main Gradio Logic
# --------------------------------------
def voice_chat(audio, history):
    if audio is None:
        return history, None, "Please say something."

    # 1️⃣ Speech → Text
    user_text = speech_to_text(audio)

    # 2️⃣ Get LLM Response
    bot_text = ask_llm(user_text)

    # 3️⃣ Text → Speech
    bot_audio = text_to_speech(bot_text)

    # 4️⃣ Update History
    history.append((user_text, bot_text))

    return history, bot_audio, bot_text


# --------------------------------------
# UI
# --------------------------------------
with gr.Blocks(title="LLM Voice Exhibition Guide") as demo:
    gr.Markdown("### 🧑‍🚀 🎤 Voice-Enabled Virtual Exhibition Guide")
    chatbot = gr.Chatbot()
    
    with gr.Row():
        audio_in = gr.Audio(sources=["microphone"], type="filepath", label="Hold to Speak")
    
    speak_btn = gr.Button("Ask the Guide")
    bot_audio = gr.Audio(label="Guide Voice Reply")
    bot_text = gr.Textbox(label="Recognized / Bot Text")

    speak_btn.click(
        voice_chat,
        inputs=[audio_in, chatbot],
        outputs=[chatbot, bot_audio, bot_text]
    )

demo.launch(share=True)
