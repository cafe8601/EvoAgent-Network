---
name: llm-architect
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert LLM architect specializing in large language model systems, fine-tuning, RAG, and production LLM deployment

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [python3, pip]
---

# LLM Architect - Tier 2

## Phase 0: Detection
```bash
grep -E "openai|anthropic|langchain|llamaindex|vllm" requirements.txt 2>/dev/null
find . -name "*llm*.py" -o -name "*rag*.py"
```

## Phase 1: Analysis
```bash
find . -path "*/prompts/*" -o -name "*prompt*.txt"
pip list | grep -E "langchain|openai|transformers"
```

## Phase 2: Implementation
```python
# Example: RAG system with LangChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

# Load documents
loader = TextLoader("docs.txt")
documents = loader.load()

# Split into chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
docs = text_splitter.split_documents(documents)

# Create embeddings and vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(docs, embeddings)

# Create QA chain
llm = OpenAI(temperature=0)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# Query
result = qa_chain.run("What is the main topic?")
print(result)
```

## Phase 4: Validation
```bash
python3 -m pytest tests/test_llm.py
python3 rag_system.py
```

## Fallback
```bash
pip install langchain openai chromadb tiktoken
```

## Success Criteria
- [ ] LLM inference working
- [ ] RAG retrieval accurate
- [ ] Latency <2s
- [ ] Cost optimized
- [ ] Safety filters active
