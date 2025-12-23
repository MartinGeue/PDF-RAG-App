## Installation
You need to install the better Python package manager **[uv](https://docs.astral.sh/uv/getting-started/installation/)** to run this app.
You also need to install **[Ollama](https://ollama.com/download)**. (Tested with Ollama v0.1.3.4)

### License Information
This project uses **[Ollama](https://ollama.com/)** (License: [MIT](https://github.com/ollama/ollama/blob/main/LICENSE)) and **[uv](https://docs.astral.sh/uv/)** (License: [Apache 2.0](https://github.com/astral-sh/uv/blob/main/LICENSE)). Please review the respective license terms for each tool.

### Privacy Notice
All data and requests are processed locally on your machine. No data is transmitted to external servers.

### Tested Versions
- Ollama: v0.1.3.4 (other versions may work but have not been tested)
- Python: 3.13

### Disclaimer
This project is provided as-is, without warranty. Use at your own risk.

### Commands After Installation
- **`ollama run ministral-3:3b`** (LLM for offline capability)
- **`uv python install 3.13`** (required Python version)
- **`uv init`**
- **`uv venv --python 3.13`**
- **`uv pip install -r requirements.txt`**
- **`uv run main.py`**

### Additional Information
- After running **`uv run main.py`**, navigate to [http://localhost:5000/](http://localhost:5000/) in your web browser.
- You can now upload a PDF file and ask your questions.
- To stop the app, press **`[CTRL] + [C]`** in the console.
- To restart, simply run **`uv run main.py`** again.
