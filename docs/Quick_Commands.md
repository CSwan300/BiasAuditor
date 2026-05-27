## Quick Commands

### Docker

- Start containers: `docker compose up -d`
- Stop containers: `docker compose down`

### Frontend


#### Development & Preview

- Start dev server: `npm run dev --prefix frontend`  
  Launches the Vite dev server, usually on `localhost:5173`.
- Preview production build: `npm run preview --prefix frontend`  
  Starts a local server to preview the production build.

#### Testing


- Standard test: `npm run test --prefix frontend`  
  Runs Vitest in watch mode.
- UI test mode: `npm run test:ui --prefix frontend`  
  Opens the browser-based Vitest UI.
- CI / single run: `npm run test:run --prefix frontend`  
  Runs all tests once and exits.

#### Build

- Full build: `npm run build --prefix frontend`  
  Runs the TypeScript compiler first, then builds the production frontend.

### Backend

#### FastAPI Commands

- Start backend: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
- Install dependencies: `pip install -r requirements.txt`
- Run tests: `python -m pytest backend/tests`

#### Useful URLs

- Health check: [http://localhost:8000/health](http://localhost:8000/health)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)