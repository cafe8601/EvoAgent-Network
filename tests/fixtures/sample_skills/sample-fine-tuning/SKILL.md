---
name: sample-fine-tuning
description: Sample skill for testing fine-tuning related queries. Use for LoRA, QLoRA, and Axolotl fine-tuning tasks.
version: 1.0.0
author: Test Author
license: MIT
tags: [Fine-Tuning, LoRA, QLoRA, Axolotl, PEFT]
dependencies: [transformers>=4.40.0, peft>=0.10.0]
---

# Sample Fine-Tuning SKILL

## Quick Start

This is a sample SKILL for testing purposes.

```bash
pip install peft transformers
```

## Common Workflows

### Workflow 1: LoRA Fine-tuning

```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05
)
model = get_peft_model(base_model, config)
```

## When to Use

- Fine-tuning LLMs with limited GPU memory
- Quick adaptation to specific domains
- Parameter-efficient training

## Common Issues

**Issue: OOM Error**
Solution: Reduce batch size or use gradient checkpointing.
