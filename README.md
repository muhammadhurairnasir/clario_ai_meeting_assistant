# Clario AI Meeting Assistant

An AI-powered web application that transcribes audio meetings, generates condensed summaries, extracts action items (assigned tasks and deadlines), and maps knowledge graphs.

## Prerequisites

- Python 3.9+
- [FFmpeg](https://ffmpeg.org/) (Required for Whisper audio decoding)

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Clario_Project_flask
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the spaCy language model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Running the Application

1. **Start the Flask Server**
   ```bash
   python app.py
   ```

2. **Access the App**
   Open your browser and navigate to:
   `http://127.0.0.1:5000`

---
*Note: The first time you process a meeting, the BART summarization and Whisper models will be downloaded automatically (~2-3 GB). Subsequent runs will use the cached models and execute faster.*
