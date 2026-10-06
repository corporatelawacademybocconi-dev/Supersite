import hashlib
import time
from datetime import datetime, timezone

from supabase import create_client, ClientOptions

from config import Config
from translator import translate_article


supabase = create_client(
    Config.SUPABASE_URL,
    Config.SUPABASE_SERVICE_ROLE_KEY,
    options=ClientOptions(schema="public"),
)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def get_source_hash(article):
    source_text = "|".join([
        article.get("title") or "",
        article.get("excerpt") or "",
        article.get("content") or "",
    ])

    return hashlib.sha256(
        source_text.encode("utf-8")
    ).hexdigest()


def get_next_job():
    response = (
        supabase
        .table("translation_jobs")
        .select("*")
        .eq("status", "pending")
        .order("created_at")
        .limit(1)
        .execute()
    )

    jobs = response.data or []

    return jobs[0] if jobs else None


def mark_job_processing(job):
    attempts = (job.get("attempts") or 0) + 1

    (
        supabase
        .table("translation_jobs")
        .update({
            "status": "processing",
            "attempts": attempts,
            "error": None,
            "updated_at": now_iso(),
        })
        .eq("id", job["id"])
        .execute()
    )


def mark_job_done(job_id):
    (
        supabase
        .table("translation_jobs")
        .update({
            "status": "done",
            "error": None,
            "updated_at": now_iso(),
        })
        .eq("id", job_id)
        .execute()
    )


def mark_job_failed(job_id, error):
    (
        supabase
        .table("translation_jobs")
        .update({
            "status": "failed",
            "error": str(error)[:2000],
            "updated_at": now_iso(),
        })
        .eq("id", job_id)
        .execute()
    )


def get_article(article_id):
    response = (
        supabase
        .table("articles")
        .select(
            "id,title,excerpt,content,source_language"
        )
        .eq("id", article_id)
        .limit(1)
        .execute()
    )

    articles = response.data or []

    return articles[0] if articles else None


def get_existing_translation(article_id):
    response = (
        supabase
        .table("article_translations")
        .select("*")
        .eq("article_id", article_id)
        .eq("language", "en")
        .limit(1)
        .execute()
    )

    translations = response.data or []

    return translations[0] if translations else None


def save_translation(article, translated):
    article_id = article["id"]

    source_hash = get_source_hash(article)

    translation_data = {
        "article_id": article_id,
        "language": "en",
        "title": translated["title"],
        "excerpt": translated["excerpt"],
        "content": translated["content"],
        "source_hash": source_hash,
        "updated_at": now_iso(),
    }

    existing = get_existing_translation(article_id)

    if existing:
        (
            supabase
            .table("article_translations")
            .update(translation_data)
            .eq("id", existing["id"])
            .execute()
        )

        print("Existing English translation updated.")

    else:
        (
            supabase
            .table("article_translations")
            .insert(translation_data)
            .execute()
        )

        print("English translation created.")


def process_job(job):
    print()
    print(
        f"Processing job {job['id']} "
        f"for article {job['article_id']}..."
    )

    mark_job_processing(job)

    article = get_article(job["article_id"])

    if not article:
        raise ValueError("Article not found.")

    if article.get("source_language") != "it":
        raise ValueError(
            "Article source language is not Italian."
        )

    translated = translate_article(
        title=article.get("title") or "",
        excerpt=article.get("excerpt") or "",
        content=article.get("content") or "",
        source_language="it",
        target_language="en",
    )

    save_translation(
        article,
        translated,
    )

    mark_job_done(job["id"])

    print(
        f"Job {job['id']} completed successfully."
    )


def run_worker():
    print("Translation worker started.")
    print("Waiting for translation jobs...")

    while True:
        job = get_next_job()

        if not job:
            time.sleep(10)
            continue

        try:
            process_job(job)

        except Exception as error:
            print(
                f"Job {job['id']} failed: {error}"
            )

            mark_job_failed(
                job["id"],
                error,
            )

        time.sleep(2)


if __name__ == "__main__":
    run_worker()