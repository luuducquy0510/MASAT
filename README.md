# MASAT

# Setup and Deployment

## Prerequisites

Before running the application locally, ensure you have the following installed:

1. **python 3.12**: Python 3.12 or above is required to run a2a-sdk
2. **set up .env**

Create a `.env` file in the root of the `MASAT` directory with your Google API Key:

```bash
GOOGLE_API_KEY="your_api_key_here"
```

---

## Run the Agents

### Terminal 1: Run activities_agent

```bash
cd activities_agent
source .venv/bin/activate
python __main__.py
```

### Terminal 2: Run stays_agent

```bash
cd stays_agent
source .venv/bin/activate
python __main__.py
```

### Terminal 3: Run flights_agent

```bash
cd flights_agent
source .venv/bin/activate
python __main__.py
```

### Terminal 4: Run Host Agent

```bash
cd host_agent
source .venv/bin/activate
adk web
```

### Demo question: 
I’m planning a 7-day trip from Hanoi, VietNam to Tokyo. Can you help me find a flight, a hotel, and suggest some fun activities in under $5000 total while I’m there? Then make a full schedule as detail as possible for me with cost next to each section.