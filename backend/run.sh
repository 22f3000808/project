#!/usr/bin/env bash
# usage: ./run.sh
# export API_KEY="${API_KEY:-secret-key}"
# Use DATABASE_URL=sqlite:///./data.db or set to your DB
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
