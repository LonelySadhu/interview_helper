```markdown
# Interview Helper

This project aims to create an AI assistant for real-time interviews  using Python,  
OpenAI, and WebSockets. It integrates the Vosk speech-to-text model,  
Watchdog for file monitoring, and FastAPI for interacting with WebSocket.

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
1. Âownload and install from https://vb-audio.com/Cable/ VB-CABLE Driver  
 for recording interviews
2. Download the Vosk model:
- Visit https://alphacephei.com/vosk/models and download the model for your desired language.
- Extract the downloaded archive and place the folder with name 'model' in the `interview_helper` directory.

3. Create .env file like env_example and put api key and assistant_id your openai assistant to it
4. Promt for an openai assistant:  
>You are acting as a personal assistant to a software developer.  You are interviewing >for a software developer position at a development company. You receive the >interviewer's speech in the form of text input. You extract only technical questions >from the interviewer from the entire text and give answers to them. The answers >should be concise and precise.  Accompany them with code examples in python if it >helps to understand the essence of the question and if the interviewer requires it. >Always answer in Russian. Please provide answers in HTML format. 
>Plain text format with html standart like `<p>`, `<ul>`, `<ol>`, `<li>` etc.
> Wrap all code samples (regardless of programming language) in `<pre>` and `<code>` 
> tags so that they are properly displayed as formatted code.
> Follow the HTML structure and make sure that tags are properly nested.
> Example:
```
<p>function example on Python:</p>
<pre><code>def greet(name):
    return f"Hello, {name}!"
</code></pre>
```

5. Start the code by ```bash
poetry run python main.py
```
6. Open with browser index.html file when it would be printed in the console


7. Index.html will connect by WebSocket to http://127.0.0.1:8000/ws.


## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

