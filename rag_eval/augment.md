# Augment

This assignment is part of the RAG Evaluation. The goal is to build a model that can generate answers using augmented context. You're given a prompt and a list of contexts. Each context is upto 10Mb of text. The answer should be a sentence or a short paragraph that is relevant to the context.

Here are few ideas to get started:
- Prompt Improvements: Will a chain of density or chain of thought style prompt improve the performance?
- HyDE: Can you use HyDE to generate answers for each context?
- How can you make the model good at saying "I don't know" when it doesn't have enough information to answer the question?
    - Can you use a logprobs threshold to decide when to say "I don't know"?
- Chunking: Can you chunk the context into smaller pieces and generate answers for each chunk?

## Evaluation Criteria
- **Relevance**: How relevant is the answer to the context?
- **Consistency**: How consistent is the answer with the prompt?
- **Completeness**: How complete is the answer?
- **Latency**: How long does it take to generate the answer?

Bonus points for:
- **Novelty**: How novel is the approach?
- **Robustness**: How robust is the model to different contexts?
- **Efficiency**: How efficient is the model in terms of speed and resources?
- **Explainability**: How explainable is the model? E.g. citation of context
- **Streaming**: Does your service support streaming?

In due time, we'll share the metrics and their implementation details. We will not share the contexts which we'll use to query or ping your service. There are no context provided for testing the model. You can assume that the prompts will be in at least 3 languages, and the contexts will be from a variety of domains.

## Disqualification Criteria
- **Plagiarism**: Copying from others' work without citation. We encourage you to use the Internet to find solutions, but you should always cite the source.
- **Throughput**: If your service is not able to handle the load with graceful degradation, it will be disqualified.
- **Stability**: If the answers are not consistent across multiple queries, it will be disqualified.
- **Latency**: If the time to first token is higher than 5s, it will be disqualified.