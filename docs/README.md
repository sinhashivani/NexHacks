# Documentation Index

Complete documentation for the NexHacks Polymarket Correlation Tool.

## 📚 Documentation Files

### 0. [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) ⭐ **START HERE**
**Project context and overview** - Use this to understand what we're building.
- Problem statement
- Solution overview
- Features and capabilities
- Tech stack
- Current status
- Next steps

**When to use**: Sharing project context, onboarding, understanding the big picture

---

### 1. [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)
**Start here!** Complete setup guide for Supabase.
- Create Supabase account
- Create new project
- Get credentials
- Configure environment
- Create database schema
- Test connection

**When to use**: First time setup, connection issues, environment configuration

---

### 2. [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)
Complete database schema documentation.
- All 6 tables explained
- Field definitions and types
- Indexes and their purposes
- Example records
- Relationships between tables

**When to use**: Understanding data structure, designing queries, adding new fields

---

### 3. [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)
Code examples and implementation patterns.
- Connection setup
- CRUD operations
- Market data operations
- User trade operations
- Correlation operations
- Query examples
- Advanced patterns

**When to use**: Writing code, implementing features, learning patterns

---

### 4. [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
Quick reference cheat sheet.
- Common operations
- Query syntax
- Code snippets
- Table names
- Field types

**When to use**: Quick lookups, copy-paste code snippets, syntax reminders

---

## 🚀 Quick Start

1. **Understand the Project** → Read [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)
2. **Setup Supabase** → Read [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)
3. **Understand Schema** → Read [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)
4. **Start Coding** → Use [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)
5. **Quick Lookups** → Reference [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)

---

## 📋 Database Overview

**Database**: PostgreSQL (via Supabase)

**Tables**:
1. `markets` - Polymarket market data
2. `user_trades` - User trading history
3. `trade_correlations` - Calculated correlations
4. `related_trades` - Related/pairs trading opportunities
5. `parlay_suggestions` - Parlay recommendations
6. `hedge_opportunities` - Hedge suggestions

---

## 🎯 Common Tasks

### Setting Up for First Time
1. Follow [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) Step 1-7
2. Run SQL schema in Supabase SQL Editor
3. Test connection: `python database/test_connection.py`
4. Import CSV data (see Implementation Guide)

### Adding a New Field
1. Check [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) for table structure
2. Update schema documentation
3. Add migration SQL if needed

### Writing a Query
1. Check [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for syntax
2. See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) for examples
3. Verify indexes in [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)

### Troubleshooting
1. Check [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) Troubleshooting section
2. Verify credentials in `.env` file
3. Check table indexes in Supabase dashboard

---

## 📝 Notes

- All credentials should be in `.env` file (never commit to git)
- Use indexes for frequently queried fields
- Always use `NOW()` or `datetime.utcnow()` for timestamps
- Test connections before running full application
- Use Supabase SQL Editor for schema changes

---

## 🔗 Related Files

- `database/supabase_connection.py` - Connection handler
- `database/schema.sql` - Database schema SQL
- `database/init_db.py` - Database initialization check
- `.env` - Environment variables

---

## 💡 Tips

1. **Use Supabase dashboard** to view and manage data visually
2. **Use SQL Editor** for schema changes and migrations
3. **Use anon key** for client-side code (not service_role)
4. **Check Supabase logs** for debugging queries
5. **Use the Table Editor** in dashboard to manually inspect data

---

For questions or issues, refer to the specific documentation file or check the troubleshooting sections.
