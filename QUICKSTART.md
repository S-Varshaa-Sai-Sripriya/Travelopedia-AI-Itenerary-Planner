# 🚀 AI Travel Planner - Quick Start Guide

## 📋 What You Need

### Required (Free)
- Python 3.9+ 
- Git
- Redis (brew install redis)

### API Keys (All Completely Free)
1. **OpenWeatherMap**: 1000 calls/day free → https://openweathermap.org/api
2. **Aviationstack**: 1000 requests/month free → https://aviationstack.com/
3. **Fixer.io**: 100 requests/month free → https://fixer.io/

### No API Keys Required (Open Source)
- **OpenStreetMap**: Maps and geocoding (completely free)
- **Nominatim**: Address search (completely free)
- **Overpass API**: POI and attractions data (completely free)

### Optional
- **Ollama**: Completely free local LLM → https://ollama.ai/

## ⚡ 5-Minute Setup

```bash
# 1. Clone and setup
git clone https://github.com/12-crypto/AI-Itenary.git
cd AI-Itenary
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Environment setup
cp .env.example .env
# Edit .env with your API keys

# 4. Initialize database
python scripts/init_db.py

# 5. Start Redis
redis-server  # or brew services start redis

# 6. Start the app
uvicorn app.main:app --reload
```

**✅ Success!** Visit http://localhost:8000

## 🎯 Quick Test

```bash
# Test the API
curl http://localhost:8000/api/v1/health

# View API docs
open http://localhost:8000/api/docs
```

## 🏗️ Project Structure

```
AI-Itenary/
├── app/                    # Main application
│   ├── agents/            # AI agents (LLM, GNN, Budget, Itinerary)
│   ├── api/               # FastAPI routes
│   ├── core/              # Config, database, logging
│   ├── models/            # Database models
│   └── services/          # External APIs
├── notebooks/             # Jupyter research notebooks
├── tests/                 # Test files
├── scripts/               # Utility scripts
└── docker-compose.yml     # Docker setup
```

## 🔧 Development Commands

```bash
# Run tests
pytest

# Format code
black .

# Start with Docker
docker-compose up -d

# View logs
docker-compose logs -f app
```

## 🚨 Need Help?

1. **Check SETUP.md** for detailed instructions
2. **Create GitHub Issue** for bugs
3. **Check logs** for error details
4. **Ask team** in Slack/Discord

## 📚 Key Resources

- **API Docs**: http://localhost:8000/api/docs
- **Detailed Setup**: [SETUP.md](SETUP.md)
- **Main README**: [README.md](README.md)
- **Free APIs Guide**: See README.md "Free APIs Used" section

## 🎉 What's Working

- ✅ FastAPI backend with health checks
- ✅ Database models and initialization
- ✅ Multi-agent architecture (LLM, GNN, Budget, Itinerary)
- ✅ External API integrations (weather, flights, currency)
- ✅ Docker setup for easy deployment
- ✅ Test framework and CI ready
- ✅ GNN research notebook for personalization

## 🔮 Next Steps (8-Week Timeline)

### Week 1: ✅ Project Setup & Data Engineering
- Base project structure ✅
- API integrations ✅
- Database schema ✅
- Development environment ✅

### Week 2-3: GNN/Multi-modal Development
- [ ] Implement user preference modeling
- [ ] Build GNN recommendation engine
- [ ] Create similarity algorithms
- [ ] Test personalization accuracy

### Week 4: LLM Orchestration
- [ ] Integrate Ollama/OpenAI for intent parsing
- [ ] Implement agent coordination
- [ ] Add constraint validation
- [ ] Handle edge cases and errors

### Week 5-6: Big Data Integration
- [ ] Implement Kafka streaming
- [ ] Add real-time data processing
- [ ] Scale for multiple users
- [ ] Performance optimization

### Week 7: Testing & Optimization
- [ ] End-to-end testing
- [ ] User acceptance testing
- [ ] Performance benchmarking
- [ ] Bug fixes and improvements

### Week 8: Final Report
- [ ] Complete documentation
- [ ] Deployment guide
- [ ] Performance analysis
- [ ] Project submission

---

**🎯 Goal**: Build an intelligent, automated travel itinerary planner that leverages AI agents, real-time data, and personalized recommendations!

**💡 Remember**: All APIs are free, focus on building awesome features!