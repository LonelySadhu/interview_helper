Apologies for the confusion. If you're using Poetry for managing your project dependencies, you'll need to adjust the installation instructions accordingly. Here's an updated README.MD that reflects this change:

```markdown
# Interview Helper

This project aims to create a real-time interview assistant using Python, OpenAI, and WebSockets. It integrates the Vosk speech-to-text model, Watchdog for file monitoring, and FastAPI for WebSocket communication.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/LonelySadhu.git
cd interview_helper
```

2. Create a virtual environment (optional but recommended):
```bash
poetry shell
```

3. Install the required packages:
```bash
poetry install
```

## Usage

1. Download the Vosk model:
- Visit https://alphacephei.com/vosk/models and download the model for your desired language.
- Extract the downloaded archive and place the folder with name 'model' in the `interview_helper` directory.

2. Create .env file like env_example and put api key and assistant_id your openai assistant to it
3. Open with browser index.html file when it would be printed in the console

4. Start monitoring folders for new audio files and text files:


5. Index.html will connect by WebSocket to http://127.0.0.1:8000/ws.


## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

