# Build Checklist

## Pre-Build Steps

1. **Install Dependencies**:
   ```bash
   cd Extension
   npm install
   ```

2. **Create .env File**:
   Create `Extension/.env`:
   ```
   VITE_BACKEND=http://localhost:8000
   ```

3. **Verify Backend is Running**:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```

## Build Steps

1. **Build Extension**:
   ```bash
   cd Extension
   npm run build
   ```

2. **Verify Build Output**:
   Check that `Extension/dist/` contains:
   - `manifest.json`
   - `content.js`
   - `background.js`
   - `chunks/` folder (with React chunks)
   - `assets/` folder (if any)

3. **Load in Chrome**:
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select `Extension/dist` folder

## Common Build Issues

### Issue: "Cannot find module"
**Fix**: Run `npm install` again

### Issue: "VITE_BACKEND is undefined"
**Fix**: 
- Create `.env` file in `Extension/` directory
- Restart dev server or rebuild

### Issue: "Manifest not found in dist/"
**Fix**: 
- Check `vite.config.ts` has copy-manifest plugin
- Verify `src/manifest.json` exists
- Rebuild: `npm run build`

### Issue: TypeScript errors
**Fix**: 
- Check `tsconfig.json` is correct
- Verify all imports are correct
- Check `vite-env.d.ts` exists

## Post-Build Verification

1. **Check Extension Loads**:
   - Go to `chrome://extensions/`
   - Verify extension shows no errors
   - Check "Errors" section if present

2. **Test on Polymarket**:
   - Navigate to `https://polymarket.com/event/...`
   - Open browser console (F12)
   - Check for content script errors
   - Hover over a market card
   - Verify overlay appears

3. **Test Backend Connection**:
   - Open overlay
   - Check browser console for API calls
   - Verify no CORS errors
   - Check Network tab for `/v1/recommendations` request

## Debug Commands

```bash
# Check if build succeeded
cd Extension
npm run build

# Check dist contents
ls -la dist/

# Check for TypeScript errors
npx tsc --noEmit

# Check for linting errors
# (if you have ESLint configured)
```
