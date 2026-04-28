## Installing libraries

pip install faiss-cpu numpy python-dotenv pdfplumber ollama 

## Using Ollama for local models

In this example we will use Qwen2.5:1.5b (1.5 billion parameters ±1Gb) for the text generation and nomic-embed-text

URL: https://ollama.com/download

ollama serve 
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text

Example Usage for generation model:

```python
import ollama

response = ollama.chat(
    model="qwen2.5:1.5b",
    messages=[
        {"role": "user", "content": "Explain what a constitution is"}
    ]
)

print(response["message"]["content"])
```

We can also chat freely with the model using 

ollama run qwen2.5:1.5b

