# Clario AI Meeting Assistant

An AI-powered web application that transcribes audio meetings, generates condensed summaries, extracts action items (assigned tasks, deadlines, and urgency/priority), and visualizes the results using advanced business analytics (Knowledge Graphs, Assignee distribution, Task Priority, and Completion Status charts).

## Prerequisites

- Python 3.9+
- [FFmpeg](https://ffmpeg.org/) (Required for Whisper audio decoding)

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/muhammadhurairnasir/clario_ai_meeting_assistant.git
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

## Testing with Dummy Data

If you want to instantly load a fully-populated dummy meeting with generated graphs and analytics (ideal for demonstrations), run the database seeder script:
```bash
python seed.py
```
*Note: This will truncate your existing database and recreate a pristine testing environment with the demo credentials `demo@clario.ai` / `Demo1234!`.*

---
*Note: The first time you process a meeting, the BART summarization and Whisper models will be downloaded automatically (~2-3 GB). Subsequent runs will use the cached models and execute faster.*
