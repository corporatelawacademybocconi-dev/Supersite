from flask import Flask, render_template
# pyrefly: ignore [missing-import]
from supabase import create_client

from datetime import datetime, timezone

from config import Config

from flask import request, session, redirect, url_for

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config["SECRET_KEY"]
print("URL:", app.config["SUPABASE_URL"])
print("KEY:", app.config["SUPABASE_KEY"][:20] if app.config["SUPABASE_KEY"] else None)

supabase = create_client(
    app.config["SUPABASE_URL"],
    app.config["SUPABASE_KEY"]
)

@app.route("/reserved-area-login", methods=["GET", "POST"])
def reserved_area_login():

    if request.method == "POST":

        password = request.form.get("password")

        if password == app.config["ADMIN_PASSWORD"]:
            session["reserved_access"] = True
            return redirect(url_for("reserved_area"))

    return render_template("admin/login.html")

@app.route("/reserved-area")
def reserved_area():

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    return render_template("admin/dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/reserved-area/events")
def admin_events():

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    response = (
        supabase
        .table("events")
        .select("*")
        .order("start_datetime", desc=True)
        .execute()
    )

    events = response.data or []

    return render_template(
        "admin/events.html",
        events=events
    )
@app.route("/reserved-area/events/create", methods=["GET", "POST"])
def admin_create_event():

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    if request.method == "POST":

        title = request.form.get("title")
        slug = request.form.get("slug")
        description = request.form.get("description")
        location = request.form.get("location")
        start_datetime = request.form.get("start_datetime")

        supabase.table("events").insert({
            "title": title,
            "slug": slug,
            "description": description,
            "location": location,
            "start_datetime": start_datetime,
            "status": "published"
        }).execute()

        return redirect(url_for("admin_events"))

    return render_template("admin/create_event.html")

@app.route("/reserved-area/people")
def admin_people():

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    response = (
        supabase
        .table("people")
        .select("*")
        .order("name")
        .execute()
    )

    people = response.data or []

    return render_template(
        "admin/people.html",
        people=people
    )
@app.route("/reserved-area/people/create", methods=["GET", "POST"])
def admin_create_person():

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    if request.method == "POST":

        name = request.form.get("name")
        slug = request.form.get("slug")
        role = request.form.get("role")
        bio = request.form.get("bio")
        linkedin_url = request.form.get("linkedin_url")

        supabase.table("people").insert({
            "name": name,
            "slug": slug,
            "role": role,
            "bio": bio,
            "linkedin_url": linkedin_url,
            "is_author": True,
            "is_team_member": True
        }).execute()

        return redirect(url_for("admin_people"))

    return render_template("admin/create_person.html")

@app.route("/reserved-area/people/<person_id>/edit", methods=["GET", "POST"])
def admin_edit_person(person_id):

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    if request.method == "POST":

        supabase.table("people").update({
            "name": request.form.get("name"),
            "slug": request.form.get("slug"),
            "role": request.form.get("role"),
            "bio": request.form.get("bio"),
            "linkedin_url": request.form.get("linkedin_url"),
            "is_author": request.form.get("is_author") == "on",
            "is_team_member": request.form.get("is_team_member") == "on"
        }).eq("id", person_id).execute()

        return redirect(url_for("admin_people"))

    response = (
        supabase
        .table("people")
        .select("*")
        .eq("id", person_id)
        .single()
        .execute()
    )

    person = response.data

    return render_template(
        "admin/edit_person.html",
        person=person
    )

@app.route("/reserved-area/articles")
def admin_articles():

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    response = (
        supabase
        .table("articles")
        .select("*, author:people!articles_author_id_fkey(*)")
        .order("created_at", desc=True)
        .execute()
    )

    articles = response.data or []

    return render_template(
        "admin/articles.html",
        articles=articles
    )

@app.route("/reserved-area/articles/create", methods=["GET", "POST"])
def admin_create_article():

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    authors_response = (
        supabase
        .table("people")
        .select("*")
        .eq("is_author", True)
        .order("name")
        .execute()
    )

    authors = authors_response.data or []

    if request.method == "POST":

        title = request.form.get("title")
        slug = title.lower().replace(" ", "-")

        supabase.table("articles").insert({
            "title": title,
            "slug": slug,
            "excerpt": request.form.get("excerpt"),
            "content": request.form.get("content"),
            "author_id": int(request.form.get("author_id")),
            "category": request.form.get("category"),
            "status": request.form.get("status"),
            "is_featured": request.form.get("is_featured") == "on"
        }).execute()

        return redirect(url_for("admin_articles"))

    return render_template(
        "admin/create_article.html",
        authors=authors
    )

@app.route("/reserved-area/articles/<article_id>/edit", methods=["GET", "POST"])
def admin_edit_article(article_id):

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    authors_response = (
        supabase
        .table("people")
        .select("*")
        .eq("is_author", True)
        .order("name")
        .execute()
    )

    authors = authors_response.data or []

    if request.method == "POST":

        supabase.table("articles").update({
            "title": request.form.get("title"),
            "excerpt": request.form.get("excerpt"),
            "content": request.form.get("content"),
            "author_id": int(request.form.get("author_id")),
            "category": request.form.get("category"),
            "status": request.form.get("status"),
            "is_featured": request.form.get("is_featured") == "on"
        }).eq("id", article_id).execute()

        return redirect(url_for("admin_articles"))

    response = (
        supabase
        .table("articles")
        .select("*")
        .eq("id", article_id)
        .single()
        .execute()
    )

    article = response.data

    return render_template(
        "admin/edit_article.html",
        article=article,
        authors=authors
    )

@app.route("/reserved-area/events/<event_id>/edit", methods=["GET", "POST"])
def admin_edit_event(event_id):

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    if request.method == "POST":

        supabase.table("events").update({
            "title": request.form.get("title"),
            "slug": request.form.get("slug"),
            "description": request.form.get("description"),
            "flyer_image_url": request.form.get("flyer_image_url"),
            "event_report": request.form.get("event_report"),
            "location": request.form.get("location"),
            "start_datetime": request.form.get("start_datetime"),
            "end_datetime": request.form.get("end_datetime") or None,
            "registration_url": request.form.get("registration_url"),
            "is_featured": request.form.get("is_featured") == "on",
            "status": request.form.get("status")
        }).eq("id", event_id).execute()

        return redirect(url_for("admin_events"))

    response = (
        supabase
        .table("events")
        .select("*")
        .eq("id", event_id)
        .single()
        .execute()
    )

    event = response.data

    return render_template(
        "admin/edit_event.html",
        event=event
    )
@app.route("/reserved-area/events/<event_id>/delete", methods=["POST"])
def admin_delete_event(event_id):

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    supabase.table("events").delete().eq("id", event_id).execute()

    return redirect(url_for("admin_events"))

@app.route("/reserved-area/journal")
def admin_journal():

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    response = (
        supabase
        .table("journal_editions")
        .select("*")
        .order("publication_date", desc=True)
        .execute()
    )

    editions = response.data or []

    return render_template(
        "admin/journal.html",
        editions=editions
    )

@app.route("/reserved-area/journal/create", methods=["GET", "POST"])
def admin_create_journal_edition():

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    if request.method == "POST":

        title = request.form.get("title")
        slug = request.form.get("slug")

        is_current = request.form.get("is_current") == "on"

        if is_current:
            supabase.table("journal_editions").update({
                "is_current": False
            }).neq("id", "00000000-0000-0000-0000-000000000000").execute()

        supabase.table("journal_editions").insert({
            "title": title,
            "slug": slug,
            "description": request.form.get("description"),
            "pdf_url": request.form.get("pdf_url"),
            "cover_image_url": request.form.get("cover_image_url"),
            "volume": int(request.form.get("volume")) if request.form.get("volume") else None,
            "issue": int(request.form.get("issue")) if request.form.get("issue") else None,
            "publication_date": request.form.get("publication_date") or None,
            "status": request.form.get("status"),
            "is_current": is_current
        }).execute()

        return redirect(url_for("admin_journal"))

    return render_template("admin/create_journal.html")

@app.route("/reserved-area/journal/<edition_id>/edit", methods=["GET", "POST"])
def admin_edit_journal_edition(edition_id):

    if not session.get("reserved_access"):
        return redirect(url_for("reserved_area_login"))

    if request.method == "POST":

        is_current = request.form.get("is_current") == "on"

        if is_current:
            supabase.table("journal_editions").update({
                "is_current": False
            }).neq("id", edition_id).execute()

        supabase.table("journal_editions").update({
            "title": request.form.get("title"),
            "slug": request.form.get("slug"),
            "description": request.form.get("description"),
            "pdf_url": request.form.get("pdf_url"),
            "cover_image_url": request.form.get("cover_image_url"),
            "volume": request.form.get("volume"),
            "issue": request.form.get("issue"),
            "publication_date": request.form.get("publication_date"),
            "status": request.form.get("status"),
            "is_current": is_current
        }).eq("id", edition_id).execute()

        return redirect(url_for("admin_journal"))

    response = (
        supabase
        .table("journal_editions")
        .select("*")
        .eq("id", edition_id)
        .single()
        .execute()
    )

    edition = response.data

    return render_template(
        "admin/edit_journal.html",
        edition=edition
    )

@app.route("/search")
def search():

    query = request.args.get("q", "").strip()

    articles = []
    people = []
    journal_editions = []
    events = []

    if query:

        articles_response = (
            supabase
            .table("articles")
            .select("*")
            .or_(
                f"title.ilike.%{query}%,"
                f"excerpt.ilike.%{query}%,"
                f"content.ilike.%{query}%"
            )
            .eq("status", "published")
            .execute()
        )

        people_response = (
            supabase
            .table("people")
            .select("*")
            .or_(
                f"name.ilike.%{query}%,"
                f"role.ilike.%{query}%,"
                f"bio.ilike.%{query}%"
            )
            .execute()
        )

        journal_response = (
            supabase
            .table("journal_editions")
            .select("*")
            .or_(
                f"title.ilike.%{query}%,"
                f"description.ilike.%{query}%"
            )
            .eq("status", "published")
            .execute()
        )

        event_response = (
            supabase
            .table("events")
            .select("*")
            .or_(
                f"title.ilike.%{query}%,"
                f"description.ilike.%{query}%,"
                f"event_report.ilike.%{query}%"
            )
            .eq("status", "published")
            .execute()
        )

        articles = articles_response.data or []
        people = people_response.data or []
        journal_editions = journal_response.data or []
        events = event_response.data or []

    return render_template(
        "search.html",
        query=query,
        articles=articles,
        people=people,
        journal_editions=journal_editions,
        events=events
    )

@app.route("/our-work")
def our_work():
    return render_template("our_work/index.html")

@app.route("/our-work/articles")
def articles():
    response = (
        supabase
        .table("articles")
        .select("*, author:people!articles_author_id_fkey(*)")
        .eq("status", "published")
        .order("published_at", desc=True)
        .execute()
    )

    articles = response.data

    featured_article = next(
        (article for article in articles if article.get("is_featured")),
        None
    )

    latest_articles = [
        article for article in articles
        if not article.get("is_featured")
    ]

    return render_template(
        "our_work/articles.html",
        articles=articles,
        featured_article=featured_article,
        latest_articles=latest_articles
    )

@app.route("/our-work/articles/<slug>")
def article_detail(slug):
    response = (
        supabase
        .table("articles")
        .select("*, author:people!articles_author_id_fkey(*)")
        .eq("slug", slug)
        .single()
        .execute()
    )

    article = response.data

    return render_template(
    "our_work/article_detail.html",
    article=article
)

@app.route("/our-work/events")
def events():
    now = datetime.now(timezone.utc).isoformat()

    featured_response = (
        supabase
        .table("events")
        .select("*")
        .eq("is_featured", True)
        .eq("status", "published")
        .gte("start_datetime", now)
        .order("start_datetime")
        .limit(1)
        .execute()
    )

    featured_event = featured_response.data[0] if featured_response.data else None

    upcoming_response = (
        supabase
        .table("events")
        .select("*")
        .eq("status", "published")
        .gte("start_datetime", now)
        .order("start_datetime")
        .execute()
    )

    past_response = (
        supabase
        .table("events")
        .select("*")
        .eq("status", "published")
        .lt("start_datetime", now)
        .order("start_datetime", desc=True)
        .execute()
    )

    return render_template(
        "our_work/events.html",
        featured_event=featured_event,
        upcoming_events=upcoming_response.data or [],
        past_events=past_response.data or []
    )
@app.route("/events/<slug>")
def event_detail(slug):
    response = (
        supabase
        .table("events")
        .select("*")
        .eq("slug", slug)
        .eq("status", "published")
        .single()
        .execute()
    )

    event = response.data

    return render_template(
        "our_work/event_detail.html",
        event=event
    )


@app.route("/our-work/team-building")
def team_building():
    return render_template("our_work/team_building.html")


@app.route("/our-work/moot-court")
def moot_court():
    return render_template("our_work/moot_court.html")


@app.route("/our-work/podcast")
def podcast():
    return render_template("our_work/podcast.html")

@app.route("/our-work/journal")

def journal():

    current_response = (

        supabase

        .table("journal_editions")

        .select("*")

        .eq("status", "published")

        .eq("is_current", True)

        .limit(1)

        .execute()

    )

    current_edition = current_response.data[0] if current_response.data else None

    selected_pieces = []

    if current_edition:

        pieces_response = (

            supabase

            .table("journal_articles")

            .select("display_order, is_featured, article:articles(*)")

            .eq("journal_edition_id", current_edition["id"])

            .eq("is_featured", True)

            .order("display_order")

            .execute()

        )

        selected_pieces = pieces_response.data or []

    archive_response = (

        supabase

        .table("journal_editions")

        .select("*")

        .eq("status", "published")

        .order("publication_date", desc=True)

        .execute()

    )

    editions = archive_response.data or []

    return render_template(

        "our_work/journal.html",

        current_edition=current_edition,

        selected_pieces=selected_pieces,

        editions=editions

    )
@app.route("/journal/<slug>")
def journal_detail(slug):
    response = (
        supabase
        .table("journal_editions")
        .select("*")
        .eq("slug", slug)
        .eq("status", "published")
        .single()
        .execute()
    )

    edition = response.data

    return render_template(
        "our_work/journal_detail.html",
        edition=edition
    )

@app.route("/networking")
def networking():
    return render_template("networking.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/test-db")
def test_db():

    response = (
        supabase
        .table("articles")
        .select("*")
        .execute()
    )

    return str(response.data)

@app.route("/people")
def people():
    response = (
        supabase
        .table("people")
        .select("*")
        .order("name")
        .execute()
    )

    people = response.data

    return render_template(
        "people/index.html",
        people=people
    )


@app.route("/people/<slug>")
def person_detail(slug):
    person_response = (
        supabase
        .table("people")
        .select("*")
        .eq("slug", slug)
        .single()
        .execute()
    )

    person = person_response.data

    articles_response = (
        supabase
        .table("articles")
        .select("*")
        .eq("author_id", person["id"])
        .eq("status", "published")
        .order("published_at", desc=True)
        .execute()
    )

    articles = articles_response.data

    return render_template(
        "people/detail.html",
        person=person,
        articles=articles
    )

if __name__ == "__main__":
    app.run(debug=True)