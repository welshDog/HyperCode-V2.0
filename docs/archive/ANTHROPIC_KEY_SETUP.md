# ⚠️ IMPORTANT: Add Your Anthropic API Key

Your `.env` file has been created with secure, randomly-generated secrets for:
- ✅ API_KEY
- ✅ HYPERCODE_JWT_SECRET  
- ✅ POSTGRES_PASSWORD
- ✅ HYPERCODE_MEMORY_KEY

## 🔑 Action Required

**You need to add your Anthropic API key to make the AI agents work.**

### Steps:

1. Open `.env` file in this directory
2. Find this line:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```
3. Replace `your_anthropic_api_key_here` with your actual Anthropic API key
4. Save the file
5. Restart the services:
   ```bash
   docker-compose restart crew-orchestrator
   docker-compose restart frontend-specialist backend-specialist database-architect qa-engineer devops-engineer security-engineer system-architect project-strategist
   ```

### Get an Anthropic API Key

If you don't have one:
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new key
5. Copy it to your `.env` file

---

**⚠️ NEVER commit the `.env` file to git - it's already in .gitignore**
