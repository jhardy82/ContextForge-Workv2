---
description: "LangChain Python patterns, Runnable interface, chat models, and vectorstores"
applyTo: "langchain*, LangChain*, LCEL*, RAG*, retriever*, vectorstore*, chat model*, embedding*"
---

# LangChain Quick Reference

## Runnable Interface

```python
# LCEL composition
chain = prompt | chat_model | output_parser

# Execution methods
result = chain.invoke(input)           # Single
results = chain.batch([inputs])        # Parallel
async for chunk in chain.astream(input):  # Stream
    print(chunk)
```

## Chat Models

```python
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

chat = ChatOpenAI(model="gpt-4", temperature=0)
messages = [
    SystemMessage(content="You are helpful."),
    HumanMessage(content="What is LangChain?")
]
response = chat.invoke(messages)
```

## Tool Calling & Structured Output

```python
# Bind tools
chat_with_tools = chat.bind_tools([my_tool])

# Structured output
chat_structured = chat.with_structured_output(MySchema)
```

## RAG Pattern

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()
chain = retriever | prompt | llm | parser
```

## Best Practices
- Use `batch()` with `max_concurrency` for parallel calls
- Prefer streaming for chat UIs
- Use tags/metadata in `RunnableConfig` for LangSmith tracing

## Full Reference
See `.github/instructions/archive/langchain-python-full.md`
