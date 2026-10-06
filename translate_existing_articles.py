import hashlib

from config import Config
from supabase import create_client, ClientOptions

# pyrefly: ignore [missing-import]
from translator import translate_article


supabase = create_client(
    Config.SUPABASE_URL,
    Config.SUPABASE_SERVICE_ROLE_KEY,
    options=ClientOptions(
        schema="public"
    ),
)


def get_source_hash(article):
    source_text = "|".join([
        article.get("title") or "",
        article.get("excerpt") or "",
        article.get("content") or "",
    ])

    return hashlib.sha256(
        source_text.encode("utf-8")
    ).hexdigest()


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

    rows = response.data or []

    return rows[0] if rows else None


def translate_existing_articles():
    response = (
        supabase
        .table("articles")
        .select("id,title,excerpt,content,source_language,status")
        .eq("source_language", "it")
        .execute()
    )

    articles = response.data or []

    print(f"Found {len(articles)} Italian articles.")

    for index, article in enumerate(articles, start=1):
        article_id = article["id"]
        title = article.get("title") or ""

        print()
        print(f"[{index}/{len(articles)}] {title}")

        source_hash = get_source_hash(article)

        existing = get_existing_translation(article_id)

        if (
            existing
            and existing.get("source_hash") == source_hash
        ):
            print("Already translated. Skipping.")
            continue

        try:
            translated = translate_article(
                title=title,
                excerpt=article.get("excerpt") or "",
                content=article.get("content") or "",
                source_language="it",
                target_language="en"
            )

            translation_data = {
                "article_id": article_id,
                "language": "en",
                "title": translated["title"],
                "excerpt": translated["excerpt"],
                "content": translated["content"],
                "source_hash": source_hash,
            }

            if existing:
                (
                    supabase
                    .table("article_translations")
                    .update(translation_data)
                    .eq("id", existing["id"])
                    .execute()
                )

                print("Translation updated.")

            else:
                (
                    supabase
                    .table("article_translations")
                    .insert(translation_data)
                    .execute()
                )

                print("Translation created.")

        except Exception as error:
            print(f"FAILED: {error}")


if __name__ == "__main__":
    translate_existing_articles()