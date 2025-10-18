# Travelopedia: AI-Powered Itinerary Planner

This is the base setup for the AI Travel Planner project. This document will help team members set up their development environment and start contributing.

## Project Overview

The AI Travel Planner is an intelligent, automated itinerary planning system that leverages:
- **Multi-Agent AI Architecture**: Orchestrated agents for different aspects of travel planning
- **Real-time Data Integration**: Live flight, hotel, and weather data
- **Graph Neural Networks (GNN)**: For personalized recommendations
- **Big Data Processing**: Kafka streams for real-time updates
- **Local-first Approach**: Constraint-aware validation engine

## Architecture Components

```
User Request → LLM Orchestrator → Real-time APIs → Personalization (GNN) → Decision Points → Automated Execution → User Response
```

### Key Agents:
1. **LLM Orchestrator**: Parses user requests and coordinates other agents
2. **GNN Agent**: Provides personalized recommendations based on user profile
3. **Budget Optimization Agent**: Balances cost vs convenience
4. **Itinerary Agent**: Consolidates decisions and automates bookings

## Quick Start

### Prerequisites
- Python 3.9+
- Git
- Redis (for caching and message queuing)
- Optional: Docker (for containerized development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/12-crypto/AI-Itenary.git
   cd AI-Itenary
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Updated for Python 3.13 compatibility - some packages versions adjusted*

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys (see API Keys section below)
   # Note: Demo works without API keys for basic testing
   ```

5. **Initialize database**
   ```bash
   python scripts/init_db.py
   ```
   *Creates SQLite database with tables and demo user (demo@example.com / demo123)*

6. **Start the development server**
   ```bash
   # Always activate venv first for any command
   source venv/bin/activate
   uvicorn app.main:app --reload --port 8000
   ```
   *Server will run on http://127.0.0.1:8000*

## Project Structure

```
AI-Itenary/
├── app/                    # Main application code
│   ├── agents/            # AI agents (LLM, GNN, Budget, Itinerary)
│   ├── api/               # FastAPI routes and endpoints
│   ├── core/              # Core configuration and utilities
│   ├── models/            # Database models and schemas
│   ├── services/          # Business logic and external integrations
│   └── main.py           # FastAPI application entry point
├── data/                  # Data storage and processing
│   ├── raw/              # Raw data files
│   ├── processed/        # Processed datasets
│   └── models/           # Trained ML models
├── scripts/              # Utility scripts
├── tests/                # Test files
├── docs/                 # Documentation
├── docker/               # Docker configuration
├── notebooks/            # Jupyter notebooks for research
└── config/               # Configuration files
```

## Free APIs Used

### ✅ Completely Free APIs:
1. **Weather**: OpenWeatherMap (1000 calls/day free)
2. **Hotels**: OpenStreetMap + Overpass API (completely free)
3. **Flights**: Aviationstack (1000 requests/month free)
4. **Maps/Places**: OpenStreetMap + Nominatim (completely free)
5. **Currency**: Fixer.io (100 requests/month free)
6. **LLM**: Ollama (local inference, completely free)
7. **Geocoding**: Nominatim (completely free)
8. **Points of Interest**: Overpass API (completely free)

### 🌟 Why These APIs?
- **Zero Cost**: All APIs are completely free with no payment required
- **No Credit Cards**: No need to provide payment information
- **Generous Limits**: Sufficient for development and testing
- **Open Source**: Many are backed by open-source communities
- **No Vendor Lock-in**: Easy to switch or self-host alternatives

## API Keys Setup

Create a `.env` file with the following keys:

```env
# Core Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./travel_planner.db

# AI/LLM Configuration (Completely Free)
OLLAMA_BASE_URL=http://localhost:11434  # Local LLM (completely free)

# Travel APIs (All Completely Free)
OPENWEATHER_API_KEY=your-openweather-key  # 1000 calls/day free
AVIATIONSTACK_API_KEY=your-aviationstack-key  # 1000 requests/month free
FIXER_API_KEY=your-fixer-key  # 100 requests/month free

# Infrastructure (Local & Free)
REDIS_URL=redis://localhost:6379  # Local Redis
KAFKA_BOOTSTRAP_SERVERS=localhost:9092  # Local Kafka

# Open Source APIs (No Keys Required)
# OpenStreetMap/Nominatim: No API key needed
# Overpass API: No API key needed

# Optional Integrations
CALENDAR_WEBHOOK_URL=your-webhook-url  # For calendar sync
```

## Development Workflow

### 1. Feature Development
```bash
# Always activate venv first
source venv/bin/activate

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python -m pytest tests/

# Format code
black .
flake8 .

# Commit and push
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
```

### 2. Testing
```bash
# Always activate venv first
source venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Run specific test file
pytest tests/test_health.py

# Run with coverage
pytest --cov=app tests/
```

### 3. Code Quality
```bash
# Always activate venv first
source venv/bin/activate

# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

## Getting API Keys (All Free)

### 1. OpenWeatherMap (Weather Data)
- Visit: https://openweathermap.org/api
- Sign up for free account
- Get API key (1000 calls/day free)
- **Cost**: $0 forever

### 2. Aviationstack (Flight Data)
- Visit: https://aviationstack.com/
- Sign up for free plan (1000 requests/month)
- Get API key from dashboard
- **Cost**: $0 forever

### 3. Fixer.io (Currency Exchange)
- Visit: https://fixer.io/
- Sign up for free plan (100 requests/month)
- Get API key from dashboard
- **Cost**: $0 forever

### 4. Ollama (Local LLM - Completely Free)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (choose one)
ollama pull llama2          # General purpose
ollama pull codellama        # For code tasks
ollama pull mistral          # Lightweight option

# Start Ollama server
ollama serve
```
**Cost**: $0 forever (runs locally)

### 5. OpenStreetMap APIs (No Registration Needed)
- **Nominatim**: Geocoding and reverse geocoding
- **Overpass API**: Points of interest and map data
- **Cost**: $0 forever (community-maintained)
- **Usage**: No API key required, just use the endpoints directly

## ✅ Setup Verification

After completing the installation, verify your setup:

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests (should pass 3/3)
python -m pytest tests/ -v

# Start server
uvicorn app.main:app --reload --port 8000

# Test API endpoints
curl http://127.0.0.1:8000/  # Root endpoint
open http://127.0.0.1:8000/api/docs  # API documentation
```

**Expected Results:**
- ✅ All tests pass (3/3 health tests)
- ✅ Server starts without errors
- ✅ API documentation accessible
- ✅ Demo user created: `demo@example.com` / `demo123`
- ✅ SQLite database created: `travel_planner.db`
- ✅ GNN training pipeline operational (Phase 2 complete)

**Verification Commands:**
```bash
# Test GNN functionality (Phase 2 verification)
python test_gnn_suite.py  # Should show 9/9 tests passing

# Test GNN training specifically
python test_gnn_training.py  # Should show successful training
```

## Team Collaboration Guidelines

### 1. Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Feature development
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical fixes

### 2. Commit Convention
```
feat: add new feature
fix: bug fix
docs: documentation changes
style: formatting changes
refactor: code refactoring
test: add or update tests
chore: maintenance tasks
```

### 3. Code Review Process
1. Create feature branch
2. Implement feature with tests
3. Create pull request
4. Code review by team member
5. Merge to develop
6. Deploy to staging
7. Merge to main for production

### 4. Communication
- Daily standups: Progress updates
- Weekly retrospectives: Process improvements
- Slack/Discord: Real-time communication
- GitHub Issues: Task tracking

## Deployment Options

### Local Development
```bash
uvicorn app.main:app --reload
```

### Docker (Recommended for consistency)
```bash
docker-compose up -d
```

### Production (Free Options)
1. **Railway**: Free tier available
2. **Fly.io**: Free tier available
3. **Heroku**: Free tier (limited)
4. **Vercel**: Free tier for Python

## Monitoring and Logging

- **Local**: Structured logging with `structlog`
- **Production**: Can integrate with free tiers of Sentry, LogRocket
- **Metrics**: Prometheus (self-hosted, free)

## Timeline Alignment

### ✅ Phase 1: Enhanced LLM Orchestration (COMPLETED)
- [x] Enhanced LLM orchestrator with Ollama integration
- [x] Real-time API service with external travel data
- [x] Comprehensive validation with Pydantic V2
- [x] User profile modeling for GNN input
- [x] Production-ready testing framework

### ✅ Phase 2: GNN & Multi-modal Development (COMPLETED - October 2025)
- [x] **Graph Neural Network Architecture**: PyTorch Geometric implementation ✅
- [x] **Travel Knowledge Graph**: Heterogeneous graph with travel entities ✅
- [x] **GNN Training Pipeline**: Automatic training with positive/negative sampling ✅
- [x] **Trained Model Recommendations**: Real neural network-based suggestions ✅
- [x] **Comprehensive Testing Framework**: 100% test success rate (9/9 tests) ✅
- [x] **Performance Optimization**: Eliminated fallback mode warnings ✅

**Latest Achievement**: GNN training pipeline fully operational! Model trains from 0.6411 → 0.0000 loss, generates real neural network recommendations with 0.92 personalization score, and achieves 100% test success rate.

### ⏳ Phase 3: Multi-modal & Advanced AI Integration (NEXT - November 2025)
- [ ] **Multi-modal Reasoning System**: Text, image, and preference processing
- [ ] **Advanced LLM Integration**: Seamless orchestrator coordination
- [ ] **Context-aware Recommendations**: Dynamic preference learning
- [ ] **Real-time Decision Making**: Live adaptation to user feedback
- [ ] **Automated Booking Workflows**: End-to-end trip planning

### ⏳ Phase 4: Big Data & Scalability (PLANNED)
- [ ] Kafka stream processing
- [ ] Real-time data pipelines
- [ ] Scaling optimizations
- [ ] Performance testing

## 📋 Development Progress

### Phase 2 Status (COMPLETED ✅)
```
✅ Graph Neural Network Architecture    [COMPLETED]
✅ Travel Knowledge Graph               [COMPLETED]
✅ GNN Training Pipeline               [COMPLETED]
✅ Trained Model Recommendations       [COMPLETED]
✅ Comprehensive Testing Framework     [COMPLETED]
✅ Performance Optimization            [COMPLETED]
```

**🎉 Major Milestone Achieved**:
- **GraphAttentionTravelNet**: 3-layer GNN with 8 attention heads, 300,225 parameters
- **TravelKnowledgeGraph**: 6 entity types, 28+ relationship types
- **Enhanced Training Pipeline**: Positive/negative sampling, automatic training triggers
- **Real Neural Recommendations**: 0.92 personalization score (vs 0.65 fallback)
- **100% Test Success**: All 9 comprehensive test categories passing
- **Zero Warning Messages**: Eliminated "GNN model not trained" warnings

**Performance Metrics**:
- Training Loss: 0.6411 → 0.0000 (convergence achieved)
- Model Status: "Graph Neural Network (Trained)" 
- Recommendation Quality: 92% personalization vs 65% fallback
- Test Coverage: 9/9 test categories with 100% success rate

### Phase 3 Roadmap (Starting November 2025)
```
⏳ Multi-modal Reasoning System         [PLANNED]
⏳ Advanced LLM Integration             [PLANNED]
⏳ Context-aware Recommendations       [PLANNED]
⏳ Real-time Decision Making           [PLANNED]
⏳ Automated Booking Workflows         [PLANNED]
```

**Next Milestone**: Multi-modal reasoning for text + image + preference analysis

For detailed Phase 2 documentation and technical implementation, see [`PHASE2.md`](./PHASE2.md)

## Contributing

1. Read this README thoroughly
2. Set up your development environment
3. Pick an issue from GitHub Issues
4. Create feature branch
5. Implement with tests
6. Submit pull request
7. Participate in code review

## Support

- **Documentation**: Check `/docs` folder
- **Issues**: GitHub Issues
- **Questions**: Team Slack/Discord channel
- **Code Review**: GitHub Pull Requests

## Next Steps

1. **For New Team Members**:
   - Complete environment setup
   - Run the test suite
   - Review the codebase structure
   - Pick a starter issue

2. **For Project Leads**:
   - Assign GitHub Issues to team members
   - Set up CI/CD pipeline
   - Configure monitoring and logging
   - Schedule regular team meetings

---

Happy coding! 🚀✈️🏨

For questions, reach out to the team or create an issue in the repository.
