
import argparse
import hashlib
import re
from functools import lru_cache
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

VAULT_PATH = (
    Path(__file__).resolve().parents[2]
    / "taskflow-knowledge-base"
)

# Index is stored outside the Git repository.
INDEX_PATH = Path.home() / ".taskflow" / "rag-index"
COLLECTION_NAME = "taskflow_notes"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 80


@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer(MODEL_NAME, device="cpu")


def split_into_chunks(content: str) -> list[str]:
    """Split a Markdown note into smaller sections."""

    content = content.replace("\r\n", "\n")

    # Remove YAML frontmatter from the indexed text.
    frontmatter = re.match(
        r"\A---\n.*?\n---\n",
        content,
        flags=re.DOTALL,
    )

    if frontmatter:
        content = content[frontmatter.end():]

    sections = re.split(
        r"(?=^#{1,6}\s)",
        content,
        flags=re.MULTILINE,
    )

    chunks = []
    step = CHUNK_SIZE - CHUNK_OVERLAP

    for section in sections:
        section = section.strip()

        if not section:
            continue

        if len(section) <= CHUNK_SIZE:
            chunks.append(section)
            continue

        for start in range(0, len(section), step):
            chunk = section[start:start + CHUNK_SIZE]

            if chunk.strip():
                chunks.append(chunk.strip())

            if start + CHUNK_SIZE >= len(section):
                break

    return chunks


def load_vault_chunks():
    """Read Markdown notes from the local Obsidian vault."""

    if not VAULT_PATH.is_dir():
        raise FileNotFoundError(
            f"Obsidian vault not found: {VAULT_PATH}"
        )

    ids = []
    documents = []
    metadatas = []

    vault_root = VAULT_PATH.resolve()

    for path in sorted(VAULT_PATH.rglob("*.md")):
        relative_path = path.relative_to(VAULT_PATH)

        if any(
            part.startswith(".")
            for part in relative_path.parts
        ):
            continue

        # Avoid indexing files outside the vault.
        if not path.resolve().is_relative_to(vault_root):
            continue

        content = path.read_text(encoding="utf-8")

        for index, chunk in enumerate(
            split_into_chunks(content)
        ):
            document = f"{path.stem}\n{chunk}"

            chunk_id = hashlib.sha256(
                f"{relative_path.as_posix()}:{index}".encode(
                    "utf-8"
                )
            ).hexdigest()

            ids.append(chunk_id)
            documents.append(document)
            metadatas.append({
                "source": relative_path.as_posix(),
                "title": path.stem,
                "chunk": index,
            })

    return ids, documents, metadatas


def build_index():
    """Build the persistent Chroma vector index."""

    ids, documents, metadatas = load_vault_chunks()

    if not documents:
        raise RuntimeError(
            "No Markdown chunks found in the Obsidian vault."
        )

    print(f"Vault: {VAULT_PATH}")
    print(f"Chunks: {len(documents)}")
    print(f"Embedding model: {MODEL_NAME}")
    print("Generating embeddings...")

    model = get_model()

    vectors = model.encode(
        documents,
        batch_size=16,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).tolist()

    INDEX_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(INDEX_PATH)
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    # Replace only the derived vector records.
    # Obsidian Markdown notes are not modified.
    existing_ids = collection.get(include=[])["ids"]

    if existing_ids:
        collection.delete(ids=existing_ids)

    for start in range(0, len(documents), 100):
        end = start + 100

        collection.upsert(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
            embeddings=vectors[start:end],
        )

    print(f"Indexed chunks: {collection.count()}")
    print(f"Index location: {INDEX_PATH}")
    print("RAG INDEX BUILD SUCCESSFUL")


def semantic_search(query: str, top_k: int = 5) -> str:
    """Retrieve relevant Obsidian chunks by embeddings."""

    query = query.strip()

    if not query:
        return "Помилка: порожній пошуковий запит."

    if not INDEX_PATH.exists():
        return "Векторний індекс не знайдено."

    client = chromadb.PersistentClient(
        path=str(INDEX_PATH)
    )

    collection = client.get_collection(
        name=COLLECTION_NAME
    )

    count = collection.count()

    if count == 0:
        return "Векторний індекс порожній."

    model = get_model()

    query_vector = model.encode(
        query,
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )

    output = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for document, metadata, distance in zip(
        documents, metadatas, distances
    ):
        output.append(
            f"Файл: {metadata['source']}\n"
            f"Фрагмент: {metadata['chunk']}\n"
            f"Векторна відстань: {distance:.4f}\n"
            f"Вміст:\n{document}"
        )

    return "\n\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="TaskFlow RAG vector index"
    )

    parser.add_argument(
        "action",
        choices=["build", "search"],
    )

    parser.add_argument(
        "query",
        nargs="?",
    )

    args = parser.parse_args()

    if args.action == "build":
        build_index()
    else:
        if not args.query:
            parser.error(
                "The search action requires a query."
            )

        print(semantic_search(args.query))


if __name__ == "__main__":
    main()
