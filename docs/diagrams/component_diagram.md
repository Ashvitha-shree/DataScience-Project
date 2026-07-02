# Component Diagram

```mermaid
graph LR
    subgraph Frontend["React Frontend"]
        FE_Auth[Auth Context]
        FE_Pages[Pages: Dashboard, Roads, Traffic, Incidents, Alerts, Agent, Reports]
        FE_API[API Client - axios]
    end

    subgraph Backend["FastAPI Backend"]
        API_Routes[API Routes Layer]
        Auth_Layer[Auth - JWT + Password Hashing]
        ML[ml_module - Random Forest]
        DL[dl_module - LSTM]
        NLP[nlp_module - spaCy]
        SLM[slm_module - FLAN-T5 Small]
        GenAI[genai_module - Scenario Generator]
        AgentMod[agent_module - Rule-based Agent]
        DataLayer[database - SQLAlchemy ORM]
    end

    subgraph Storage["Storage"]
        MySQL[(MySQL Database)]
        ModelFiles[/Saved Model Files - .pkl / .h5/]
        ReportFiles[/Generated PDF Reports/]
    end

    FE_Pages --> FE_API
    FE_API -->|REST/JSON over HTTPS| API_Routes
    API_Routes --> Auth_Layer
    API_Routes --> ML
    API_Routes --> DL
    API_Routes --> NLP
    API_Routes --> SLM
    API_Routes --> GenAI
    API_Routes --> AgentMod
    API_Routes --> DataLayer
    AgentMod --> SLM
    ML --> ModelFiles
    DL --> ModelFiles
    DataLayer --> MySQL
    API_Routes --> ReportFiles
```

**Explanation:** The frontend only ever talks to the API Routes layer. Within the backend, each
AI module is a separate component with a narrow responsibility; the Agent module is the only one
that calls another AI module directly (SLM, for alert text). All persistent state lives in
MySQL, with trained model binaries and generated PDF reports stored as files on disk.
