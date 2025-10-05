# AI Travel Planner - Setup Instructions

## Quick Setup for Team Members

### 1. Prerequisites Installation

**Install Python 3.9+ and Git:**
```bash
# macOS (using Homebrew)
brew install python@3.11 git

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv git

# Windows (use official installers)
# Download from python.org and git-scm.com
```

**Install Redis (for caching):**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis

# Windows
# Download from redis.io/download
```

### 2. Project Setup

**Clone and setup:**
```bash
# Clone the repository
git clone https://github.com/12-crypto/AI-Itenary.git
cd AI-Itenary

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Get Free API Keys

**OpenWeatherMap (Weather Data):**
1. Visit: https://openweathermap.org/api
2. Sign up for free account
3. Get API key (1000 calls/day free)
4. Add to `.env`: `OPENWEATHER_API_KEY=your_key_here`

**Aviationstack (Flight Data):**
1. Visit: https://aviationstack.com/
2. Sign up for free plan (1000 requests/month)
3. Get API key
4. Add to `.env`: `AVIATIONSTACK_API_KEY=your_key_here`

**Fixer.io (Currency Exchange):**
1. Visit: https://fixer.io/
2. Sign up for free plan (100 requests/month)
3. Get API key
4. Add to `.env`: `FIXER_API_KEY=your_key_here`

**Ollama (Free Local LLM):**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (this may take a few minutes)
ollama pull llama2

# Start Ollama server (keep this running)
ollama serve
```

### 4. Initialize Database

```bash
# Initialize database and create sample data
python scripts/init_db.py
```

### 5. Start Development Server

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Verify Setup

Visit http://localhost:8000 in your browser. You should see:
```json
{
  "message": "AI Travel Planner API",
  "version": "1.0.0",
  "docs": "/api/docs",
  "status": "healthy"
}
```

**Check API documentation:**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 7. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_health.py -v
```

## Docker Setup (Alternative)

If you prefer Docker:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

## Development Workflow

### Daily Development
```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Redis (if not running)
redis-server  # or brew services start redis

# Start Ollama (if using local LLM)
ollama serve

# Start development server
uvicorn app.main:app --reload
```

### Working with Git
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python -m pytest tests/

# Format code
black .
flake8 .

# Commit changes
git add .
git commit -m "feat: description of your changes"

# Push to remote
git push origin feature/your-feature-name

# Create pull request on GitHub
```

### Code Quality Checks
```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .

# Run all quality checks
black . && flake8 . && mypy . && pytest
```

## Troubleshooting

### Common Issues

**1. Import errors when running the app:**
- Make sure virtual environment is activated
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**2. Database errors:**
- Run database initialization: `python scripts/init_db.py`
- Check if SQLite file permissions are correct

**3. Redis connection errors:**
- Make sure Redis is running: `redis-cli ping` should return `PONG`
- Check Redis URL in `.env` file

**4. API key issues:**
- Verify API keys are correctly set in `.env` file
- Check API usage limits (some free tiers have daily limits)

**5. Ollama not working:**
- Make sure Ollama is installed: `ollama --version`
- Check if model is downloaded: `ollama list`
- Verify Ollama server is running: `curl http://localhost:11434`

### Getting Help

1. **Check logs:** The application uses structured logging
2. **GitHub Issues:** Create an issue for bugs or questions
3. **Team Chat:** Use your team's Slack/Discord channel
4. **Documentation:** Check `/docs` folder for detailed guides

### Performance Tips

1. **Use Docker for consistency** across team members
2. **Enable Redis caching** for better API performance
3. **Use pytest-xdist** for parallel test execution: `pip install pytest-xdist` then `pytest -n auto`
4. **Monitor API usage** to stay within free tier limits

## Next Steps

1. **For New Contributors:**
   - Complete this setup
   - Read the main README.md
   - Pick an issue from GitHub Issues
   - Join team communication channels

2. **For Project Leads:**
   - Set up CI/CD pipeline
   - Configure monitoring and logging
   - Create team communication channels
   - Assign issues to team members

---

**Need help?** Create an issue on GitHub or reach out to the team!

Happy coding! 🚀✈️🏨