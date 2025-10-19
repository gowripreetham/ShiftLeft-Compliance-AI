# 🚀 Quick Start Guide

## Get Running in 3 Steps

### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 2: Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

Or manually:
```bash
npm install
```

### Step 3: Start Development Server
```bash
npm run dev
```

### Step 4: Open in Browser
Visit: **http://localhost:3000**

---

## 🎯 What You'll See

### Dashboard (Home)
- Real-time statistics cards
- Bar chart of findings by risk level
- Auto-refresh every 10 seconds

### Findings Page
- Complete table of all security findings
- Search and filter capabilities
- Direct links to Jira, GitHub, Slack
- Mark findings as resolved

### Trends Page
- Line chart showing findings over time
- Filter by risk level
- Statistics (total, average, peak)

### Settings Page
- Configure integrations
- View system status
- Test connections

---

## 📋 Requirements Checklist

- ✅ Node.js 18+ installed
- ✅ `compliance_memory.db` exists in parent directory
- ✅ Port 3000 available

---

## 🐛 Troubleshooting

### Port 3000 Already in Use
```bash
npm run dev -- -p 3001
```

### Database Not Found
Make sure `compliance_memory.db` exists:
```bash
ls ../compliance_memory.db
```

### Module Errors
```bash
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 More Information

- **Full Documentation**: See `README.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **API Reference**: See `README.md` API Endpoints section

---

## 🎉 You're All Set!

The dashboard is now running and ready to monitor your compliance findings in real-time.

Happy monitoring! 🛡️

