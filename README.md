# GraphFix AI

GraphFix AI is a conversational AI assistant that enables maintenance engineers and technical professionals to analyze maintenance reports through natural language. It transforms unstructured maintenance reports into a  knowledge graph, allowing users to ask questions about assets, components, failures, maintenance actions, and their relationships.

Instead of manually skimming through large collections of maintenance documents, users can interact with the system conversationally to retrieve relevant maintenance history and discover relationships.

![alt text](assets/image.png)

## Architecture

![alt text](assets/architecture.png)

## 🛠️ Tech Stack

### 🌐 Frontend

<p align="left">
  <img src="https://skillicons.dev/icons?i=nextjs,react,ts,tailwind" />
</p>

- **Framework:** Next.js 16
- **UI Library:** React 19
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4
- **Icons:** Lucide React

---

### ⚙️ Backend

<p align="left">
  <img src="https://skillicons.dev/icons?i=python,fastapi" />
</p>

- **Framework:** FastAPI
- **Server:** Uvicorn
- **Data Validation:** Pydantic
- **PDF Processing:** PyMuPDF (`pymupdf4llm`)

---

### 🤖 AI & GraphRAG

<p align="left">

![LangChain](https://img.shields.io/badge/LangChain-121212?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge)
![Semantic Router](https://img.shields.io/badge/Semantic%20Router-2563EB?style=for-the-badge)
![GraphRAG](https://img.shields.io/badge/GraphRAG-0F172A?style=for-the-badge)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)

</p>

- **LLM:** Groq (`llama-3.3-70b-versatile`)
- **AI Framework:** LangChain
- **Retrieval:** GraphRAG
- **Knowledge Graph QA:** GraphCypherQAChain
- **Intent Routing:** Semantic Router
- **Embeddings:** Hugging Face Sentence Transformers (`BAAI/bge-small-en-v1.5`)

---

### 🗄️ Database
- **Graph Database:** Neo4j Aura
- **Driver:** Neo4j Python Driver

---
## 📂 Project Structure

```text
GraphFix-AI/
│
├── README.md
├── LICENSE
├── assets/                    
│
├── backend/
│   ├── app/
│   │   ├── models/             # Data schemas
│   │   ├── prompts/            # LLM prompts
│   │   ├── services/           # GraphRAG pipeline
│   │   │   ├── text_extraction.py
│   │   │   ├── llm_extraction.py
│   │   │   ├── ontology_mapper.py
│   │   │   ├── graph_builder.py
│   │   │   ├── qa_service.py
│   │   │   └── router/
│   │   ├── exceptions/
│   │   └── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   ├── components/
│   │   ├── chatbar/
│   │   └── sidebar/
│   ├── public/
│   └── package.json
│
├── scripts/
│
└── .env.example
```
## 🚀 Installation & Setup

Follow the steps below to set up and run **GraphFix AI** locally.

---

### 1. Clone the Repository

Clone the repository and navigate into the project directory.

```bash
git clone https://github.com/your-username/GraphFix-AI.git
cd GraphFix-AI
```

---

### 2. Set Up Neo4j

GraphFix AI requires a Neo4j database instance.

You can use one of the following:

- **Neo4j AuraDB** (Recommended)
- **Neo4j Desktop**
- **Neo4j Docker Container**

---

### 3. Backend Setup

Navigate to the backend directory.

```bash
cd backend
```

Create a virtual environment using **uv**.

```bash
uv venv
```

Activate the virtual environment.

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install the required dependencies.

```bash
uv pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file inside the `backend` directory and add the following:

```env
# Groq API
GROQ_API_KEY=your_groq_api_key

# Neo4j Database
DATABASE_URI=your_neo4j_uri
DATABASE_USERNAME=your_username
DATABASE_PASSWORD=your_password
```

---

### 3. Run the Backend

Start the FastAPI development server.

```bash
uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://localhost:8000
```

## ✅ You're Ready!

Open your browser and navigate to:

```text
http://localhost:3000
```
## 💡 Example Queries

After uploading one or more maintenance reports, try asking questions like:

### 📄 Maintenance History

- "Show me all reports related to **[Asset Name]**."
- "List all maintenance actions performed on **[Component Name]**."
- "Which assets experienced **[Failure Mode]**?"

### 🔍 Failure Analysis

- "What caused the failure of **[Asset Name]**?"
- "Which components were affected by **[Failure Mode]**?"
- "How was **[Issue]** resolved?"

### 🔗 Relationship Discovery

- "What components are associated with **[Asset Name]**?"
- "Show the maintenance history of **[Asset Name]**."
- "Which assets have experienced similar failures?"

### 💬 Conversational Follow-ups

The assistant supports contextual conversations.

**Example**

> **User:** What failed on **[Asset Name]**?  
> **Assistant:** ...  
> **User:** How was it repaired?

### 🌍 General Knowledge

- "What is preventive maintenance?"
- "What is predictive maintenance?"
- "What are common causes of corrosion in industrial equipment?"
