import os
from gtts import gTTS

def generate_audio(text, filename):
    print(f"Generating {filename}...")
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(filename)
    print(f"Saved {filename}")

if __name__ == "__main__":
    out_dir = "sample_audios"
    os.makedirs(out_dir, exist_ok=True)

    meetings = {
        "engineering_standup.mp3": (
            "Good morning team. Let's do a quick standup. "
            "Sarah, please review the pull requests for the frontend dashboard today. "
            "John will deploy the new database schema by tomorrow afternoon. "
            "We also have a minor bug in the login flow. Dave needs to check the authentication logs "
            "when he has some free time. That's all for today."
        ),
        "client_kickoff.mp3": (
            "Hello everyone, welcome to the kickoff call with the new enterprise client. "
            "This project is extremely time-sensitive. "
            "Alice, you must finalize the security compliance document immediately, this is urgent. "
            "Bob, please prepare the initial architectural diagrams for their review on Friday. "
            "We cannot afford any delays here, so everyone needs to stay focused."
        ),
        "marketing_sync.mp3": (
            "Alright, let's sync on the upcoming product launch. "
            "The social media campaign looks good, but Emma needs to schedule the posts for next week. "
            "Liam, please reach out to our influencer partners to confirm their availability. "
            "Also, someone must double-check the billing configuration before we go live, this is critical."
        )
    }

    for filename, text in meetings.items():
        filepath = os.path.join(out_dir, filename)
        generate_audio(text, filepath)
    
    print("\n✅ All sample audios generated successfully in the 'sample_audios' folder!")
