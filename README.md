# NEXUS Trading OS

Institutional Trading Operating System — 250+ modules, 30+ strategies, Bloomberg-level terminal.

**Cost: ~$14/month | Stack: FastAPI + React + PostgreSQL + Redis + Qdrant**

---

## Quick Start (VPS Deployment)

### Step 1 — Get a VPS

Go to [hetzner.com](https://hetzner.com) → Cloud → Add Server
- OS: Ubuntu 22.04
- Type: CX22 (2 vCPU, 4GB RAM)
- Location: Finland or Germany
- Cost: €3.79/month

### Step 2 — Connect to VPS

Download [Termius](https://termius.com) on your computer.
Add your server IP, username `root`, and password from Hetzner email.

### Step 3 — Install Docker

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Verify
docker --version
docker compose version
```

### Step 4 — Upload NEXUS

```bash
# Create directory
mkdir -p /opt/nexus && cd /opt/nexus

# Upload files (from your computer using scp or SFTP)
# Or clone if you have git repo:
# git clone your-repo /opt/nexus
```

### Step 5 — Configure

```bash
# Copy env template
cp .env.example .env

# Edit with your API keys
nano .env

# Minimum required:
# SECRET_KEY=random_64_char_string
# MASTER_PASSWORD=your_password
# POSTGRES_PASSWORD=strong_db_password
# REDIS_PASSWORD=strong_redis_password
# ENCRYPTION_KEY=32_char_string
# JWT_SECRET=random_64_char_string
# ANTHROPIC_API_KEY=sk-ant-...
# TELEGRAM_BOT_TOKEN=... (from @BotFather)
# TELEGRAM_ADMIN_ID=... (your Telegram user ID)
```

### Step 6 — Start

```bash
# Build and start everything
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f backend

# View all logs
docker compose logs -f
```

### Step 7 — Access

- **Dashboard**: http://your-server-ip:3000
- **API docs**: http://your-server-ip:8000/api/docs
- **Telegram bot**: Find your bot by username

---

## Architecture

```
┌─────────────────────────────────────────────┐
│                    YOU                       │
│         Telegram / Dashboard / PWA           │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│              NEXUS on VPS                    │
│                                             │
│  ┌─────────────┐    ┌─────────────────────┐ │
│  │  AI WAR ROOM│    │   DATA COLLECTOR    │ │
│  │             │    │                     │ │
│  │ Claude      │    │ MT5 / Binance       │ │
│  │ Gemini      │◄───│ Yahoo Finance       │ │
│  │ DeepSeek    │    │ FRED (macro)        │ │
│  │ FinBERT     │    │ NewsAPI             │ │
│  │ Groq        │    │ CFTC COT            │ │
│  └──────┬──────┘    └─────────────────────┘ │
│         │                                   │
│         ▼                                   │
│  ┌─────────────────────────────────────────┐│
│  │           DATABASE LAYER                ││
│  │  PostgreSQL  │  Redis  │  Qdrant (RAG)  ││
│  └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

---

## Modules Overview

### Analysis (14 modules)
- Full Institutional Analysis Engine
- Multi-Timeframe Confluence Score (M1→MN)
- Market Regime Detector
- Liquidity Map Engine (BSL/SSL/FVG)
- Market Structure Engine (BOS/CHOCH/MSS)
- Session Plan Engine (Asia/London/NY)
- Scenario Builder (Bull/Base/Bear)
- AI Debate Engine (Bull vs Bear)
- Second Opinion Engine
- Session Transition Analyzer
- Volatility Analysis Engine
- Smart Watchlist Engine
- Optimal Entry Timing Engine
- Chart Screenshot Analyzer

### Strategies (30+)
ICT/SMC · Wyckoff · Elliott Wave · VSA · Price Action
Supply & Demand · Momentum · Carry Trade · Seasonal
Tape Reading · Dark Pool · Iceberg Detector · Stop Hunt
Funding Rate Arb · Gamma Squeeze · Market Profile (TPO)
Statistical Mean Reversion · Pairs Trading · Z-Score
Hurst Exponent · Fractal Dimension · Fed Pivot
Inflation Trade · Recession Trade · Dollar Smile
Ensemble · Adaptive · Contra-trend · Delta Divergence

### Risk Engine (10 modules)
- Position Size Calculator (Kelly Criterion)
- Daily Risk Monitor (hard 10% stop)
- Portfolio Risk Engine
- VaR Engine (95%/99%/CVaR)
- Stress Test Engine
- Correlation Guard
- Risk of Ruin Calculator
- Prop Firm Guardian (FTMO/E8/etc)
- Kill Switch (/stop command)
- Psychology Blocker

### Psychological Engine (8 modules)
- Emotional State Detector
- Pre-Trade Protocol (5 questions)
- Morning Mood Check
- Flow State Optimizer
- Behavioral Pattern Detector
- Pause & Recovery System
- Energy/Focus Check
- Trading Constitution Guardian

### Journal Engine (8 modules)
- Full Trade Journal (broker-synced)
- AI Trade Autopsy
- Signal Journal
- Missed Trade Journal
- Shadow Portfolio
- Voice Journal (Whisper transcription)
- Screenshot Journal
- Post-Trade Autopsy Score

### AI Self-Learning
- RAG Knowledge Base (Qdrant)
- Reinforcement Learning Engine
- Pattern Recognition from your trades
- Personal Model Engine
- Historical Backtester
- Adaptive Analysis Engine

---

## Languages & Timezones

**Languages**: English · Русский · Türkçe · العربية (with RTL support)

All AI responses, alerts, reports, and academy materials are in your chosen language.

**Timezones**: All UTC±14 supported
- МСК (UTC+3), GMT (UTC+0), EST (UTC-5)
- TRT (UTC+3), GST (UTC+4), and all others

---

## API Keys Checklist

### Required ($14/month total)
- [ ] `ANTHROPIC_API_KEY` — console.anthropic.com (~$10/mo)
- [ ] Hetzner VPS — hetzner.com (€3.79/mo)

### Free (register once)
- [ ] `GEMINI_API_KEY` — aistudio.google.com
- [ ] `GROQ_API_KEY` — groq.com
- [ ] `MISTRAL_API_KEY` — console.mistral.ai
- [ ] `OPENROUTER_API_KEY` — openrouter.ai
- [ ] `TWELVE_DATA_KEY` — twelvedata.com
- [ ] `ALPHA_VANTAGE_KEY` — alphavantage.co
- [ ] `FRED_API_KEY` — fred.stlouisfed.org/docs/api
- [ ] `NEWS_API_KEY` — newsapi.org
- [ ] `CMC_API_KEY` — coinmarketcap.com/api
- [ ] `HUGGINGFACE_API_KEY` — huggingface.co
- [ ] `DEEPGRAM_KEY` — deepgram.com
- [ ] `POLYGON_API_KEY` — polygon.io
- [ ] `FMP_API_KEY` — financialmodelingprep.com
- [ ] `DEEPSEEK_API_KEY` — platform.deepseek.com
- [ ] `TOGETHER_API_KEY` — together.ai
- [ ] `TAVILY_KEY` — tavily.com
- [ ] `GROQ_API_KEY` — groq.com
- [ ] `LUNARCRUSH_KEY` — lunarcrush.com

### Broker APIs
- [ ] Binance: `BINANCE_API_KEY` + `BINANCE_SECRET`
- [ ] Bybit: `BYBIT_API_KEY` + `BYBIT_SECRET`
- [ ] MT5: `MT5_LOGIN` + `MT5_PASSWORD` + `MT5_SERVER`

### Notifications
- [ ] `TELEGRAM_BOT_TOKEN` — @BotFather
- [ ] `TELEGRAM_ADMIN_ID` — your Telegram ID
- [ ] `SMTP_USER` + `SMTP_PASSWORD` — for email alerts
- [ ] `TWILIO_*` — for WhatsApp/SMS (optional)

---

## Adding API Keys via Dashboard

1. Open Dashboard → Settings → API Hub
2. Find the API in the list
3. Click "Add Key"
4. Paste your key
5. System validates automatically
6. Module activates instantly

No code editing required.

---

## Security

- All API keys encrypted with AES-256 in database
- 2FA via Telegram (code sent on login)
- JWT authentication with 24h expiry
- Zero-knowledge architecture option
- Automatic nightly backup to S3
- Anomaly detection (new IP alert)
- Rate limiting on all endpoints
- HTTPS enforced via Nginx

**Rules:**
- Never share your `.env` file
- Never send API keys in chat
- Binance/Bybit: enable read-only first, then trading
- MT5: use investor password (read-only) first
- Enable 2FA everywhere possible

---

## Useful Commands

```bash
# Start system
docker compose up -d

# Stop system
docker compose down

# View logs
docker compose logs -f

# Restart specific service
docker compose restart backend

# Update system
git pull
docker compose up -d --build

# Database backup
docker compose exec postgres pg_dump -U nexus nexus > backup.sql

# Enter backend shell
docker compose exec backend bash
```

---

## Cost Breakdown

| Stage | Monthly Cost |
|-------|-------------|
| Start (now) | ~$14 |
| Medium (month 2-3) | ~$146 |
| Professional (month 6+) | ~$500 |
| Hedge Fund Level | ~$950 |

Bloomberg Terminal costs $24,000/year.
NEXUS costs $168/year to start.

---

## Support

All questions → Telegram bot: /help
System status → Dashboard → Data Quality
API issues → Dashboard → Settings → API Hub

---

*NEXUS Trading OS — Built for disciplined, systematic trading.*
*The system never trades without your confirmation.*
