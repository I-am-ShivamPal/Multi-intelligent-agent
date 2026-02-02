#!/bin/bash
# Render startup script - ensures fast initialization

# Create required directories
mkdir -p logs insightflow dataset

# Create minimal telemetry file
echo "[]" > insightflow/telemetry.json

# Start Streamlit with optimized settings
exec streamlit run web/web_app.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.runOnSave=false \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false
