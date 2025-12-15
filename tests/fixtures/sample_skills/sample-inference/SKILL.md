---
name: sample-inference
description: Sample skill for testing inference and model serving queries. Use for vLLM, TGI, and model deployment tasks.
version: 1.0.0
author: Test Author
license: MIT
tags: [Inference, Serving, vLLM, TGI, Deployment]
dependencies: [vllm>=0.3.0, transformers>=4.40.0]
---

# Sample Inference SKILL

## Quick Start

```bash
pip install vllm
```

## Common Workflows

### Workflow 1: vLLM Server

```python
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-2-7b-chat-hf")
sampling = SamplingParams(temperature=0.7, max_tokens=256)
outputs = llm.generate(["Hello, how are you?"], sampling)
```

## When to Use

- High-throughput inference
- Production model serving
- Low-latency requirements

## Common Issues

**Issue: CUDA OOM**
Solution: Reduce max_model_len or use tensor parallelism.
