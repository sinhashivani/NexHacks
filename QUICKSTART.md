# Quick Start Guide

## Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- MongoDB (local or remote)
- Gemini API key (optional but recommended)

## Backend Setup (5 minutes)

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file**:
   ```bash
   # Copy example
   cp .env.example .env
   
   # Edit .env and set:
   # MONGODB_URI=mongodb://localhost:27017
   # GEMINI_API_KEY=your_key_here
   ```

4. **Start MongoDB** (if not running):
   ```bash
   # Option 1: Docker
   docker run -d -p 27017:27017 mongo:latest
   
   # Option 2: Use existing MongoDB instance
   ```

5. **Start backend server**:
   ```bash
   python run.py
   # Server runs on http://localhost:8000
   ```

## Extension Setup (5 minutes)

1. **Navigate to Extension directory**:
   ```bash
   cd Extension
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Build extension**:
   ```bash
   npm run build
   ```

4. **Load in Chrome**:
   - Open Chrome → `chrome://extensions/`
   - Enable "Developer mode" (top right)
   - Click "Load unpacked"
   - Select `Extension/dist` folder

5. **Configure backend URL** (if backend not on localhost:8000):
   - Create `Extension/.env`:
     ```
     VITE_BACKEND_URL=http://your-backend-url:8000
     ```
   - Rebuild: `npm run build`

## Testing

1. **Open Polymarket**:
   - Navigate to any market page: `https://polymarket.com/event/...`

2. **Trigger overlay**:
   - Click Buy or Sell button → Overlay should open automatically
   - Or click the floating "Open Trade Assistant" button

3. **Verify features**:
   - Primary trade card shows market info
   - Amplify tab shows 5 recommendations
   - Hedge tab shows 5 recommendations
   - Add legs to basket
   - Open next unvisited leg

## Troubleshooting

### Extension not loading
- Check `dist/manifest.json` exists
- Check Chrome extension console for errors
- Verify all files built: `ls Extension/dist/`

### Backend connection errors
- Verify backend is running: `curl http://localhost:8000/health`
- Check CORS settings in `backend/config.py`
- Check browser console for CORS errors

### No recommendations
- Check backend logs for errors
- Verify Gemini API key is set (optional)
- Check MongoDB connection
- Verify Gamma/CLOB APIs are accessible

## Development Mode

### Backend (auto-reload):
```bash
cd backend
uvicorn main:app --reload
```

### Extension (watch mode):
```bash
cd Extension
npm run dev
# Then reload extension in Chrome after changes
```

## Next Steps

- Customize recommendation logic in `backend/services/recommendation_engine.py`
- Adjust UI styling in `Extension/src/content/shadowStyles.ts`
- Add more trade detection heuristics in `Extension/src/utils/tradeDetection.ts`
