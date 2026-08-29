# PO Assistant — Step 1: Multi-tenant backend skeleton

## ⚠️ First: rotate your Supabase secret key
You pasted your live `SUPABASE_SECRET_KEY` into a chat earlier. Go to
Supabase Dashboard → Project Settings → API → regenerate the secret key,
then use the *new* value below. Never commit this key to git or share it
in chat again — it has full read/write access to your database, bypassing
all security rules.

## Setup

1. Create `.env` from the template:
   ```bash
   cp .env.example .env
   ```
   Fill in your (rotated) Supabase values and your Groq API key.

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the database schema:
   Open the Supabase SQL editor and run `supabase/schema.sql`. This creates:
   - `organizations` — one row per customer company (tenant)
   - `profiles` — links each login to an organization
   - `purchase_orders` — the PO data itself, tagged with `org_id`

4. Manually create a test organization + link your user to it (until
   Step 3 adds a signup flow):
   ```sql
   insert into organizations (name) values ('Test Company') returning id;
   -- copy the returned id, then:
   insert into profiles (id, org_id, role)
   values ('<your-supabase-auth-user-id>', '<org-id-from-above>', 'owner');
   ```

5. Run the API:
   ```bash
   uvicorn app.main:app --reload
   ```

## What's in this step

- `app/auth.py` — verifies the Supabase JWT sent by the frontend and
  resolves which organization (tenant) the logged-in user belongs to.
- `app/core/engine.py` — your original script's logic, refactored to
  pull data from the database instead of a local `.xlsx` path, scoped
  to the caller's org, now calling **Mistral** (`mistral-large-latest`)
  instead of Groq.
- `app/routers/po.py` — `POST /po/upload` lets a customer upload an
  `.xlsx` to populate their org's data (fallback until Sheets/ERP sync
  is added).
- `app/routers/chat.py` — `POST /chat` answers a question against the
  caller's own PO data only.
- `supabase/schema.sql` — multi-tenant schema with RLS as defense-in-depth.
- `frontend/index.html` — a single-file frontend: Supabase email/password
  login, file upload, and a chat interface. Open it directly in a browser
  (no build step). Before using it, edit the three config lines at the top
  of the `<script>` block:
  - `SUPABASE_URL` — your Supabase project URL
  - `SUPABASE_PUBLISHABLE_KEY` — your Supabase **publishable** key (safe for
    frontend use — this is different from the secret key, never put the
    secret key here)
  - `API_BASE` — where your FastAPI backend is running (e.g.
    `http://localhost:8000` locally)

  Test users need a password set — either invite them via the Supabase
  dashboard (Authentication → Users → Add user) or use
  `sb.auth.signUp()` once to bootstrap your own test account, then link
  it to an org via the SQL in step 4 above.

## Not yet built (next steps)

- **Step 2**: Google Sheets auto-sync (scheduled pull instead of manual upload)
- **Step 3**: Signup flow (currently orgs/profiles are created manually via SQL)
- **Step 4**: Usage limits / billing (e.g. Stripe metered billing per org)
- **Step 5**: Deployment (e.g. Fly.io / Railway for the API, Vercel/Netlify or
  just static hosting for the frontend)
