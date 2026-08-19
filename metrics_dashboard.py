import json
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from metrics import RAGMetrics

st.set_page_config(page_title="RAG Metrics Dashboard", layout="wide")

st.title("🔍 RAG Evaluation Dashboard")
st.caption("Monitor retrieval quality and response metrics")

log_file = "rag_metrics.jsonl"

if not Path(log_file).exists():
    st.warning("No metrics logged yet. Start chatting in the app first!")
    st.stop()

# Parse logs
retrieval_logs = []
response_logs = []

try:
    with open(log_file, 'r') as f:
        for line in f:
            if line.strip():
                entry = json.loads(line)
                if 'retrieved_chunks' in entry:
                    retrieval_logs.append(entry)
                elif 'ai_response' in entry:
                    response_logs.append(entry)
except Exception as e:
    st.error(f"Error reading logs: {e}")
    st.stop()

if not retrieval_logs:
    st.warning("No retrieval logs found yet.")
    st.stop()

# ============================================================================
# METRICS SUMMARY
# ============================================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Queries", len(retrieval_logs))

with col2:
    # Compute average relevance across all queries
    all_relevances = []
    for log in retrieval_logs:
        if log.get('relevance_scores'):
            all_relevances.extend(log['relevance_scores'])
    
    avg_relevance = np.mean(all_relevances) if all_relevances else 0.0
    st.metric("Avg Relevance Score", f"{avg_relevance:.3f}", 
              help="Cosine similarity (0.0-1.0, higher is better)")

with col3:
    # Average chunks retrieved per query
    avg_chunks = np.mean([len(log['retrieved_chunks']) for log in retrieval_logs])
    st.metric("Avg Chunks Retrieved", f"{avg_chunks:.1f}")

with col4:
    if response_logs:
        avg_response_length = np.mean([
            log.get('response_length', 0) for log in response_logs
        ])
        st.metric("Avg Response Length", f"{avg_response_length:.0f} chars")
    else:
        st.metric("Avg Response Length", "N/A")

# ============================================================================
# RELEVANCE TRENDS
# ============================================================================

st.subheader("Relevance Scores Over Time")

# Extract relevance per query
relevance_by_query = []
for i, log in enumerate(retrieval_logs):
    avg_rel = np.mean(log['relevance_scores']) if log['relevance_scores'] else 0.0
    relevance_by_query.append({
        'Query #': i + 1,
        'Avg Relevance': avg_rel,
        'Timestamp': log.get('timestamp', '')
    })

if relevance_by_query:
    rel_df = pd.DataFrame(relevance_by_query)
    st.line_chart(rel_df.set_index('Query #')['Avg Relevance'])
    st.dataframe(rel_df, use_container_width=True)
else:
    st.info("No relevance data available.")

# ============================================================================
# DETAILED RETRIEVAL BREAKDOWN
# ============================================================================

st.subheader("Detailed Retrieval Analysis")

for i, log in enumerate(retrieval_logs):
    query_text = log['user_query'][:70]
    
    with st.expander(f"Query {i+1}: {query_text}...", expanded=False):
        # Query info
        st.write(f"**User Query:** {log['user_query']}")
        st.write(f"**Timestamp:** {log.get('timestamp', 'N/A')}")
        st.write(f"**User ID:** {log.get('user_id', 'N/A')}")
        st.write(f"**Turn #:** {log.get('turn_num', 'N/A')}")
        
        st.divider()
        
        # Retrieved chunks with scores
        st.write("**Retrieved Chunks (ranked by relevance):**")
        
        chunks = log.get('retrieved_chunks', [])
        distances = log.get('distances', [])
        relevance_scores = log.get('relevance_scores', [])
        
        for j in range(len(chunks)):
            chunk = chunks[j] if j < len(chunks) else ""
            dist = distances[j] if j < len(distances) else "N/A"
            rel = relevance_scores[j] if j < len(relevance_scores) else "N/A"
            
            # Color-code relevance
            if isinstance(rel, (int, float)):
                if rel > 0.7:
                    color = "🟢"
                elif rel > 0.4:
                    color = "🟡"
                else:
                    color = "🔴"
                rel_text = f"{color} {rel:.3f}"
            else:
                rel_text = "N/A"
            
            st.write(f"**Rank {j+1}** — Relevance: {rel_text} | Distance: {dist}")
            st.text(chunk[:250] + "..." if len(chunk) > 250 else chunk)
            st.divider()

# ============================================================================
# RESPONSE METRICS
# ============================================================================

if response_logs:
    st.subheader("Response Quality Metrics")
    
    response_df = pd.DataFrame([
        {
            'Turn #': log.get('turn_num', i),
            'Response Length': log.get('response_length', 0),
            'Timestamp': log.get('timestamp', '')
        }
        for i, log in enumerate(response_logs)
    ])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Response Length Over Time**")
        st.line_chart(response_df.set_index('Turn #')['Response Length'])
    
    with col2:
        st.metric(
            "Total Responses",
            len(response_logs),
            delta=None
        )
    
    st.write("**Response Log Table**")
    st.dataframe(response_df, use_container_width=True)
else:
    st.info("No responses logged yet.")

# ============================================================================
# DOWNLOAD LOGS
# ============================================================================

st.divider()
st.subheader("Download Raw Metrics")

log_text = ""
try:
    with open(log_file, 'r') as f:
        log_text = f.read()
except Exception as e:
    st.error(f"Error reading log file: {e}")

if log_text:
    st.download_button(
        label="📥 Download Metrics (JSONL)",
        data=log_text,
        file_name="rag_metrics.jsonl",
        mime="application/jsonl"
    )

# ============================================================================
# RAG METRICS SUMMARY
# ============================================================================

st.divider()
st.subheader("RAG Performance Summary")

with st.spinner("Computing summary..."):
    metrics_logger = RAGMetrics(log_file)
    metrics_logger.summary()

st.success("Dashboard loaded successfully!")