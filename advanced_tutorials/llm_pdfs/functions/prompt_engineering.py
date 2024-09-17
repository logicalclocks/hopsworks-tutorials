from typing import List, Tuple
from sentence_transformers import SentenceTransformer

def get_source(neighbors: List[Tuple[str, str, int, int]]) -> str:
    """
    Generates a formatted string for the sources of the provided context.

    Args:
        neighbors (List[Tuple[str, str, int, int]]): List of tuples representing document information.

    Returns:
        str: Formatted string containing document names, links, pages, and paragraphs.
    """
    return '\n\nReferences:\n' + '\n'.join(
        [
            f' - {neighbor[0]}({neighbor[1]}): Page: {neighbor[2]}, Paragraph: {neighbor[3]}' 
            for neighbor 
            in neighbors
        ]
    )

def get_context(neighbors: List[Tuple[str]]) -> str:
    """
    Generates a formatted string for the context based on the provided neighbors.

    Args:
        neighbors (List[Tuple[str]]): List of tuples representing context information.

    Returns:
        str: Formatted string containing context information.
    """
    return '\n\n'.join([neighbor[-1] for neighbor in neighbors])


def generate_prompt(context: str, question: str) -> str:
    """
    Generates a prompt for the AI assistant based on context and question.
    
    Args:
        context (str): Formatted string containing context information.
        question (str): The question to be included in the prompt.

    Returns:
        str: Formatted prompt for the AI assistant.
    """
    prompt_template = """
[INST] 
Instruction: You are an AI assistant specialized in regulatory documents. 
Your role is to provide accurate and informative answers based on the given context.
[/INST]

### CONTEXT:

{context}

### QUESTION:
[INST]{question}[/INST]
     """

    return prompt_template.format(
        context=context, 
        question=question,
    )


def get_neighbors(query: str, sentence_transformer: SentenceTransformer, feature_view, k: int = 10) -> List[Tuple[str, float]]:
    """
    Get the k closest neighbors for a given query using sentence embeddings.

    Parameters:
    - query (str): The input query string.
    - sentence_transformer (SentenceTransformer): The sentence transformer model.
    - feature_view (FeatureView): The feature view for retrieving neighbors.
    - k (int, optional): Number of neighbors to retrieve. Default is 10.

    Returns:
    - List[Tuple[str, float]]: A list of tuples containing the neighbor context.
    """
    question_embedding = sentence_transformer.encode(query)

    # Retrieve closest neighbors
    neighbors = feature_view.find_neighbors(
        question_embedding, 
        k=k,
    )

    return neighbors


def rerank(query: str, neighbors: List[str], reranker, k: int = 3) -> List[str]:
    """
    Rerank a list of neighbors based on a reranking model.

    Parameters:
    - query (str): The input query string.
    - neighbors (List[str]): List of neighbor contexts.
    - reranker (Reranker): The reranking model.
    - k (int, optional): Number of top-ranked neighbors to return. Default is 3.

    Returns:
    - List[str]: The top-ranked neighbor contexts after reranking.
    """
    # Compute scores for each context using the reranker
    scores = [reranker.compute_score([query, context[-1]]) for context in neighbors]

    combined_data = [*zip(scores, neighbors)]

    # Sort contexts based on the scores in descending order
    sorted_data = sorted(combined_data, key=lambda x: x[0], reverse=True)

    # Return the top-k ranked contexts
    return [context for score, context in sorted_data][:k]


def get_context_and_source(user_query: str, sentence_transformer: SentenceTransformer,
                           feature_view, reranker) -> Tuple[str, str]:
    """
    Retrieve context and source based on user query using a combination of embedding, feature view, and reranking.

    Parameters:
    - user_query (str): The user's input query string.
    - sentence_transformer (SentenceTransformer): The sentence transformer model.
    - feature_view (FeatureView): The feature view for retrieving neighbors.
    - reranker (Reranker): The reranking model.

    Returns:
    - Tuple[str, str]: A tuple containing the retrieved context and source.
    """
    # Retrieve closest neighbors
    neighbors = get_neighbors(
        user_query,
        sentence_transformer,
        feature_view,
        k=10,
    )

    # Rerank the neighbors to get top-k
    context_reranked = rerank(
        user_query,
        neighbors,
        reranker,
        k=3,
    )

    # Retrieve context
    context = get_context(context_reranked)

    # Retrieve source
    source = get_source(context_reranked)

    return context, source
