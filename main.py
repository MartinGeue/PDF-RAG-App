import os, threading, uuid, chromadb, shutil
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama

DATA_PATH = r"data"
CHROMA_PATH = r"chroma"
ALLOWED_EXT = {"pdf"}

if os.path.exists(DATA_PATH):
    shutil.rmtree(DATA_PATH)
if os.path.exists(CHROMA_PATH):
    shutil.rmtree(CHROMA_PATH)
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)

app = Flask(__name__, template_folder='.')
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(
    name="rag",
    metadata={
        "hnsw:space": "cosine",
        "hnsw:search_ef": 400, # max 500  
        "hnsw:construction_ef": 300, # max 400  
        "hnsw:M": 64, # max 128           
    }
)

ingest_state = {"state": "idle", "message": "", "filename": ""}
chain = None
current_pdf = None
ingest_lock = threading.Lock()

def set_state(s, msg="", filename=""):
    ingest_state["state"] = s
    ingest_state["message"] = msg
    ingest_state["filename"] = filename

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

def ingest(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,        
        chunk_overlap=200,     
        separators=[
            "\n\n\n",          
            "\n\n",            
            "\n",              
            ". ", "! ", "? ",  
            " ",               
        ],
        is_separator_regex=False,
    )

    chunks = text_splitter.split_documents(pages)
    documents = []
    metadata = []
    ids = []
    i = 0

    for chunk in chunks:
        documents.append(chunk.page_content)
        ids.append(str(uuid.uuid4()))
        metadata.append(chunk.metadata)
        i += 1

    collection.upsert(
        documents=documents,
        metadatas=metadata,
        ids=ids
    )

def build_chain(user_query):
    model = ChatOllama(model="ministral-3:3b")

    results = collection.query(
        query_texts=[user_query],
        n_results=10
    )

    context_string = "\n".join(results['documents'][0][:4])

    template = """
    [Instructions] 
    ## Role
    You are a document assistant. Answer the question **strictly** based on the provided context.
    ## Guidelines
    - Use only plain text or Markdown in your responses
    - If the question cannot be answered using the provided context, state that the question needs to be rephrased or clarified
    - Never include information, suggestions, or interpretations that are not directly supported by the context
    - Strictly limit your responses to the provided context
    **Always follow these guidelines without exception**
    [/Instructions]
    [Instructions] 
    Question: {input}
    Context: {context}
    Answer:
    [/Instructions]
    """
    
    prompt = PromptTemplate.from_template(template)

    chain = prompt | model
    response = chain.invoke({
        "input": user_query,
        "context": context_string
    })
    
    return {
        "answer": response.content, 
        "retrieved": context_string
    }

def rebuild_from_pdf(pdf_path):
    global current_pdf
    with ingest_lock:
        set_state("ingesting", "Ingest gestartet...", os.path.basename(pdf_path))
        try:
            ingest(pdf_path)
            current_pdf = pdf_path
            set_state("ready", "Ingest abgeschlossen. Fragen möglich.", os.path.basename(pdf_path))
        except Exception as e:
            set_state("error", f"Ingest-Fehler: {e}")
            print("Ingest error:", e)
    return True

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/ingest_state", methods=["GET"])
def get_ingest_state():
    return jsonify(ingest_state)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "Keine Datei"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "Nur PDF erlaubt"}), 400

    set_state("uploading", "Upload läuft...", file.filename)
    filename = secure_filename(file.filename)
    dest = os.path.join(DATA_PATH, filename)
    file.save(dest)

    def bg():
        try:
            set_state("ingesting", "Ingest läuft...", file.filename)
            rebuild_from_pdf(dest)
        except Exception as e:
            set_state("error", f"Ingest-Fehler: {e}")
            print("Ingest error:", e)
    threading.Thread(target=bg, daemon=True).start()

    return jsonify({"filename": filename}), 200

@app.route("/ask", methods=["POST"])
def ask_route():
    body = request.get_json() or {}
    query = (body.get("query") or "").strip()
    if not query:
        return jsonify({"answer": ""})
    try:
        result = build_chain(query)
        return jsonify({
            "answer": result["answer"],
            "retrieved": result["retrieved"]
        }) 
    except Exception as e:
        return jsonify({
            "answer": f"{e}",
            "retrieved": ""
        }), 500

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(DATA_PATH, filename, as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)