# Troubleshooting Guide

## Common Build Errors

### 1. Environment Variable Not Found
**Error**: `VITE_BACKEND is undefined`

**Solution**: 
- Make sure `.env` file exists in `Extension/` directory
- File should contain: `VITE_BACKEND=http://localhost:8000`
- Restart the dev server after creating/modifying `.env`
- For production builds, Vite will use the env variable if set

### 2. Module Not Found / Import Errors
**Error**: `Cannot find module '...'` or `Failed to resolve import`

**Solution**:
```bash
cd Extension
npm install
```

### 3. TypeScript Errors
**Error**: Type errors in TypeScript files

**Solution**:
- Check `tsconfig.json` is correct
- Run `npm run build` to see full error messages
- Make sure all dependencies are installed

### 4. Build Output Issues
**Error**: `manifest.json` not found in dist/ or files missing

**Solution**:
- The build process should copy `src/manifest.json` to `dist/manifest.json`
- Check that `vite.config.ts` has the copy-manifest plugin
- Verify `dist/` folder exists after build

### 5. Chrome Extension Load Errors
**Error**: "Manifest file is missing or unreadable" or "Service worker registration failed"

**Solution**:
- Make sure you're loading the `dist/` folder, not `src/`
- Check that `dist/manifest.json` exists
- Verify `dist/content.js` and `dist/background.js` exist
- Reload the extension in Chrome after rebuilding

## Runtime Errors

### 1. Backend Connection Failed
**Error**: `API error: Failed to fetch` or CORS errors

**Solution**:
- Verify backend is running: `curl http://localhost:8000/health`
- Check `.env` file has correct `VITE_BACKEND` URL
- Check browser console for CORS errors
- Verify backend CORS settings allow extension origin

### 2. Overlay Not Appearing
**Error**: Overlay doesn't show on hover or trade module open

**Solution**:
- Check browser console for JavaScript errors
- Verify content script is loaded (check Chrome DevTools → Sources → Content scripts)
- Check that Shadow DOM is being created
- Verify interaction detection is working (check console logs)

### 3. Hover Detection Not Working
**Error**: Hovering market cards doesn't trigger overlay

**Solution**:
- Check browser console for errors
- Verify market cards match the selectors in `interactionDetection.ts`
- Polymarket may have changed their HTML structure - update selectors if needed
- Check that `pointerenter` events are firing (add console.log to debug)

### 4. Pin Toggle Not Working
**Error**: Pin button doesn't prevent hover updates

**Solution**:
- Check React DevTools to see if `isPinned` state is updating
- Verify the `useEffect` dependency array includes `isPinned`
- Check browser console for React errors

## Build Commands

### Development
```bash
cd Extension
npm run dev
# Then reload extension in Chrome after changes
```

### Production Build
```bash
cd Extension
npm run build
# Load dist/ folder in Chrome
```

## Debugging Steps

1. **Check Build Output**:
   ```bash
   cd Extension
   npm run build
   ls dist/
   # Should see: content.js, background.js, manifest.json, chunks/, assets/
   ```

2. **Check Browser Console**:
   - Open Chrome DevTools (F12)
   - Go to Console tab
   - Look for errors from content script
   - Check for CORS or network errors

3. **Check Extension Console**:
   - Go to `chrome://extensions/`
   - Click "Inspect views: service worker" for background script errors
   - Check "Errors" section for manifest issues

4. **Verify Content Script Injection**:
   - Open Polymarket.com
   - Open DevTools → Sources
   - Look for "Content scripts" section
   - Should see `content.js` listed

5. **Test Backend Connection**:
   ```bash
   # In terminal
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```

## Common Issues

### Issue: "Cannot use import statement outside a module"
**Fix**: Make sure `manifest.json` has `"type": "module"` in background service_worker

### Issue: "React is not defined"
**Fix**: Make sure React is imported in all component files

### Issue: "Shadow DOM styles not applying"
**Fix**: Styles must be injected as textContent, not via CSS imports

### Issue: "Rate limiting too aggressive"
**Fix**: Adjust `RATE_LIMIT_MS` in `interactionDetection.ts` (currently 1000ms)

### Issue: "Hover detection triggers too often"
**Fix**: Adjust `HOVER_DEBOUNCE_MS` in `interactionDetection.ts` (currently 250ms)

## Getting Help

If you encounter errors:

1. Check the browser console for full error messages
2. Check the extension service worker console
3. Verify all files are built correctly
4. Check that backend is running and accessible
5. Review the error message and search for similar issues

## Environment Setup Checklist

- [ ] Node.js 18+ installed
- [ ] `npm install` run in Extension/
- [ ] `.env` file created with `VITE_BACKEND=http://localhost:8000`
- [ ] Backend running on port 8000
- [ ] MongoDB running (if using local)
- [ ] Extension built with `npm run build`
- [ ] Extension loaded in Chrome from `dist/` folder
