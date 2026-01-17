# Supabase Setup Guide

Complete guide for setting up Supabase for the NexHacks Polymarket Correlation Tool.

## Table of Contents
1. [Why Supabase?](#why-supabase)
2. [Create Supabase Account](#create-supabase-account)
3. [Create a New Project](#create-a-new-project)
4. [Get Your Credentials](#get-your-credentials)
5. [Configure Environment](#configure-environment)
6. [Install Dependencies](#install-dependencies)
7. [Create Database Schema](#create-database-schema)
8. [Test Connection](#test-connection)
9. [Troubleshooting](#troubleshooting)

---

## Why Supabase?

- **PostgreSQL Database** - Powerful, reliable SQL database
- **Free Tier** - Generous free tier perfect for hackathons
- **Easy Setup** - No complex configuration needed
- **REST API** - Built-in REST API for your database
- **Real-time** - Real-time subscriptions (bonus feature)
- **Dashboard** - Beautiful web interface to manage your data

---

## Create Supabase Account

1. Go to [Supabase](https://supabase.com/)
2. Click **"Start your project"** or **"Sign Up"**
3. Sign up with GitHub, Google, or email
4. Verify your email if required

---

## Create a New Project

1. After logging in, click **"New Project"**
2. Fill in project details:
   - **Name**: `nexhacks-polymarket` (or your preferred name)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to you
   - **Pricing Plan**: Select **"Free"** tier
3. Click **"Create new project"**
4. Wait 2-3 minutes for project to be created

---

## Get Your Credentials

1. In your Supabase project dashboard, click **"Settings"** (gear icon) in the left sidebar
2. Click **"API"** under Project Settings
3. You'll see two important values:

   **Project URL:**
   ```
   https://xxxxxxxxxxxxx.supabase.co
   ```

   **anon public key:**
   ```
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4eHh4eHh4eHh4eHh4eHgiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTY0NTk2ODAwMCwiZXhwIjoxOTYxNTQ0MDAwfQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

4. **Copy both values** - you'll need them for your `.env` file

---

## Configure Environment

Create or update your `.env` file in the project root:

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Database Name (optional, for reference)
DATABASE_NAME=nexhacks_polymarket
```

**Replace:**
- `SUPABASE_URL` with your Project URL
- `SUPABASE_ANON_KEY` with your anon public key

---

## Install Dependencies

Install the Supabase Python client:

```bash
pip install supabase python-dotenv
```

---

## Create Database Schema

1. Go to your Supabase dashboard
2. Click **"SQL Editor"** in the left sidebar
3. Click **"New query"**
4. Open the file `database/schema.sql` in your project
5. **Copy the entire contents** of `schema.sql`
6. **Paste it into the SQL Editor**
7. Click **"Run"** (or press Ctrl+Enter)
8. You should see: "Success. No rows returned"

This creates all 6 tables:
- `markets` - Polymarket market data
- `user_trades` - User trading history
- `trade_correlations` - Calculated correlations
- `related_trades` - Related/pairs trading opportunities
- `parlay_suggestions` - Parlay recommendations
- `hedge_opportunities` - Hedge suggestions

---

## Test Connection

Run the test script:

```bash
python database/test_connection.py
```

You should see:
```
Testing Supabase connection...
[OK] Supabase client created
[OK] Successfully connected to Supabase
[OK] Markets table accessible

[SUCCESS] Connection test successful! Supabase is ready to use.
```

---

## Verify Tables Were Created

Run the initialization check:

```bash
python database/init_db.py
```

This will show which tables exist and which are missing.

---

## Quick Start Checklist

- [ ] Created Supabase account
- [ ] Created new project
- [ ] Copied Project URL and anon key
- [ ] Added credentials to `.env` file
- [ ] Installed dependencies: `pip install supabase python-dotenv`
- [ ] Ran SQL schema in Supabase SQL Editor
- [ ] Tested connection: `python database/test_connection.py`
- [ ] Verified tables: `python database/init_db.py`

---

## Troubleshooting

### Connection Issues

**Problem**: `Missing Supabase credentials`
- **Solution**: Check your `.env` file has `SUPABASE_URL` and `SUPABASE_ANON_KEY`

**Problem**: `Invalid API key`
- **Solution**: Make sure you copied the **anon public key**, not the service_role key

**Problem**: `Table does not exist`
- **Solution**: Run the SQL schema in Supabase SQL Editor (see [Create Database Schema](#create-database-schema))

### SQL Schema Issues

**Problem**: `relation already exists`
- **Solution**: Tables already exist, this is OK. You can ignore the error or drop tables first.

**Problem**: `permission denied`
- **Solution**: Make sure you're running SQL in the SQL Editor, not trying to create tables via API

### General Tips

1. **Always use the anon key** for client-side code (not service_role key)
2. **Keep your database password safe** - you'll need it if you connect via psql
3. **Use the SQL Editor** for schema changes and migrations
4. **Check the Supabase dashboard** to view your data visually

---

## Next Steps

After successful setup:
1. ✅ Read [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) to understand the data structure
2. ✅ Read [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) for usage examples
3. ✅ Import your Polymarket CSV data into the `markets` table
4. ✅ Start building correlation algorithms

---

## Quick Reference

### Connection String Format

```python
from supabase import create_client

supabase = create_client(
    "https://your-project.supabase.co",
    "your-anon-key"
)
```

### Common Commands

```bash
# Test connection
python database/test_connection.py

# Check tables
python database/init_db.py

# View data in Supabase dashboard
# Go to: Table Editor in left sidebar
```

---

## Support

For issues:
1. Check [Troubleshooting](#troubleshooting) section above
2. Review Supabase documentation: https://supabase.com/docs
3. Check Supabase dashboard for error messages
