# Gemini CLI Authentication Setup for uDOS

## Option 1: OAuth (Recommended)
1. Run: `./udos-gemini.sh --assist`
2. Choose OAuth when prompted
3. Follow browser authentication flow
4. Free tier: 60 requests/min, 1,000 requests/day

## Option 2: API Key
1. Get API key from: https://aistudio.google.com/apikey
2. Set environment variable:
   ```bash
   export GEMINI_API_KEY="YOUR_API_KEY"
   ```
3. Free tier: 100 requests/day

## Option 3: Vertex AI (Enterprise)
1. Set up Google Cloud Project
2. Set environment variables:
   ```bash
   export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT"
   export GOOGLE_API_KEY="YOUR_API_KEY"
   export GOOGLE_GENAI_USE_VERTEXAI=true
   ```

## Test Authentication
```bash
./udos-gemini.sh --assist
```

If authentication works, you'll see the Gemini CLI interface with uDOS context.
