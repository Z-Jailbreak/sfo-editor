import os

KNOWN_LANGS = ("en", "es")


def _split_lang(stem):
    """'readme-es' -> ('readme', 'es'); 'readme' -> ('readme', None)"""
    base, sep, lang = stem.rpartition("-")
    if sep and base and lang in KNOWN_LANGS:
        return base, lang
    return stem, None


def _parse_document(raw, filename):
    """Splits the front matter (title/description) from the markdown body.

    Expected format:

        ---
        title: Title
        description: Description
        ---
        Markdown content...
    """
    title = os.path.splitext(filename)[0]
    description = ""
    content = raw.strip()

    lines = raw.splitlines()
    if lines and lines[0].strip() == "---":
        end = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break

        if end is not None:
            for line in lines[1:end]:
                if ":" not in line:
                    continue
                key, _, value = line.partition(":")
                key = key.strip().lower()
                value = value.strip()
                if key == "title" and value:
                    title = value
                elif key == "description" and value:
                    description = value
            content = "\n".join(lines[end + 1:]).strip()

    return {
        "title": title,
        "description": description,
        "content": content,
    }


def load_help_docs(lang):
    """Reads the help/ .md files matching the given language.

    A file is assigned a language by its suffix: `readme-es.md` only
    appears when `lang == "es"`. If the file doesn't exist for that
    language, the document doesn't appear at all.

    Each document: {id, file, lang, title, description, content}
    """
    folder = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "help"
    )
    if not os.path.isdir(folder):
        return []

    docs = []
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".md"):
            continue
        path = os.path.join(folder, filename)
        if not os.path.isfile(path):
            continue

        base, doc_lang = _split_lang(os.path.splitext(filename)[0])
        if doc_lang != lang:
            continue

        with open(path, "r", encoding="utf-8") as f:
            info = _parse_document(f.read(), filename)

        info["id"] = base
        info["file"] = filename
        info["lang"] = doc_lang
        docs.append(info)

    return docs


def get_help_doc(doc_id, lang):
    """Returns the specific document for that language or None"""
    for doc in load_help_docs(lang):
        if doc["id"] == doc_id:
            return doc
    return None
