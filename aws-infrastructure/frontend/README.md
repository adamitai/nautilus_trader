# Frontend Dashboard - Nautilus Trader Arbitrage Tools

A modern web-based dashboard for monitoring and controlling the Nautilus Trader arbitrage system.

## 🎯 Features

### Trading Dashboard
- **Real-time arbitrage opportunities** with live price feeds
- **Interactive charts** showing price spreads and trends
- **Trading signals** with profit/loss calculations
- **Exchange connectivity status** and API health

### Portfolio Management
- **Current positions** across all exchanges
- **Balance tracking** and P&L visualization
- **Risk metrics** and exposure analysis
- **Trade history** with detailed analytics

### System Monitoring
- **Service health** and performance metrics
- **Resource utilization** (CPU, memory, database)
- **Log viewer** with real-time updates
- **Alert management** and notification settings

### Configuration
- **Trading parameters** adjustment
- **Exchange settings** and API key management
- **Risk limits** and position sizing
- **Strategy configuration** and backtesting

## 🏗️ Architecture

### Frontend Stack
- **React 18** with TypeScript
- **Material-UI** for modern components
- **Chart.js** for data visualization
- **WebSocket** for real-time updates
- **Axios** for API communication

### Backend API
- **FastAPI** for REST endpoints
- **WebSocket** for real-time data
- **JWT authentication** for security
- **Rate limiting** and request validation

### Data Flow
```
Frontend (React) ←→ API Gateway ←→ Backend Services ←→ Trading System
     ↓                    ↓              ↓              ↓
WebSocket ←→ Real-time Updates ←→ Database ←→ Exchange APIs
```

## 🚀 Quick Start

### Development Setup

```bash
# Install dependencies
cd aws-infrastructure/frontend
npm install

# Start development server
npm run dev

# Access dashboard
open http://localhost:3000
```

### Production Deployment

```bash
# Build for production
npm run build

# Deploy with Docker
docker build -t nautilus-dashboard .
docker run -p 3000:3000 nautilus-dashboard
```

## 📱 Dashboard Screens

### 1. Trading Overview
- Live arbitrage opportunities
- Current market conditions
- Exchange status indicators
- Quick action buttons

### 2. Portfolio View
- Position summary
- P&L charts
- Risk metrics
- Balance across exchanges

### 3. Analytics
- Historical performance
- Strategy backtesting
- Market analysis
- Correlation studies

### 4. System Status
- Service health
- Resource monitoring
- Log viewer
- Alert management

### 5. Configuration
- Trading parameters
- Exchange settings
- Risk management
- User preferences

## 🔐 Security Features

- **JWT Authentication** with refresh tokens
- **Role-based access control** (Admin, Trader, Viewer)
- **API rate limiting** and request validation
- **HTTPS only** in production
- **CORS configuration** for cross-origin requests

## 📊 Real-time Updates

### WebSocket Events
- `arbitrage_opportunity` - New trading opportunity
- `price_update` - Live price feeds
- `trade_executed` - Trade completion
- `system_alert` - System notifications
- `portfolio_update` - Balance changes

### Data Refresh
- **Prices**: Every 1-5 seconds
- **Portfolio**: Every 10-30 seconds
- **System metrics**: Every 60 seconds
- **Logs**: Real-time streaming

## 🎨 UI Components

### Charts and Visualizations
- **Candlestick charts** for price history
- **Line charts** for spreads and trends
- **Bar charts** for volume and P&L
- **Gauge charts** for risk metrics
- **Heatmaps** for correlation analysis

### Interactive Elements
- **Real-time tables** with sorting and filtering
- **Modal dialogs** for trade execution
- **Dropdown menus** for configuration
- **Toggle switches** for feature control
- **Progress bars** for loading states

## 📱 Responsive Design

- **Mobile-first** approach
- **Tablet optimization** for trading
- **Desktop enhancement** for analysis
- **Touch-friendly** controls
- **Adaptive layouts** for all screen sizes

## 🔧 Configuration

### Environment Variables
```bash
REACT_APP_API_URL=https://api.nautilus-arbitrage.com
REACT_APP_WS_URL=wss://ws.nautilus-arbitrage.com
REACT_APP_ENVIRONMENT=production
REACT_APP_VERSION=1.0.0
```

### API Endpoints
```typescript
// Trading endpoints
GET /api/opportunities - Get arbitrage opportunities
POST /api/trades - Execute trade
GET /api/portfolio - Get portfolio data

// System endpoints
GET /api/health - System health check
GET /api/metrics - Performance metrics
GET /api/logs - System logs

// Configuration endpoints
GET /api/config - Get configuration
PUT /api/config - Update configuration
GET /api/exchanges - Exchange status
```

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### AWS Deployment
- **S3 + CloudFront** for static hosting
- **API Gateway** for backend API
- **Lambda** for serverless functions
- **WebSocket API** for real-time updates

## 📈 Performance

### Optimization Features
- **Code splitting** for faster loading
- **Lazy loading** for components
- **Memoization** for expensive calculations
- **Virtual scrolling** for large datasets
- **Image optimization** and compression

### Caching Strategy
- **Browser caching** for static assets
- **API response caching** for frequently accessed data
- **WebSocket connection pooling**
- **Local storage** for user preferences

## 🧪 Testing

### Test Coverage
- **Unit tests** for components and utilities
- **Integration tests** for API endpoints
- **E2E tests** for user workflows
- **Performance tests** for load handling

### Testing Tools
- **Jest** for unit testing
- **React Testing Library** for component testing
- **Cypress** for E2E testing
- **Lighthouse** for performance testing

## 📚 Documentation

- **Component documentation** with Storybook
- **API documentation** with OpenAPI/Swagger
- **User guide** with interactive tutorials
- **Developer guide** for customization

## 🔄 Updates and Maintenance

### Version Management
- **Semantic versioning** for releases
- **Feature flags** for gradual rollouts
- **A/B testing** for UI improvements
- **Rollback capabilities** for quick fixes

### Monitoring
- **Error tracking** with Sentry
- **Performance monitoring** with Web Vitals
- **User analytics** with privacy focus
- **Uptime monitoring** for availability

## 🆘 Support

### Help Resources
- **In-app help** with contextual guidance
- **Video tutorials** for key features
- **FAQ section** for common questions
- **Contact support** for technical issues

### Community
- **GitHub issues** for bug reports
- **Feature requests** for enhancements
- **Documentation contributions** welcome
- **Community forum** for discussions
