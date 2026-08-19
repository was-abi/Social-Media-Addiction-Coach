import json
import csv
from datetime import datetime
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RAGMetrics:
    def __init__(self, log_file="rag_metrics.jsonl"):
        self.log_file = log_file
        self.csv_file = "rag_metrics.csv"
        self._init_csv()

    def _init_csv(self):
        """Create CSV with headers if not exists"""
        if not Path(self.csv_file).exists():
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'user_id', 'turn_num',
                    'user_query', 'retrieved_chunks', 'relevance_scores',
                    'context_used', 'ai_response', 'response_length',
                    'query_embedding_norm', 'chunk_distances'
                ])
                writer.writeheader()

    def log_retrieval(self, user_query, query_embedding, retrieved_chunks,
                     retrieved_embeddings, distances, user_id, turn_num):
        """Log retrieval step with similarity metrics"""

        relevance_scores = [1 - d for d in distances]  # Convert distance to similarity
        context = "\n\n".join(retrieved_chunks)

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'turn_num': turn_num,
            'user_query': user_query,
            'retrieved_chunks': retrieved_chunks,
            'relevance_scores': relevance_scores,
            'context_used': context,
            'query_embedding_norm': float(np.linalg.norm(query_embedding)),
            'chunk_distances': [float(d) for d in distances]
        }

        # Write to JSONL
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        return relevance_scores

    def log_response(self, user_id, turn_num, ai_response):
        """Log LLM response metrics"""
        metrics = {
            'response_length': len(ai_response),
            'word_count': len(ai_response.split()),
            'char_count': len(ai_response)
        }

        # Append to existing JSONL entry (rough tracking)
        with open(self.log_file, 'a') as f:
            f.write(json.dumps({
                'type': 'response',
                'user_id': user_id,
                'turn_num': turn_num,
                'ai_response': ai_response,
                **metrics,
                'timestamp': datetime.now().isoformat()
            }) + '\n')

    def compute_retrieval_precision(self, n=3):
        """Compute avg precision@n from logs"""
        scores = []
        with open(self.log_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                if 'relevance_scores' in entry:
                    # Precision = avg of top-n relevance scores
                    top_n_scores = entry['relevance_scores'][:n]
                    scores.append(np.mean(top_n_scores))

        if scores:
            return np.mean(scores), np.std(scores)
        return 0, 0

    def summary(self):
        """Print summary stats"""
        precision, std = self.compute_retrieval_precision()

        print(f"\n=== RAG Metrics Summary ===")
        print(f"Retrieval Precision@3: {precision:.3f} (±{std:.3f})")
        print(f"Logs written to: {self.log_file}")
        print(f"CSV written to: {self.csv_file}")
