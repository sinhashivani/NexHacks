# Task List: Third-Party Integrations

## Overview

This document lists all tasks required for third-party integrations, separated into:
- **Autonomous Tasks**: Can be completed by development team
- **External Tasks**: Require external actions (API keys, approvals, etc.)

---

## Tier 1: MVP Integrations (Week 1-2)

### The Odds API Integration

#### External Tasks (Cannot Do Autonomously)

- [ ] **Get The Odds API Key**
  - **Who**: Arav or Nicolas
  - **Action**: Sign up at https://the-odds-api.com/
  - **Free Tier**: 500 requests/month
  - **Paid Tier**: $10/month for 10,000 requests
  - **Timeline**: Day 1
  - **Deliverable**: API key string

- [ ] **Verify API Access**
  - **Who**: Shivani
  - **Action**: Test API key with curl command
  - **Command**: `curl "https://api.the-odds-api.com/v4/sports?apiKey=YOUR_KEY"`
  - **Timeline**: Day 1
  - **Deliverable**: Confirmation API works

#### Autonomous Tasks (Can Do Now)

- [x] **Create OddsAPIService class**
  - **File**: `services/odds_api.py`
  - **Status**: ✅ Implemented in guide

- [x] **Create CorrelationEngine class**
  - **File**: `services/correlation_engine.py`
  - **Status**: ✅ Implemented in guide

- [x] **Create database migration for odds tables**
  - **File**: `database/migrations/006_create_odds_correlation.sql`
  - **Status**: ✅ Implemented in guide

- [ ] **Implement API endpoints**
  - **File**: `api/main.py`
  - **Endpoints**: `/odds/sports`, `/odds/correlated`, `/parlay/suggestions`
  - **Timeline**: Day 2-3
  - **Owner**: Shivani

- [ ] **Add environment variable handling**
  - **File**: `.env.example`
  - **Variable**: `THE_ODDS_API_KEY`
  - **Timeline**: Day 1
  - **Owner**: Nicolas

- [ ] **Create test script**
  - **File**: `scripts/test_odds_api.py`
  - **Timeline**: Day 2
  - **Owner**: Shivani

- [ ] **Add error handling and rate limiting**
  - **File**: `services/odds_api.py`
  - **Timeline**: Day 3
  - **Owner**: Shivani

- [ ] **Create frontend component (if applicable)**
  - **File**: `frontend/components/CorrelatedOdds.tsx`
  - **Timeline**: Day 4-5
  - **Owner**: Frontend team

---

### MetaMask Snap Integration

#### External Tasks (Cannot Do Autonomously)

- [ ] **Create MetaMask Developer Account**
  - **Who**: Arav or Nicolas
  - **Action**: Sign up at https://developers.metamask.io/
  - **Timeline**: Day 1
  - **Deliverable**: Developer account access

- [ ] **Submit Snap for Review (if publishing)**
  - **Who**: Arav
  - **Action**: Submit to MetaMask Snap registry
  - **Timeline**: Week 2 (after development)
  - **Deliverable**: Published Snap or approval pending

- [ ] **Get Snap ID from MetaMask**
  - **Who**: Development team
  - **Action**: Register Snap and get ID
  - **Timeline**: Day 2
  - **Deliverable**: Snap ID string

- [ ] **Test with MetaMask Wallet**
  - **Who**: All team members
  - **Action**: Install MetaMask extension, test Snap
  - **Timeline**: Day 4-5
  - **Deliverable**: Working Snap in MetaMask

#### Autonomous Tasks (Can Do Now)

- [x] **Create Snap manifest**
  - **File**: `metamask-snap/snap.manifest.json`
  - **Status**: ✅ Implemented in guide

- [x] **Create Snap source code**
  - **File**: `metamask-snap/src/index.ts`
  - **Status**: ✅ Implemented in guide

- [x] **Create website integration example**
  - **File**: `metamask-snap/website/index.html`
  - **Status**: ✅ Implemented in guide

- [ ] **Set up Snap development environment**
  - **Action**: Install MetaMask Flask, set up build tools
  - **Timeline**: Day 1
  - **Owner**: Shivani

- [ ] **Build and bundle Snap**
  - **Action**: Configure build process, create bundle.js
  - **Timeline**: Day 2
  - **Owner**: Shivani

- [ ] **Implement Snap RPC methods**
  - **Methods**: `get_trending_markets`, `get_parlay_suggestions`, `get_correlated_odds`
  - **Timeline**: Day 2-3
  - **Owner**: Shivani

- [ ] **Create Snap UI components**
  - **Action**: Design and implement dialog panels
  - **Timeline**: Day 3
  - **Owner**: Frontend team

- [ ] **Test Snap locally with Flask**
  - **Action**: Test all RPC methods
  - **Timeline**: Day 4
  - **Owner**: All team

- [ ] **Create Snap documentation**
  - **File**: `metamask-snap/README.md`
  - **Timeline**: Day 5
  - **Owner**: Nicolas

---

### Zapier Integration

#### External Tasks (Cannot Do Autonomously)

- [ ] **Create Zapier Developer Account**
  - **Who**: Arav or Nicolas
  - **Action**: Sign up at https://zapier.com/apps/developer
  - **Timeline**: Day 1
  - **Deliverable**: Developer account

- [ ] **Create Zapier App**
  - **Who**: Arav
  - **Action**: Create new app in Zapier developer dashboard
  - **Timeline**: Day 2
  - **Deliverable**: Zapier app ID

- [ ] **Submit Zapier App for Review (if public)**
  - **Who**: Arav
  - **Action**: Submit app to Zapier marketplace
  - **Timeline**: Week 2 (after development)
  - **Deliverable**: Published app or approval pending

- [ ] **Test Zapier Webhook in Production**
  - **Who**: All team
  - **Action**: Create test Zap, trigger webhook
  - **Timeline**: Day 5
  - **Deliverable**: Working Zap

#### Autonomous Tasks (Can Do Now)

- [x] **Create webhook endpoints**
  - **File**: `api/main.py`
  - **Status**: ✅ Implemented in guide

- [x] **Create webhooks database table**
  - **File**: `database/migrations/007_create_webhooks_table.sql`
  - **Status**: ✅ Implemented in guide

- [ ] **Implement webhook registration endpoint**
  - **Endpoint**: `POST /webhooks/parlay-alert`
  - **Timeline**: Day 2
  - **Owner**: Shivani

- [ ] **Implement webhook trigger system**
  - **Endpoint**: `POST /webhooks/trigger`
  - **Timeline**: Day 3
  - **Owner**: Shivani

- [ ] **Create background task for parlay checking**
  - **Action**: Periodic job to check for new opportunities
  - **Timeline**: Day 3-4
  - **Owner**: Shivani

- [ ] **Add webhook authentication**
  - **Action**: Secure webhook endpoints
  - **Timeline**: Day 4
  - **Owner**: Shivani

- [ ] **Create Zapier template JSON**
  - **File**: `zapier/template.json`
  - **Timeline**: Day 2
  - **Owner**: Nicolas

- [ ] **Test webhook with Zapier test environment**
  - **Action**: Create test Zap, verify data flow
  - **Timeline**: Day 4-5
  - **Owner**: All team

---

## Tier 2: Extended Integrations (Week 3-4)

### Binance API Integration

#### External Tasks (Cannot Do Autonomously)

- [ ] **Create Binance API Key**
  - **Who**: Arav or Nicolas
  - **Action**: Sign up at https://www.binance.com/en/my/settings/api-management
  - **Note**: Read-only key is sufficient
  - **Timeline**: Week 3, Day 1
  - **Deliverable**: API key and secret

- [ ] **Verify Binance API Access**
  - **Who**: Shivani
  - **Action**: Test API with key
  - **Timeline**: Week 3, Day 1
  - **Deliverable**: Confirmation API works

#### Autonomous Tasks (Can Do Now)

- [x] **Create BinanceAPIService class**
  - **File**: `services/binance_api.py`
  - **Status**: ✅ Implemented in guide

- [ ] **Implement crypto correlation logic**
  - **Action**: Match crypto symbols in market questions
  - **Timeline**: Week 3, Day 2
  - **Owner**: Shivani

- [ ] **Add Binance endpoints to API**
  - **Endpoints**: `/crypto/correlated`, `/crypto/price`
  - **Timeline**: Week 3, Day 2-3
  - **Owner**: Shivani

- [ ] **Add environment variables**
  - **Variables**: `BINANCE_API_KEY`, `BINANCE_SECRET_KEY`
  - **Timeline**: Week 3, Day 1
  - **Owner**: Nicolas

---

### PrizePicks Integration

#### External Tasks (Cannot Do Autonomously)

- [ ] **Contact PrizePicks for API Access**
  - **Who**: Arav
  - **Action**: Email partnerships@prizepicks.com or developer relations
  - **Note**: May not have public API - need partnership
  - **Timeline**: Week 3
  - **Deliverable**: API access or partnership agreement

- [ ] **Research PrizePicks Data Sources**
  - **Who**: Nicolas
  - **Action**: Find if they have public data feeds or scraping options
  - **Timeline**: Week 3
  - **Deliverable**: Data source identified

#### Autonomous Tasks (Can Do Now)

- [ ] **Research PrizePicks data structure**
  - **Action**: Analyze their website/app for data patterns
  - **Timeline**: Week 3, Day 1
  - **Owner**: Nicolas

- [ ] **Create PrizePicks service (if API available)**
  - **File**: `services/prizepicks_api.py`
  - **Timeline**: Week 3, Day 2-3
  - **Owner**: Shivani

---

### Kraken/Coinbase Integration

#### External Tasks (Cannot Do Autonomously)

- [ ] **Get Kraken API Key**
  - **Who**: Arav or Nicolas
  - **Action**: Sign up at https://www.kraken.com/u/security/api
  - **Timeline**: Week 4, Day 1
  - **Deliverable**: API key

- [ ] **Get Coinbase API Key**
  - **Who**: Arav or Nicolas
  - **Action**: Sign up at https://www.coinbase.com/api
  - **Timeline**: Week 4, Day 1
  - **Deliverable**: API key

#### Autonomous Tasks (Can Do Now)

- [ ] **Create Kraken service**
  - **File**: `services/kraken_api.py`
  - **Timeline**: Week 4, Day 2
  - **Owner**: Shivani

- [ ] **Create Coinbase service**
  - **File**: `services/coinbase_api.py`
  - **Timeline**: Week 4, Day 2
  - **Owner**: Shivani

---

## Tier 3: Strategic Integrations (Month 2)

### Dome API Integration

#### External Tasks (Cannot Do Autonomously)

- [ ] **Wait for Dome API Launch**
  - **Who**: All team
  - **Action**: Monitor for API announcement
  - **Timeline**: TBD
  - **Deliverable**: API documentation

- [ ] **Get Dome API Access**
  - **Who**: Arav
  - **Action**: Apply for early access or API key
  - **Timeline**: When available
  - **Deliverable**: API key

#### Autonomous Tasks (Can Do Now)

- [ ] **Research Dome API (when available)**
  - **Action**: Study API documentation
  - **Timeline**: When API launches
  - **Owner**: Nicolas

- [ ] **Create Dome service**
  - **File**: `services/dome_api.py`
  - **Timeline**: After API access
  - **Owner**: Shivani

---

### HubSpot/Enterprise Integration

#### External Tasks (Cannot Do Autonomously)

- [ ] **Contact HubSpot for Partnership**
  - **Who**: Arav
  - **Action**: Reach out to HubSpot partnerships team
  - **Timeline**: Month 2
  - **Deliverable**: Partnership discussion or API access

- [ ] **Get HubSpot API Credentials**
  - **Who**: Arav
  - **Action**: Create HubSpot developer account
  - **Timeline**: Month 2
  - **Deliverable**: API credentials

#### Autonomous Tasks (Can Do Now)

- [ ] **Research HubSpot API**
  - **Action**: Study HubSpot App Marketplace requirements
  - **Timeline**: Month 2, Week 1
  - **Owner**: Nicolas

- [ ] **Create HubSpot app structure**
  - **File**: `hubspot-app/`
  - **Timeline**: Month 2, Week 2
  - **Owner**: Shivani

---

## General Tasks (All Integrations)

### External Tasks

- [ ] **Set up Production Environment**
  - **Who**: Nicolas
  - **Action**: Configure production server, domain, SSL
  - **Timeline**: Week 1
  - **Deliverable**: Production API URL

- [ ] **Set up Monitoring/Logging**
  - **Who**: Nicolas
  - **Action**: Configure error tracking (Sentry, etc.)
  - **Timeline**: Week 1
  - **Deliverable**: Monitoring dashboard

- [ ] **Get Legal Review (if needed)**
  - **Who**: Arav
  - **Action**: Review terms of service for each API
  - **Timeline**: Week 1
  - **Deliverable**: Approval to use APIs

### Autonomous Tasks

- [ ] **Create integration test suite**
  - **File**: `tests/test_integrations.py`
  - **Timeline**: Week 2
  - **Owner**: Shivani

- [ ] **Add rate limiting**
  - **Action**: Implement rate limiting for all external APIs
  - **Timeline**: Week 2
  - **Owner**: Shivani

- [ ] **Create API documentation**
  - **File**: `docs/API_ENDPOINTS.md` (update)
  - **Timeline**: Week 2
  - **Owner**: Nicolas

- [ ] **Add error handling**
  - **Action**: Comprehensive error handling for all integrations
  - **Timeline**: Week 2
  - **Owner**: Shivani

- [ ] **Create integration status dashboard**
  - **Action**: Show status of all integrations
  - **Timeline**: Week 2
  - **Owner**: Frontend team

---

## Priority Order

### Week 1 (Critical Path)
1. Get The Odds API key
2. Implement Odds API service
3. Create correlation engine
4. Test basic integration

### Week 2 (MVP Completion)
1. Complete MetaMask Snap development
2. Set up Zapier webhooks
3. Test all Tier 1 integrations
4. Create demo

### Week 3-4 (Extended)
1. Binance API integration
2. PrizePicks research/contact
3. Additional crypto exchanges

### Month 2 (Strategic)
1. Dome API (when available)
2. HubSpot partnership discussions
3. Enterprise integrations

---

## Blockers & Dependencies

### Blockers
- **The Odds API Key**: Blocks all sports correlation work
- **MetaMask Developer Account**: Blocks Snap development
- **Production Environment**: Blocks webhook testing

### Dependencies
- **Database Migrations**: Must run before API endpoints
- **Environment Variables**: Must be set before services work
- **API Keys**: Must be obtained before testing

---

## Success Metrics

### Tier 1 (Week 2)
- [ ] The Odds API: 10+ correlated markets found
- [ ] MetaMask Snap: Can display trending markets
- [ ] Zapier: Can trigger webhook on new parlay

### Tier 2 (Week 4)
- [ ] Binance: Crypto correlations working
- [ ] PrizePicks: Partnership discussion started

### Tier 3 (Month 2)
- [ ] Dome API: Integration ready when API launches
- [ ] HubSpot: Partnership discussion initiated

---

## Notes

- **API Rate Limits**: Be aware of rate limits for all APIs
- **Cost Management**: Monitor API usage costs
- **Error Handling**: All integrations must handle API failures gracefully
- **Testing**: Test each integration in isolation before combining
- **Documentation**: Keep integration docs updated as APIs change
