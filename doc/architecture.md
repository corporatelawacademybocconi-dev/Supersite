Corporate Law Academy

Application Architecture

Purpose

Corporate Law Academy is an editorial and professional-development platform focused on corporate law, finance, technology, governance, and commercial practice.

The platform is designed around five core content pillars:

1. Articles
2. Journal
3. Events
4. Podcast
5. People

The current implementation uses Flask, Jinja templates, and static CSS. Future content management will be powered by Supabase/Postgres and an internal administrative interface.

⸻

Information Architecture

Public Navigation

Home

About

Our Work

* Articles
* Journal
* Events
* Moot Court
* Podcast

Networking

Contact

⸻

Route Architecture

Core Pages

/
About

/about

Our Work

/our-work

Networking

/networking

Contact

/contact

⸻

Articles

Article Library

/articles

Individual Article

/articles/

⸻

People

People Directory

/people

Individual Profile

/people/

⸻

Journal

Journal Landing Page

/journal

Journal Edition

/journal/

⸻

Events

Events Landing Page

/events

Individual Event

/events/

⸻

Podcast

Podcast Landing Page

/podcast

⸻

Core Content Entities

The application is built around the following entities:

* People
* Articles
* Journal Editions
* Events
* Podcast Episodes
* Tags

Relationships are defined separately below.
---

# Data Model

The future backend will use Supabase/Postgres.

The database should support imported Wix articles, articles created through the site editor, author profiles, article tags, view counts, journal editions, events, and podcast episodes.

The frontend templates are already designed to consume this data dynamically later.

---

## 1. People

People represent authors, contributors, team members, speakers, and editors.

### Table: people

Fields:

- id
- name
- slug
- role
- bio
- image_url
- linkedin_url
- email
- is_author
- is_team_member
- created_at
- updated_at

### Relationships

One person can write many articles.

One person can appear as an event speaker.

One person can be linked to journal contributions.

---

## 2. Articles

Articles represent standard editorial content, including imported Wix posts and articles created through the future site editor.

### Table: articles

Fields:

- id
- title
- slug
- excerpt
- content
- cover_image_url
- author_id
- category
- status
- is_featured
- source
- wix_original_id
- published_at
- created_at
- updated_at

### Notes

`source` identifies where the article came from.

Possible values:

- wix_import
- site_editor

`status` controls publication state.

Possible values:

- draft
- published
- archived

### Relationships

Each article belongs to one author.

Each article can have many tags.

Each article can belong to one journal edition if used as a journal contribution.

Each article can have many view records.

---

## 3. Tags

Tags classify articles by topic.

### Table: tags

Fields:

- id
- name
- slug
- created_at

---

## 4. Article Tags

This table creates a many-to-many relationship between articles and tags.

### Table: article_tags

Fields:

- article_id
- tag_id

---

## 5. Article Views

Article views track article engagement.

### Table: article_views

Fields:

- id
- article_id
- viewed_at
- visitor_hash

### Notes

The sitewide article view counter can be calculated from this table.

Do not build this immediately. It belongs after dynamic article rendering works.

---

## 6. Journal Editions

Journal editions represent formal CLA journal publications.

### Table: journal_editions

Fields:

- id
- title
- slug
- edition_number
- theme
- cover_image_url
- editor_note
- publication_date
- status
- created_at
- updated_at

### Relationships

One journal edition can contain many articles.

---

## 7. Journal Articles

This table links articles to journal editions.

### Table: journal_articles

Fields:

- journal_edition_id
- article_id
- display_order

### Notes

Journal contributions should remain article records.

Do not embed journal articles directly inside the journal edition table. That would be a neat little trap for future search, author pages, and view counts.

---

## 8. Events

Events represent talks, workshops, panels, networking sessions, and competitions.

### Table: events

Fields:

- id
- title
- slug
- description
- event_type
- location
- start_time
- end_time
- status
- is_featured
- image_url
- registration_url
- created_at
- updated_at

### Status Values

- upcoming
- completed
- cancelled

---

## 9. Podcast Episodes

Podcast episodes will eventually be synced from Spotify and cached in Supabase.

### Table: podcast_episodes

Fields:

- id
- spotify_id
- title
- description
- episode_url
- cover_image_url
- duration
- published_at
- created_at
- updated_at

### Notes

Spotify remains the source of truth.

Supabase acts as a cache so the website does not rely on repeated live Spotify calls.




⸻

Relationships & Content Flow

Entity Relationships

People → Articles

One Person

↓

Many Articles

Relationship:

people.id → articles.author_id

⸻

Articles → Tags

One Article

↓

Many Tags

Relationship:

articles.id → article_tags.article_id

tags.id → article_tags.tag_id

⸻

Journal Editions → Articles

One Journal Edition

↓

Many Articles

Relationship:

journal_editions.id → journal_articles.journal_edition_id

articles.id → journal_articles.article_id

⸻

Articles → Views

One Article

↓

Many Views

Relationship:

articles.id → article_views.article_id

⸻

Content Flow

Articles

Content Sources:

1. Wix Import
2. Internal Site Editor

Both sources create records in the articles table.

Flow:

Content Source

↓

articles

↓

Article Page

↓

Author Profile

↓

Related Content

⸻

Journal

Journal editions act as collections of articles.

Flow:

Journal Edition

↓

Journal Articles

↓

Individual Article Pages

Each journal contribution remains an article record.

Benefits:

* Searchable
* Attributable to authors
* Supports view counts
* Supports tags
* Supports related articles

⸻

Events

Flow:

Event Record

↓

Events Page

↓

Event Detail Page

↓

Archive

Events should be categorized as:

* Featured
* Upcoming
* Completed

⸻

Podcast

Flow:

Spotify

↓

Metadata Sync

↓

podcast_episodes

↓

Podcast Page

Spotify remains the source of truth.

The database stores cached metadata for performance and display.

⸻

Future Search Scope

Search should eventually index:

* Article titles
* Article content
* Tags
* Authors

Search should NOT initially include:

* Events
* Podcast episodes

These can be added later if needed.

⸻

Future Analytics

Metrics to support:

* Total article views
* Most viewed articles
* Most viewed authors
* Journal readership

Analytics should remain lightweight during the first release.