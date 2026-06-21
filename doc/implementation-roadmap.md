Corporate Law Academy

Implementation Roadmap

Project Status

Corporate Law Academy has completed its initial frontend architecture and design phase.

The website currently operates as a static Flask/Jinja application with a fully defined design system and information architecture.

The objective of the next phases is to transform the platform from a static website into a dynamic editorial and professional-development platform powered by Supabase/Postgres.

⸻

Phase 1 – Frontend Design

Status: Completed

Objectives

* Establish visual identity
* Define information architecture
* Create reusable design system
* Build static page templates

Deliverables

Completed pages:

* Homepage
* About
* Our Work
* Articles
* Journal
* Events
* Podcast
* Networking
* Contact
* Moot Court

Completed components:

* Navigation
* Footer
* Hero system
* Page hero system
* Cards
* Buttons
* Grid layouts
* Article cards
* Event cards
* Team cards

Outcome:

The platform has a stable visual language and consistent user experience.

⸻

Phase 2 – Application Architecture

Status: Completed

Objectives

Define the future application structure before backend implementation.

Deliverables

Completed:

* Route architecture
* Content architecture
* Entity relationships
* Content flow design
* Future database specification

Core entities defined:

* People
* Articles
* Tags
* Article Views
* Journal Editions
* Events
* Podcast Episodes

Outcome:

The platform architecture is documented and ready for implementation.

⸻

Phase 3 – Supabase Foundation

Status: Planned

Objectives

Create the backend foundation.

Deliverables

Create Supabase project.

Create database tables:

* people
* articles
* tags
* article_tags
* article_views
* journal_editions
* journal_articles
* events
* podcast_episodes

Create relationships.

Configure environment variables.

Connect Flask to Supabase.

Success Criteria

The application can retrieve data from Supabase.

No frontend changes required.

⸻

Phase 4 – Dynamic Articles

Status: Planned

Objectives

Replace hardcoded article content with dynamic article records.

Deliverables

Dynamic article listing page:

/articles

Dynamic article detail page:

/articles/

Article retrieval from Supabase.

Featured article support.

Author integration.

Tag integration.

Success Criteria

Articles are fully database-driven.

No hardcoded article content remains.

⸻

Phase 5 – Wix Migration

Status: Planned

Objectives

Import existing Wix content into the new article system.

Deliverables

Export Wix content.

Transform content into CLA article structure.

Populate articles table.

Validate formatting and metadata.

Map authors where possible.

Success Criteria

Historical CLA content exists inside Supabase.

The new platform becomes the primary content repository.

⸻

Phase 6 – Dynamic People

Status: Planned

Objectives

Create author and contributor profiles.

Deliverables

People directory:

/people

Individual profiles:

/people/

Author profile blocks.

Articles by author.

LinkedIn integration.

Success Criteria

All authors have profile pages.

Articles are connected to people records.

⸻

Phase 7 – Dynamic Journal

Status: Planned

Objectives

Implement journal editions and contribution management.

Deliverables

Journal edition records.

Journal archive.

Edition pages:

/journal/

Journal-to-article relationships.

Contributor attribution.

Success Criteria

Journal editions are fully database-driven.

Contributions remain linked to article records.

⸻

Phase 8 – Dynamic Events

Status: Planned

Objectives

Replace hardcoded event content.

Deliverables

Featured events.

Upcoming events.

Event archive.

Event detail pages:

/events/

Success Criteria

Events are managed through the database.

The homepage event section becomes dynamic.

⸻

Phase 9 – Podcast Integration

Status: Planned

Objectives

Integrate Spotify content.

Deliverables

Spotify metadata retrieval.

Supabase caching layer.

Dynamic podcast page.

Episode detail support.

Success Criteria

Podcast episodes update automatically from Spotify.

No hardcoded episode content remains.

⸻

Phase 10 – Search & Analytics

Status: Planned

Objectives

Improve discoverability and editorial insights.

Deliverables

Article search.

Tag search.

Author search.

Sitewide article views.

Most-viewed articles.

Most-viewed authors.

Success Criteria

Users can discover content efficiently.

Editorial metrics are available.

⸻

Phase 11 – Administrative Dashboard

Status: Planned

Objectives

Create an internal content-management interface.

Deliverables

Article management.

People management.

Journal management.

Event management.

Content publishing workflow.

Success Criteria

Non-technical administrators can manage platform content.

Direct database access is no longer required.

⸻

Phase 12 – Production Deployment

Status: Planned

Objectives

Launch the platform publicly.

Deliverables

Production hosting.

Supabase production environment.

Domain configuration.

Security review.

Backup strategy.

Monitoring.

Success Criteria

Corporate Law Academy operates as a fully dynamic production platform.

⸻

Development Priorities

The order of implementation should remain:

1. Supabase Foundation
2. Dynamic Articles
3. Wix Migration
4. Dynamic People
5. Dynamic Journal
6. Dynamic Events
7. Podcast Integration
8. Search & Analytics
9. Administrative Dashboard
10. Production Deployment

This order should only be changed where technical requirements make it necessary.