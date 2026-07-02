# Deployment Diagram

```mermaid
graph TB
    subgraph Client["Client Machine / Browser"]
        Browser[Web Browser]
    end

    subgraph DevServer["Local / College Lab Server"]
        subgraph Node["Node.js Runtime"]
            ViteServer[Vite Dev Server :5173 - React Frontend]
        end

        subgraph PyEnv["Python Virtual Environment"]
            Uvicorn[Uvicorn ASGI Server :8000]
            FastAPIApp[FastAPI Application]
            MLModels[Trained Models: rf_model.pkl, lstm_model.h5, slm checkpoint]
        end

        subgraph DBServer["MySQL Server :3306"]
            MySQLDB[(smart_traffic_db)]
        end

        ReportsDisk[/reports_output/ - Generated PDFs/]
    end

    subgraph External["External (Optional)"]
        OpenAI[OpenAI API - GenAI scenarios]
    end

    Browser -->|HTTP :5173| ViteServer
    ViteServer -->|REST API calls, proxied or direct :8000| Uvicorn
    Uvicorn --> FastAPIApp
    FastAPIApp --> MLModels
    FastAPIApp -->|SQL over TCP :3306| MySQLDB
    FastAPIApp --> ReportsDisk
    FastAPIApp -.->|optional, if API key set| OpenAI
```

**Explanation:** For a college demo, everything typically runs on a single machine: the Vite dev
server serves the React app, Uvicorn serves the FastAPI backend, and MySQL runs locally. The only
external dependency is the OpenAI API, which is entirely optional — without an API key, the
GenAI module falls back to its offline procedural generator, so the whole system can run with
zero internet access (useful for a viva in a room without reliable Wi-Fi).

For a more production-like deployment, each box (frontend build served via Nginx, backend
container, MySQL container) could be containerized separately and orchestrated with Docker
Compose — left as a documented future-scope item rather than implemented, to keep the submission
focused.
