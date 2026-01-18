# NexHacks - Polymarket Trade Assistant

## 🎯 What It Does

**NexHacks** is an intelligent Chrome Extension that transforms Polymarket trading by providing real-time, AI-powered trade recommendations directly on market pages. When you're viewing a prediction market on Polymarket.com, NexHacks analyzes market correlations and automatically suggests:

- **Amplify Trades** - Correlated markets that can magnify your position
- **Hedge Opportunities** - Inverse correlations to protect your portfolio
- **Related Markets** - Similar prediction markets based on semantic analysis

All recommendations appear in a beautiful floating panel that seamlessly integrates with Polymarket's interface without modifying the site itself.

---

## 💡 The Problem We Solve

Polymarket is a leading prediction market platform with thousands of active markets, but it lacks tools to help traders:

1. **Discover Correlations** - Finding related markets requires manual research across hundreds of pages
2. **Maximize Returns** - No guidance on which markets work together to amplify profits
3. **Manage Risk** - Difficult to identify hedging opportunities to protect positions
4. **Avoid Contradictions** - No warnings when trades might conflict with existing positions

Traders are left analyzing markets in isolation, missing opportunities for strategic portfolio construction.

---

## ✨ Our Solution

NexHacks brings institutional-grade market intelligence directly to Polymarket traders through:

### 🔍 **Intelligent Market Analysis**
- **Semantic Similarity**: Uses Google's Gemini AI to analyze market questions and find semantically related markets
- **Price Correlation**: Calculates statistical correlations between market prices using historical data
- **Category Mapping**: Identifies relationships across different market categories (politics, finance, sports, etc.)

### 🚀 **Real-Time Recommendations**
- **Amplify Tab**: Shows 5 correlated markets that can strengthen your position
- **Hedge Tab**: Displays 5 inverse-correlated markets for risk mitigation
- **Smart Ranking**: Recommendations scored by correlation strength, relevance, and market activity

### 📊 **Portfolio Awareness**
- Automatically tracks your trading history in the browser
- Builds a local profile of your interests (topics, entities, patterns)
- Personalizes recommendations based on your trading behavior

### 🎨 **Seamless Integration**
- Shadow DOM injection - completely isolated from Polymarket's CSS
- Non-intrusive floating panel with minimize/maximize
- Works instantly on any market page without setup

---

## 🏗️ How We Built It

### **Frontend: Chrome Extension (Manifest V3)**
- **React + TypeScript** for type-safe, component-based UI
- **Vite** for fast development and optimized builds
- **Chrome Storage API** for persistent market history tracking
- **Shadow DOM** for CSS isolation and clean integration
- **MutationObserver** for detecting page navigation in SPA

### **Backend: FastAPI Service**
- **FastAPI** for high-performance async API endpoints
- **Python** for data analysis and ML integration
- **Supabase (PostgreSQL)** for market data storage and queries
- **Polymarket Gamma API** for real-time market data
- **Polymarket CLOB API** for price history and order book data
- **Google Gemini API** for semantic analysis and entity extraction

### **Key Technical Highlights**
- **Correlation Engine**: Computes Pearson correlation coefficients on 7-day and 30-day price windows
- **Similarity Scoring**: Multi-factor scoring combining text similarity, price correlation, and category overlap
- **Caching Layer**: Aggressive caching to ensure <3 second recommendation latency
- **Error Handling**: Graceful fallbacks ensure the extension never breaks Polymarket's UI

---

## 📈 Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Chrome Browser (Extension)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Content Script (content.tsx)                    │  │
│  │  • Scrapes market data from page                 │  │
│  │  • Injects Shadow DOM panel                      │  │
│  │  • Tracks user interactions                      │  │
│  └──────────────────────────────────────────────────┘  │
│                        ↕                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Floating Assistant Panel                        │  │
│  │  • React Components                              │  │
│  │  • Real-time recommendations                     │  │
│  │  • Basket builder                                │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↕ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│            FastAPI Backend (localhost:8000)             │
│  ┌──────────────────────────────────────────────────┐  │
│  │  /v1/recommendations                             │  │
│  │  • Market correlation analysis                   │  │
│  │  • Similarity scoring                            │  │
│  │  • Recommendation generation                     │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↕
┌─────────────────────────────────────────────────────────┐
│                   External APIs                         │
│  • Polymarket Gamma API (market data)                  │
│  • Polymarket CLOB API (price history)                 │
│  • Google Gemini API (semantic analysis)               │
│  • Supabase (PostgreSQL database)                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Features

### ✅ **Amplify Recommendations**
Find markets that move together with your primary trade. Perfect for building strong, correlated positions.

### ✅ **Hedge Recommendations**  
Discover inverse correlations to protect your portfolio against downside risk.

### ✅ **Automatic Profile Building**
The extension learns from your trading history to provide personalized recommendations.

### ✅ **Real-Time Updates**
Recommendations update instantly as you navigate between markets.

### ✅ **Zero Configuration**
Works out of the box - just install and start trading smarter.

### ✅ **Performance Optimized**
Sub-3-second recommendation latency with intelligent caching.

---

## 💻 Technologies Used

- **Frontend**: React, TypeScript, Vite, Chrome Extension APIs
- **Backend**: FastAPI, Python, AsyncIO
- **Database**: Supabase (PostgreSQL)
- **AI/ML**: Google Gemini API for semantic analysis
- **APIs**: Polymarket Gamma API, Polymarket CLOB API
- **Storage**: Chrome Storage API, Supabase

---

## 🚀 What's Next

- **Market Basket Builder**: Create parlay combinations from correlated markets
- **Contradiction Detection**: Warn users before placing conflicting trades
- **Advanced Analytics**: Historical performance tracking for recommendations
- **Community Features**: Share and discover market correlation insights
- **Mobile Support**: Bring these features to Polymarket mobile apps

---

## 🎓 What We Learned

Building NexHacks taught us:

- **Chrome Extension Architecture**: Deep dive into Manifest V3, content scripts, and Shadow DOM isolation
- **Market Correlation Analysis**: Statistical methods for identifying relationships in prediction markets
- **Semantic AI Integration**: Using LLMs (Gemini) for financial market analysis
- **Real-Time Data Processing**: Efficient handling of live market data streams
- **User Experience Design**: Creating non-intrusive browser extensions that enhance rather than distract

---

## 👥 Team

- **Shivani**: Backend & Frontend Development
- **Nicolas**: Backend Development & Architecture
- **Shilo**: Database Management & Supabase Integration
- **Arav**: Business Logic, Pitch Deck & Frontend

---

## 📝 Try It Yourself

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd NexHacks
   ```

2. **Start the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python run.py
   ```

3. **Build and load the extension**
   ```bash
   cd Extension
   npm install
   npm run build
   # Load Extension/dist in Chrome via chrome://extensions/
   ```

4. **Visit Polymarket.com** and see recommendations appear automatically!

---

## 🏆 Impact

NexHacks democratizes advanced trading strategies by bringing institutional-grade market intelligence to every Polymarket trader. Whether you're a casual trader looking to diversify or a serious market participant managing a portfolio, NexHacks helps you:

- **Make Better Decisions** - Data-driven recommendations based on real correlations
- **Manage Risk** - Automatic hedging suggestions protect your capital
- **Save Time** - No more manual market research across hundreds of pages
- **Increase Returns** - Discover amplification opportunities you might have missed

---

*Built with ❤️ for the Polymarket community*
