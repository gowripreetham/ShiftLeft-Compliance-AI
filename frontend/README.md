# Shift-Left Compliance Dashboard

A modern, real-time compliance monitoring dashboard built with Next.js, React, and TypeScript. This dashboard provides comprehensive visibility into security findings, risk analytics, and compliance trends.

## 🚀 Features

- **Real-time Dashboard**: Live monitoring with auto-refresh every 10 seconds
- **Comprehensive Findings View**: Filterable table of all compliance findings
- **Trend Analysis**: Visual charts showing findings over time
- **Risk Management**: Color-coded risk levels (High, Medium, Low)
- **Integration Status**: Display Jira tickets, GitHub issues, and Slack alerts
- **Modern UI**: Built with shadcn/ui components and Tailwind CSS
- **Toast Notifications**: Alert for new high-risk findings

## 📋 Prerequisites

- Node.js 18+ 
- npm or yarn
- SQLite database (`compliance_memory.db` in parent directory)

## 🛠️ Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Verify the database exists:**
   Make sure `compliance_memory.db` exists in the parent directory (`../compliance_memory.db`)

## 🚀 Running the Application

### Development Mode

```bash
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
npm run build
npm start
```

## 📁 Project Structure

```
frontend/
├── app/                        # Next.js App Router
│   ├── api/                    # API Routes
│   │   ├── findings/          # Findings endpoints
│   │   ├── config/            # Configuration endpoint
│   │   └── trends/            # Trends endpoint
│   ├── findings/              # Findings page
│   ├── trends/                # Trends page
│   ├── settings/              # Settings page
│   ├── layout.tsx             # Root layout
│   ├── page.tsx               # Dashboard (home page)
│   └── globals.css            # Global styles
├── components/                 # React components
│   ├── ui/                    # shadcn/ui components
│   └── Sidebar.tsx            # Navigation sidebar
├── lib/                        # Utilities
│   ├── db.ts                  # Database connection
│   ├── types.ts               # TypeScript types
│   └── utils.ts               # Helper functions
└── package.json               # Dependencies
```

## 🔌 API Endpoints

### Findings
- `GET /api/findings` - Get all findings
- `GET /api/findings/:id` - Get specific finding
- `GET /api/findings/stats` - Get aggregated statistics
- `GET /api/findings/unresolved` - Get open findings
- `POST /api/findings/resolve/:jira_key` - Mark finding as resolved

### Configuration
- `GET /api/config` - Get integration configuration

### Trends
- `GET /api/trends?risk_level={level}` - Get trend data (optional risk filter)

## 🎨 UI Components

The application uses **shadcn/ui** components:
- Card
- Button
- Input
- Select
- Toast
- Label

All components are in `/components/ui/`

## 🔄 Auto-Refresh

The dashboard automatically refreshes data every **10 seconds** using SWR (stale-while-revalidate). This ensures you always see the latest findings without manual refresh.

## 🚨 Notifications

When a new **high-risk** finding is detected, a toast notification will appear in the top-right corner of the screen.

## 🎯 Pages

### Dashboard (`/`)
- Overview cards showing key metrics
- Bar chart of findings by risk level
- Real-time updates

### Findings (`/findings`)
- Searchable table of all findings
- Filter by risk level and resolution status
- Direct links to Jira, GitHub, and Slack
- Mark findings as resolved

### Trends (`/trends`)
- Line chart showing findings over time
- Filter by risk level
- Statistics (total, average, peak)

### Settings (`/settings`)
- Configure Jira, GitHub, and Slack integrations
- View system status
- Test connections

## 🗄️ Database Schema

The application connects to `compliance_memory.db` with the following table:

```sql
CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY,
  timestamp TEXT,
  summary TEXT,
  risk_level TEXT,  -- 'low', 'medium', 'high'
  jira_key TEXT,
  github_link TEXT,
  slack_link TEXT,
  resolved INTEGER  -- 0 = open, 1 = resolved
);
```

## 🎨 Styling

The application uses **Tailwind CSS** with a custom color scheme:
- **High Risk**: Red (`bg-red-100 text-red-800`)
- **Medium Risk**: Yellow (`bg-yellow-100 text-yellow-800`)
- **Low Risk**: Green (`bg-green-100 text-green-800`)

## 🔧 Configuration

Environment variables (optional):
- `JIRA_BASE_URL` - Your Jira instance URL
- `JIRA_PROJECT_KEY` - Default Jira project
- `GITHUB_REPO` - GitHub repository (owner/repo)
- `SLACK_CHANNEL_ID` - Slack channel ID

## 🐛 Troubleshooting

### Database Connection Error
Make sure `compliance_memory.db` exists in the parent directory:
```bash
ls ../compliance_memory.db
```

### Port Already in Use
Change the port in `package.json`:
```json
"dev": "next dev -p 3001"
```

### Module Not Found
Reinstall dependencies:
```bash
rm -rf node_modules package-lock.json
npm install
```

## 📝 Development

### Adding New Components
```bash
npx shadcn-ui@latest add [component-name]
```

### Type Checking
```bash
npm run build
```

### Linting
```bash
npm run lint
```

## 🤝 Contributing

This is part of the GEMINI-HACK project. For issues or contributions, please contact the project maintainer.

## 📄 License

MIT License - see LICENSE file for details

---

**Built with ❤️ using Next.js, React, TypeScript, Tailwind CSS, and shadcn/ui**

