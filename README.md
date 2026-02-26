# CityPulse - Hyperlocal Community Intelligence Platform

CityPulse is a hyperlocal community intelligence platform that uses multi-agent AI systems to monitor and synthesize neighborhood information. The platform leverages Amazon Bedrock's Nova models to provide residents with real-time insights about their community.

## Overview

CityPulse aggregates data from multiple sources including city permit databases, social media platforms, local news outlets, and community-submitted images to provide comprehensive neighborhood intelligence. The system uses five specialized AI agents to collect, analyze, and synthesize information into actionable insights.

## Architecture

The project is divided into three main layers:

1. **Agent Layer** - Five AI agents powered by Amazon Nova models
2. **Backend Layer** - API services, authentication, and data management
3. **Frontend Layer** - User-facing web application

## Project Structure

```
citypulse/
├── agents/              # AI agent implementations (Team Member 1)
│   ├── permit-monitor/
│   ├── social-listening/
│   ├── news-synthesis/
│   ├── visual-intelligence/
│   ├── voice-briefing/
│   ├── shared/         # Shared utilities and Bedrock client
│   └── infrastructure/ # Deployment scripts and IaC
├── backend/            # Backend API services (Team Member 2)
├── frontend/           # Web UI (Team Member 2)
│   └── CityPlus-prototype/
├── docs/               # Documentation and API contracts
│   ├── api-contracts/
│   └── architecture/
├── shared/             # Shared schemas and configuration
│   ├── schemas/        # JSON schemas for data models
│   └── config/
└── README.md
```

## AI Agents

### 1. Permit Monitor Agent
- **Model**: Amazon Nova Act
- **Purpose**: Scrapes city permit databases and extracts structured permit data
- **Output**: Building permits, liquor licenses, zoning changes, demolition permits

### 2. Social Listening Agent
- **Model**: Amazon Nova Act + Nova 2 Lite
- **Purpose**: Monitors social media and community boards for local discussions
- **Output**: Trending topics, sentiment analysis, community concerns

### 3. News Synthesis Agent
- **Model**: Amazon Nova 2 Lite
- **Purpose**: Aggregates and summarizes local news from RSS feeds
- **Output**: Relevant news summaries with relevance scores

### 4. Visual Intelligence Agent
- **Model**: Amazon Nova Multimodal
- **Purpose**: Analyzes images from community posts for safety and events
- **Output**: Object detection, text extraction, scene classification

### 5. Voice Briefing Agent
- **Model**: Amazon Nova 2 Lite + Nova 2 Sonic
- **Purpose**: Generates personalized voice briefings
- **Output**: Text and audio briefings summarizing neighborhood activity

## Technology Stack

### AWS Services
- **Amazon Bedrock** - AI model hosting (Nova 2 Lite, Nova 2 Sonic, Nova Multimodal, Nova Act)
- **AWS Lambda** - Serverless compute for agent functions
- **Amazon API Gateway** - REST API endpoints
- **Amazon DynamoDB** - NoSQL database for agent data
- **Amazon S3** - Object storage for images and audio files
- **Amazon EventBridge** - Scheduled agent execution
- **Amazon CloudWatch** - Logging and monitoring

### Backend
- Python 3.11+ for Lambda functions
- Node.js/Express or Python/Flask for backend API (TBD)
- Redis for caching (optional)

### Frontend
- HTML/CSS/JavaScript (building on existing prototype)
- Real-time updates via WebSocket

## Data Schemas

All data schemas are defined in `/shared/schemas/` using JSON Schema format:

- `permit.json` - City permit data structure
- `social-post.json` - Social media post structure
- `news-article.json` - News article structure
- `briefing.json` - Voice briefing structure

## Team Responsibilities

### Team Member 1 (AI/Agent Handler)
- AWS infrastructure setup and configuration
- Amazon Bedrock model access and configuration
- Implementation of all five AI agents
- Lambda function deployment
- API Gateway configuration
- DynamoDB and S3 setup
- API documentation and integration examples

### Team Member 2 (Backend/Frontend Developer)
- Backend API development
- User authentication and authorization
- Database schema design for user data
- Frontend enhancement and integration
- Real-time notification system
- UI components for displaying insights

## Getting Started

### Prerequisites
- AWS Account with Bedrock access
- AWS CLI configured
- Python 3.11+ (for agents)
- Node.js 18+ (for backend, if using Node.js)
- Git

### Setup Instructions

#### For Team Member 1 (Agents)
1. Configure AWS CLI:
   ```bash
   aws configure
   ```

2. Enable Bedrock models in AWS Console:
   - Navigate to Bedrock > Model access
   - Enable: Nova 2 Lite, Nova 2 Sonic, Nova Multimodal, Nova Act

3. Create DynamoDB tables:
   ```bash
   cd agents/infrastructure
   ./setup-dynamodb.sh
   ```

4. Deploy agents:
   ```bash
   cd agents/permit-monitor
   ./deploy.sh
   ```

#### For Team Member 2 (Backend/Frontend)
1. Install backend dependencies:
   ```bash
   cd backend
   npm install  # or pip install -r requirements.txt
   ```

2. Configure environment variables:
   ```bash
   cp shared/config/.env.example .env
   # Edit .env with API keys and endpoints
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

## API Documentation

API contracts are documented using OpenAPI/Swagger format in `/docs/api-contracts/`:

- `agent-apis.yaml` - Agent API endpoints (Team Member 1)
- `backend-apis.yaml` - Backend API endpoints (Team Member 2)

View live documentation at: [API Docs URL]

## Development Workflow

### Phase 1: Foundation (Week 1-2)
- AWS infrastructure setup
- Basic agent implementation (Permit Monitor)
- Initial API Gateway configuration

### Phase 2: Multi-Agent Development (Week 3-4)
- Implement remaining agents
- Backend API development
- Agent integration

### Phase 3: Voice Briefing & Frontend (Week 5-6)
- Voice briefing agent
- Frontend enhancement
- Real-time notifications

### Phase 4: Polish & Deploy (Week 7-8)
- Performance optimization
- Security hardening
- Production deployment

## Testing

### Agent Testing
```bash
cd agents/permit-monitor
python -m pytest tests/
```

### Backend Testing
```bash
cd backend
npm test
```

### Integration Testing
End-to-end tests are located in `/tests/integration/`

## Deployment

### Agents (Lambda)
```bash
cd agents/infrastructure
./deploy.sh --env production
```

### Backend
```bash
cd backend
npm run deploy
```

## Monitoring

- CloudWatch Logs: Monitor Lambda function execution
- CloudWatch Alarms: Alert on errors and high latency
- API Gateway Metrics: Track API usage and performance

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Write tests for new functionality
4. Submit a pull request

## Communication

- Daily async updates in Slack/Discord
- Weekly sync meetings every Monday
- Handoff checklist for integration points

## License

[License Type] - See LICENSE file for details

## Contact

- Team Member 1 (AI/Agents): [Contact Info]
- Team Member 2 (Backend/Frontend): [Contact Info]

## Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Amazon Nova Models](https://aws.amazon.com/bedrock/nova/)
- [Project Architecture Diagram](docs/architecture/system-diagram.png)
- [Integration Guide](docs/integration-guide.md)
