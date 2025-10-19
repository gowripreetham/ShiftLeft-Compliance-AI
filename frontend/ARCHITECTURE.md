# 🏗️ Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │Dashboard │  │Findings  │  │  Trends  │  │ Settings │       │
│  │   Page   │  │   Page   │  │   Page   │  │   Page   │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND COMPONENTS                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  shadcn/ui Components (Card, Button, Input, Select, etc) │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Recharts (Bar Chart, Line Chart)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SWR (Data Fetching with Auto-refresh)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API ROUTES (Next.js)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  /api/findings          - GET all findings               │  │
│  │  /api/findings/:id      - GET single finding             │  │
│  │  /api/findings/stats    - GET statistics                 │  │
│  │  /api/findings/unresolved - GET open findings            │  │
│  │  /api/findings/resolve/:jira_key - POST resolve          │  │
│  │  /api/config            - GET configuration              │  │
│  │  /api/trends            - GET trend data                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  better-sqlite3 (SQLite Driver)                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  compliance_memory.db                              │  │  │
│  │  │  ┌──────────────────────────────────────────────┐  │  │  │
│  │  │  │  audit_log table                             │  │  │  │
│  │  │  │  - id, timestamp, summary                    │  │  │  │
│  │  │  │  - risk_level, jira_key                      │  │  │  │
│  │  │  │  - github_link, slack_link, resolved         │  │  │  │
│  │  │  └──────────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     SHIFT-LEFT WORKFLOW                          │
└─────────────────────────────────────────────────────────────────┘

1. CAPTURE
   ┌─────────────┐
   │ Developer   │
   │ Commits Code│
   └──────┬──────┘
          │
          ▼
   ┌─────────────────┐
   │ capture_commit  │
   │     .py         │
   └────────┬────────┘
            │
            ▼
2. ANALYZE
   ┌────────────────────┐
   │ analyze_with_      │
   │ gemini.py          │
   │ (Gemini AI)        │
   └────────┬───────────┘
            │
            ▼
3. ACT
   ┌────────────────────┐
   │ fetch_jira_agent   │
   │      .py           │
   │ - Create Jira      │
   │ - Create GitHub    │
   │ - Send Slack       │
   └────────┬───────────┘
            │
            ▼
4. MEMORIZE
   ┌────────────────────┐
   │ compliance_memory  │
   │     .db            │
   │ (SQLite)           │
   └────────┬───────────┘
            │
            ▼
5. DISPLAY
   ┌────────────────────┐
   │  Dashboard         │
   │  (This App)        │
   │  - Real-time       │
   │  - Charts          │
   │  - Analytics       │
   └────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                        TECH STACK                                │
└─────────────────────────────────────────────────────────────────┘

FRONTEND
├── Framework: Next.js 14 (App Router)
├── Language: TypeScript 5
├── UI Library: React 18
├── Styling: Tailwind CSS 3
├── Components: shadcn/ui
├── Charts: Recharts
└── Data Fetching: SWR

BACKEND
├── API: Next.js API Routes
├── Database: SQLite (better-sqlite3)
└── ORM: Raw SQL queries

TOOLS
├── Build: Next.js Build System
├── Linting: ESLint
├── Type Checking: TypeScript
└── Package Manager: npm
```

## Component Hierarchy

```
app/layout.tsx
├── Sidebar (Navigation)
└── Main Content
    ├── Dashboard (app/page.tsx)
    │   ├── StatCards (5 cards)
    │   └── BarChart (Recharts)
    │
    ├── Findings (app/findings/page.tsx)
    │   ├── Filters (Search, Risk, Status)
    │   └── FindingsTable
    │
    ├── Trends (app/trends/page.tsx)
    │   ├── Filter (Risk Level)
    │   ├── LineChart (Recharts)
    │   └── StatCards (3 cards)
    │
    └── Settings (app/settings/page.tsx)
        ├── ConfigForm
        ├── SystemStatus
        └── About
```

## API Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER                                │
└─────────────────────────────────────────────────────────────────┘

/api/findings
├── GET /api/findings
│   └── Returns: AuditLog[]
│
├── GET /api/findings/:id
│   └── Returns: AuditLog
│
├── GET /api/findings/stats
│   └── Returns: { stats, riskStats }
│
├── GET /api/findings/unresolved
│   └── Returns: AuditLog[]
│
└── POST /api/findings/resolve/:jira_key
    └── Returns: { success, message }

/api/config
└── GET /api/config
    └── Returns: Config

/api/trends
└── GET /api/trends?risk_level={level}
    └── Returns: TrendData[]
```

## State Management

```
┌─────────────────────────────────────────────────────────────────┐
│                      STATE MANAGEMENT                            │
└─────────────────────────────────────────────────────────────────┘

SWR (Stale-While-Revalidate)
├── Auto-refresh: 10 seconds
├── Caching: Automatic
├── Revalidation: On focus, on interval
└── Error handling: Built-in

Local State (useState)
├── Search term
├── Filters (risk level, status)
├── Form inputs
└── UI state

Toast Notifications
├── New high-risk finding
├── Success messages
├── Error messages
└── Info messages
```

## File Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── api/                  # API Routes
│   │   ├── findings/        # Findings endpoints
│   │   ├── config/          # Config endpoint
│   │   └── trends/          # Trends endpoint
│   ├── findings/            # Findings page
│   ├── trends/              # Trends page
│   ├── settings/            # Settings page
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Dashboard
│   └── globals.css          # Global styles
│
├── components/               # React components
│   ├── ui/                  # shadcn/ui components
│   └── Sidebar.tsx          # Navigation
│
├── lib/                      # Utilities
│   ├── db.ts                # Database connection
│   ├── types.ts             # TypeScript types
│   └── utils.ts             # Helper functions
│
└── [config files]           # Configuration
```

## Security Considerations

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                             │
└─────────────────────────────────────────────────────────────────┘

1. Input Validation
   ├── TypeScript types
   ├── SQL parameterization
   └── Form validation

2. SQL Injection Prevention
   ├── Parameterized queries
   └── Input sanitization

3. XSS Prevention
   ├── React's built-in escaping
   └── Sanitized user input

4. CORS
   └── Same-origin policy

5. Environment Variables
   └── Sensitive data in .env.local
```

## Performance Optimizations

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE FEATURES                          │
└─────────────────────────────────────────────────────────────────┘

1. Data Fetching
   ├── SWR caching
   ├── Stale-while-revalidate
   └── Automatic revalidation

2. Rendering
   ├── React Server Components
   ├── Client-side hydration
   └── Code splitting

3. Database
   ├── SQLite (fast, embedded)
   ├── Indexed queries
   └── Efficient SQL

4. Assets
   ├── Optimized images
   ├── CSS-in-JS (Tailwind)
   └── Tree shaking
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT OPTIONS                            │
└─────────────────────────────────────────────────────────────────┘

Option 1: Vercel (Recommended)
├── Zero-config deployment
├── Automatic builds
├── Edge functions
└── CDN distribution

Option 2: Self-hosted
├── Docker container
├── Node.js server
└── Reverse proxy (nginx)

Option 3: Cloud Platforms
├── AWS (Amplify, EC2)
├── Google Cloud (App Engine)
└── Azure (App Service)
```

---

**Architecture Status**: ✅ Complete and Production-Ready

