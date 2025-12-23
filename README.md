## Installation
You need to install the better Python package manager [uv](https://docs.astral.sh/uv/getting-started/installation/) to run this app.
You also need to install [Ollama](https://ollama.com/download). (no problems with Ollama v0.13.4)

### Commands After Installation
- <b>ollama run ministral-3:3b</b> (LLM for offline capability)
- <b>uv python install 3.13</b> (Python version needed)
- <b>uv init</b>
- <b>uv venv --python 3.13</b>
- <b>uv pip install -r requirements.txt</b>
- <b>uv run main.py</b>

### Additional Information
- After the '<b>uv run main.py</b>' command, you can navigate in your web browser 
to [http://localhost:5000/](http://localhost:5000/)
- You can now upload a PDF file and ask your questions
- To stop the app, just press <b>[CTRL] + [C]</b> simultaneously on your keyboard 
while you are in the console where the Python script is running
- If you want to start the app again, simply type '<b>uv run main.py</b>' again
