#!/usr/bin/env node
/**
 * Wix → Supabase article importer
 * 
 * Usage:
 *   npm install @supabase/supabase-js csv-parse
 *   node import-from-wix.js your-wix-export.csv
 * 
 * How to export from Wix:
 *   Wix Dashboard → Blog → Posts → ⋯ menu → Export posts (CSV)
 * 
 * The script maps Wix columns to your Supabase schema and imports
 * all articles in batches of 20.
 */

const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse/sync');
const { createClient } = require('@supabase/supabase-js');

// ─── CONFIGURE THESE ──────────────────────────────────────────────────────────
const SUPABASE_URL   = 'https://YOUR_PROJECT.supabase.co';
const SUPABASE_KEY   = 'YOUR_SERVICE_ROLE_KEY'; // use service role for import
// ─────────────────────────────────────────────────────────────────────────────

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// ─── WIX COLUMN MAP ───────────────────────────────────────────────────────────
// Adjust these if your Wix export uses different column names.
// Run `node import-from-wix.js your-file.csv --show-columns` to see actual columns.
const COL_TITLE    = 'title';          // article title
const COL_BODY     = 'plainContent';   // full text (or 'content' / 'body')
const COL_AUTHOR   = 'owner';          // author name
const COL_DATE     = 'firstPublishedDate'; // ISO date string
const COL_TAGS     = 'tags';           // comma-separated tags (used as category)
const COL_EXCERPT  = 'excerpt';        // short description

function mapRow(row) {
  // Pick the first tag as the category, default to 'Uncategorised'
  const rawTags = row[COL_TAGS] || '';
  const category = rawTags.split(',')[0].trim() || 'Uncategorised';

  // Clean body text — strip HTML tags if present
  const rawBody = row[COL_BODY] || '';
  const body = rawBody.replace(/<[^>]+>/g, '').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').trim();

  // Generate excerpt from body if not present
  const excerpt = (row[COL_EXCERPT] || body.slice(0, 280)).trim();

  // Parse date — fallback to today
  let date;
  try { date = new Date(row[COL_DATE]).toISOString().split('T')[0]; }
  catch { date = new Date().toISOString().split('T')[0]; }

  return {
    title:    (row[COL_TITLE] || 'Untitled').trim(),
    author:   (row[COL_AUTHOR] || 'Unknown').trim(),
    date,
    category,
    excerpt,
    body: body || excerpt,
  };
}

async function run() {
  const csvPath = process.argv[2];
  if (!csvPath) {
    console.error('Usage: node import-from-wix.js <path-to-csv>');
    process.exit(1);
  }

  const raw = fs.readFileSync(path.resolve(csvPath), 'utf8');
  const rows = parse(raw, { columns: true, skip_empty_lines: true, trim: true });

  if (process.argv.includes('--show-columns')) {
    console.log('Columns in your CSV:', Object.keys(rows[0] || {}));
    process.exit(0);
  }

  console.log(`Found ${rows.length} rows in CSV.`);

  const articles = rows.map(mapRow).filter(a => a.title && a.body);
  console.log(`${articles.length} valid articles after filtering.`);

  // Import in batches of 20
  const BATCH = 20;
  let imported = 0;
  let failed = 0;

  for (let i = 0; i < articles.length; i += BATCH) {
    const batch = articles.slice(i, i + BATCH);
    const { error } = await supabase.from('articles').insert(batch);
    if (error) {
      console.error(`Batch ${Math.floor(i/BATCH)+1} failed:`, error.message);
      failed += batch.length;
    } else {
      imported += batch.length;
      console.log(`Imported ${imported}/${articles.length}…`);
    }
  }

  console.log(`\nDone. ${imported} articles imported, ${failed} failed.`);
  if (failed > 0) {
    console.log('Check the error messages above. You can re-run the script safely — add a unique constraint on title+date in Supabase to prevent duplicates.');
  }
}

run().catch(e => { console.error(e); process.exit(1); });
