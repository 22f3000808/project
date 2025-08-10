# 🖥️ SysUtil Admin Dashboard

A simple system monitoring dashboard that:
- Receives reports from clients (via API)
- Displays all reporting machines
- Flags configuration issues (e.g., unencrypted disk, outdated OS, no antivirus)
- Shows last check-in time
- Allows filtering by OS and issue type
- Supports CSV export of machine data


## Need to know

### First create the virtual environment and run pip install requirements.txt

Everything in this project is created and tested localy using commands as follows in the terminal in respective directory
- To run backend
      - uvicorn main:app --reload --port 8000
- To run client
      - python main.py --background --interval 5
- To run daemon file
        - python3 daemon.py
- To run frontend
      - npm run dev 

