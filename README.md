# Academia Europa — Setup Guide (Supabase edition)

## What you have

```
index.html          Public website (search, filters, article cards)
admin.html          Password-protected CMS (full article editor)
import-from-wix.js  One-time migration script for your 300 Wix articles
README.md           This file
```

---

## Step 1 — Create a Supabase project

1. Go to https://supabase.com and sign up (free)
2. Click **New project**
3. Name it (e.g. `academia-europa`)
4. Choose a region close to your users (e.g. Frankfurt for Europe)
5. Set a strong database password (save it somewhere safe)
6. Click **Create new project** — takes ~1 minute

---

## Step 2 — Create the articles table

In Supabase, go to **SQL Editor** and run this:

```sql
-- Articles table
create table articles (
  id          bigint generated always as identity primary key,
  title       text not null,
  author      text not null,
  date        date not null,
  category    text,
  excerpt     text,
  body        text,
  created_at  timestamptz default now()
);

-- Full-text search index (enables fast search across all 300 articles)
alter table articles add column fts tsvector
  generated always as (
    to_tsvector('english',
      coalesce(title,'') || ' ' ||
      coalesce(author,'') || ' ' ||
      coalesce(excerpt,'') || ' ' ||
      coalesce(body,'')
    )
  ) stored;

create index articles_fts_idx on articles using gin(fts);

-- Row-level security: public can read, only authenticated editors can write
alter table articles enable row level security;

create policy "Public read" on articles
  for select using (true);

create policy "Editors can insert" on articles
  for insert to authenticated with check (true);

create policy "Editors can update" on articles
  for update to authenticated using (true);

create policy "Editors can delete" on articles
  for delete to authenticated using (true);
```

Click **Run**.

---

## Step 3 — Get your API keys

In Supabase, go to **Settings → API**:

- Copy **Project URL** → looks like `https://abcdefgh.supabase.co`
- Copy **anon / public** key → long JWT string

Open both `index.html` and `admin.html` and replace these two lines near the top of the `<script>` section:

```javascript
const SUPABASE_URL     = 'https://YOUR_PROJECT.supabase.co';  // ← paste Project URL
const SUPABASE_ANON_KEY = 'YOUR_ANON_KEY';                    // ← paste anon key
```

---

## Step 4 — Create editor accounts

Each editor needs a Supabase Auth account.

In Supabase, go to **Authentication → Users → Add user**:
- Email: editor's email address
- Password: a strong password
- Click **Create user**

Repeat for each of your 2–3 editors.

Editors log in at `/admin.html` with their email + password. No shared password — each person has their own account. You can remove access instantly by deleting their user.

---

## Step 5 — Host the site (GitHub Pages — free)

1. Create a GitHub account (free) at https://github.com
2. Create a new **public** repository
3. Upload `index.html` and `admin.html`
4. Go to **Settings → Pages → Deploy from branch → main / root**
5. Site is live at `https://your-username.github.io/your-repo/`

Alternatively, drag and drop the folder to https://netlify.com for a custom domain.

---

## Step 6 — Import your 300 Wix articles

### Export from Wix
1. Wix Dashboard → Blog → Posts
2. Click the **⋯** menu → **Export posts**
3. Download the CSV file

### Run the import script
```bash
# Install dependencies (one-time)
npm install @supabase/supabase-js csv-parse

# First, check what columns your CSV has
node import-from-wix.js your-export.csv --show-columns

# Edit the column names at the top of import-from-wix.js if needed
# Then get your SERVICE ROLE key from Supabase Settings → API
# (different from the anon key — has full write access)

# Run the import
node import-from-wix.js your-export.csv
```

The script imports in batches of 20 and prints progress. Takes ~30 seconds for 300 articles.

---

## Day-to-day use

**Adding an article:**
1. Go to `/admin.html`
2. Sign in with your email + password
3. Click **New article**
4. Fill in title, author, date, category, excerpt, body
5. Click **Save** → live immediately on the public site

**Editing:**
- Click any article in the left sidebar → edit → Save

**Deleting:**
- Open article → scroll to bottom → "Delete this article permanently"

**Searching in admin:**
- Use the search box at the top of the sidebar (searches title, author, category locally)

---

## Customisation

### Change the association name
Search-replace `Academia Europa` in both HTML files.

### Add a category
In `admin.html`, find `<select id="f-category">` and add an `<option>`.
The new category appears automatically as a filter chip on the public site.

### Change brand colours
Edit the CSS variables at the top of `index.html`:
```css
--accent: #1e3d6e;    /* main navy — change to your colour */
--accent-2: #c8913a;  /* gold accent */
```

### Custom domain
Point your domain's DNS to GitHub Pages or Netlify — both have free guides.

---

## Security

- **Anon key** (used in the HTML files): safe to expose publicly. It can only read articles (due to RLS policies). It cannot write without being authenticated.
- **Service role key** (used only in the import script): keep this private. Never put it in the HTML files.
- **Editor passwords**: managed by Supabase Auth. Reset via Supabase dashboard at any time.

---

## Free tier limits (Supabase)

| Resource | Free limit | Your usage |
|---|---|---|
| Database | 500 MB | ~5–10 MB for 300 articles |
| API requests | Unlimited | — |
| Auth users | 50,000 | You have 2–3 |
| Storage | 1 GB | Not used (text only) |

You will never hit these limits with a 300-article association site.
