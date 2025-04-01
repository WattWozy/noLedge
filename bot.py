import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import numpy as np
import os
from typing import List, Dict, Tuple

class LocalLLMWithRAG:
    def __init__(
        self, 
        model_name: str = "microsoft/DialoGPT-small", 
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = None
    ):
        """
        Initialize a local LLM with RAG capabilities.
        
        Args:
            model_name: Name of the HuggingFace model to use for text generation
            embedding_model_name: Name of the model to use for embeddings
            device: Device to run the model on ('cuda', 'cpu', etc.)
        """
        # Determine device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"Using device: {self.device}")
        
        # Load generation model and tokenizer
        print(f"Loading model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        ).to(self.device).eval()
        
        # Load embedding model for RAG
        print(f"Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name, device=self.device)
        
        # Storage for document embeddings
        self.document_store = []
        self.document_embeddings = []
        
        # Chat history for DialoGPT
        self.chat_history_ids = None
        
    def add_documents(self, documents: List[str], chunk_size: int = 512):
        """
        Add documents to the RAG system.
        
        Args:
            documents: List of document texts
            chunk_size: Size of chunks to split documents into
        """
        # Simple chunking strategy
        chunks = []
        for doc in documents:
            # Split into chunks of roughly chunk_size characters
            doc_chunks = [doc[i:i + chunk_size] for i in range(0, len(doc), chunk_size)]
            chunks.extend(doc_chunks)
        
        # Create embeddings for each chunk
        embeddings = self.embedding_model.encode(chunks)
        
        # Store chunks and their embeddings
        self.document_store.extend(chunks)
        if not self.document_embeddings:
            self.document_embeddings = embeddings
        else:
            self.document_embeddings = np.vstack([self.document_embeddings, embeddings])
        
        print(f"Added {len(chunks)} document chunks to the RAG system")
        
    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Retrieve relevant document chunks for a query.
        
        Args:
            query: Query text
            top_k: Number of top chunks to retrieve
            
        Returns:
            List of (chunk, similarity_score) tuples
        """
        if not self.document_store:
            return []
        
        # Get query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Calculate cosine similarity
        similarities = np.dot(self.document_embeddings, query_embedding) / (
            np.linalg.norm(self.document_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return top-k chunks with scores
        return [(self.document_store[i], similarities[i]) for i in top_indices]
    
    def generate_response(self, query: str, temperature: float = 0.7, max_new_tokens: int = 100) -> str:
        """
        Generate a response using DialoGPT.
        
        Args:
            query: User input text
            temperature: Sampling temperature
            max_new_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated response
        """
        # Encode the input and add to the tokenizer
        new_user_input_ids = self.tokenizer.encode(query + self.tokenizer.eos_token, return_tensors='pt').to(self.device)
        
        # Append to chat history if it exists
        bot_input_ids = new_user_input_ids
        if self.chat_history_ids is not None:
            bot_input_ids = torch.cat([self.chat_history_ids, new_user_input_ids], dim=-1)
        
        # Generate a response
        with torch.no_grad():
            chat_history_ids = self.model.generate(
                bot_input_ids,
                max_new_tokens=max_new_tokens,
                pad_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3,
                do_sample=True,
                temperature=temperature,
                top_k=50,
                top_p=0.9
            )
        
        # Extract the response (without the input part)
        response_ids = chat_history_ids[:, bot_input_ids.shape[-1]:]
        response = self.tokenizer.decode(response_ids[0], skip_special_tokens=True)
        
        # Update chat history
        self.chat_history_ids = chat_history_ids
        
        return response
    
    def generate_with_rag(self, query: str, top_k: int = 3, temperature: float = 0.7, max_new_tokens: int = 100) -> str:
        """
        Generate text with Retrieval-Augmented Generation.
        
        Args:
            query: User query
            top_k: Number of document chunks to retrieve
            temperature: Sampling temperature
            max_new_tokens: Maximum number of tokens to generate
            
        Returns:
            Generated text
        """
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(query, top_k=top_k)
        
        if not retrieved_docs:
            return self.generate_response(query, temperature, max_new_tokens)
        
        # Format query with retrieved content
        context = "\n\n".join([doc for doc, _ in retrieved_docs])
        
        enhanced_query = f"Context: {context}\n\nQuestion: {query}"
        
        return self.generate_response(enhanced_query, temperature, max_new_tokens)
    
    def clear_history(self):
        """Clear the chat history"""
        self.chat_history_ids = None
        print("Chat history cleared")


def interactive_chat():
    """Run an interactive chat session with the RAG system"""
    # Initialize the model
    print("Initializing the model (this might take a while)...")
    llm = LocalLLMWithRAG(
        model_name="microsoft/DialoGPT-small",  # Smaller conversation-focused model
        embedding_model_name="sentence-transformers/all-MiniLM-L6-v2"  # Small embedding model
    )
    
    # Add some documents
    print("\nWould you like to add documents to the knowledge base? (y/n)")
    add_docs = input("> ").lower().strip()
    
    if add_docs == 'y':
        print("\nEnter document file paths (one per line, empty line to finish):")
        file_paths = []
        while True:
            path = input("File path: ").strip()
            if not path:
                break
            if os.path.exists(path):
                file_paths.append(path)
            else:
                print(f"File not found: {path}")
        
        documents = []
        for path in file_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    documents.append(f.read())
                print(f"Loaded: {path}")
            except Exception as e:
                print(f"Error loading {path}: {e}")
        
        if documents:
            llm.add_documents(documents)
            print(f"Added {len(documents)} documents to the knowledge base")
    
    # Chat loop
    print("\n========================================")
    print("Welcome to the Interactive LLM with RAG")
    print("Type 'exit' to quit, 'clear' to clear history")
    print("========================================\n")
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Check for exit command
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break
            
        # Check for clear history command
        if user_input.lower() == 'clear':
            llm.clear_history()
            continue
            
        # Process query and get response
        print("Thinking...")
        try:
            response = llm.generate_with_rag(
                user_input, 
                top_k=3, 
                temperature=0.7,
                max_new_tokens=100
            )
            print(f"\nAssistant: {response}\n")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    interactive_chat()