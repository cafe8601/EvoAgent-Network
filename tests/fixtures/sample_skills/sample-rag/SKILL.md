---
name: sample-rag
description: Sample skill for testing RAG (Retrieval-Augmented Generation) queries. Use for vector database, embedding, and retrieval tasks.
version: 1.0.0
author: Test Author
license: MIT
tags: [RAG, Vector Database, Retrieval, Embedding, ChromaDB]
dependencies: [chromadb>=0.4.0, sentence-transformers>=2.2.0]
---

# Sample RAG SKILL

## Quick Start

```bash
pip install chromadb sentence-transformers
```

## Common Workflows

### Workflow 1: Basic RAG Setup

```python
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.SentenceTransformerEmbeddingFunction()
collection = client.get_or_create_collection("documents", embedding_function=ef)
```

## When to Use

- Question answering over documents
- Knowledge base search
- Semantic similarity search

## Common Issues

**Issue: Slow indexing**
Solution: Use batch operations and GPU embeddings.
