from functools import lru_cache
import re

# pyrefly: ignore [missing-import]
import torch
from bs4 import BeautifulSoup, NavigableString
# pyrefly: ignore [missing-import]
from transformers import MarianMTModel, MarianTokenizer


MODEL_NAMES = {
    ("it", "en"): "Helsinki-NLP/opus-mt-it-en",
    ("en", "it"): "Helsinki-NLP/opus-mt-en-it",
}


@lru_cache(maxsize=2)
def get_translation_model(source_language, target_language):
    model_name = MODEL_NAMES.get(
        (source_language, target_language)
    )

    if not model_name:
        raise ValueError(
            f"Unsupported translation: "
            f"{source_language} -> {target_language}"
        )

    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)

    model.eval()

    return tokenizer, model


def split_text(text, max_chars=900):
    """
    Split long text into manageable chunks without cutting
    ordinary sentences unnecessarily.
    """
    text = (text or "").strip()

    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    sentences = re.split(r"(?<=[.!?])\s+", text)

    chunks = []
    current = ""

    for sentence in sentences:
        # Handle unusually long single sentences.
        if len(sentence) > max_chars:
            words = sentence.split()
            partial = ""

            for word in words:
                candidate = (
                    f"{partial} {word}".strip()
                    if partial
                    else word
                )

                if len(candidate) <= max_chars:
                    partial = candidate
                else:
                    if partial:
                        chunks.append(partial)

                    partial = word

            if partial:
                if current:
                    chunks.append(current)
                    current = ""

                chunks.append(partial)

            continue

        candidate = (
            f"{current} {sentence}".strip()
            if current
            else sentence
        )

        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)

            current = sentence

    if current:
        chunks.append(current)

    return chunks


def translate_chunk(
    text,
    source_language,
    target_language
):
    tokenizer, model = get_translation_model(
        source_language,
        target_language
    )

    encoded = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    )

    with torch.inference_mode():
        generated = model.generate(
            **encoded,
            max_length=512,
            num_beams=4,
            early_stopping=True
        )

    translated = tokenizer.decode(
        generated[0],
        skip_special_tokens=True
    )

    return translated.strip()


def translate_text(
    text,
    source_language,
    target_language
):
    """
    Translate ordinary text while handling longer passages safely.
    """
    if not text:
        return text

    if source_language == target_language:
        return text

    chunks = split_text(text)

    translated_chunks = [
        translate_chunk(
            chunk,
            source_language,
            target_language
        )
        for chunk in chunks
    ]

    return " ".join(translated_chunks)


def should_translate_node(node):
    """
    Decide whether a BeautifulSoup text node should be translated.
    """
    if not isinstance(node, NavigableString):
        return False

    text = str(node)

    if not text.strip():
        return False

    parent = node.parent

    if not parent:
        return False

    # Content inside these elements should never be translated.
    if parent.name in {
        "script",
        "style",
        "code",
        "pre",
        "noscript"
    }:
        return False

    return True


def translate_html(
    html_content,
    source_language,
    target_language
):
    """
    Translate visible text inside HTML while preserving the HTML
    structure, links and formatting.
    """
    if not html_content:
        return html_content

    if source_language == target_language:
        return html_content

    soup = BeautifulSoup(
        html_content,
        "html.parser"
    )

    text_nodes = [
        node
        for node in soup.find_all(string=True)
        if should_translate_node(node)
    ]

    for node in text_nodes:
        original_text = str(node)

        leading_space = (
            original_text[:len(original_text) - len(original_text.lstrip())]
        )

        trailing_space = (
            original_text[len(original_text.rstrip()):]
        )

        clean_text = original_text.strip()

        if not clean_text:
            continue

        translated_text = translate_text(
            clean_text,
            source_language,
            target_language
        )

        node.replace_with(
            f"{leading_space}{translated_text}{trailing_space}"
        )

    return str(soup)


def translate_article(
    title,
    excerpt,
    content,
    source_language,
    target_language
):
    """
    Translate the translatable fields of an article.
    """

    translated_title = translate_text(
        title,
        source_language,
        target_language
    )

    translated_excerpt = translate_text(
        excerpt,
        source_language,
        target_language
    )

    translated_content = translate_html(
        content,
        source_language,
        target_language
    )

    return {
        "title": translated_title,
        "excerpt": translated_excerpt,
        "content": translated_content,
    }