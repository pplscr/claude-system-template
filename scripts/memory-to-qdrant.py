#!/usr/bin/env python3
"""Memory to Qdrant — OpenRouter free embeddings (nvidia/nemotron-3-embed-1b, 2048d, $0).

Supports system/user + space-level collections:
  system_memory ← /root/.claude/projects/-root/memory/system/
  user_memory   ← /root/.claude/projects/-root/memory/user/
  factory_nsc_memory ← /root/factory-nsc/memory/    (auto-detected by CWD)

Usage:
    python3 memory-to-qdrant.py --search "query"              # search both + space (if in space)
    python3 memory-to-qdrant.py --search "query" --type system  # search system only
    python3 memory-to-qdrant.py --search "query" --type user    # search user only
    python3 memory-to-qdrant.py --search "query" --space factory-nsc  # search space only
    python3 memory-to-qdrant.py                                # sync both + space (if in space)
    python3 memory-to-qdrant.py --type system                  # sync system only
    python3 memory-to-qdrant.py --space factory-nsc            # sync space only
    python3 memory-to-qdrant.py --space factory-nsc --type system  # sync system + space
    python3 memory-to-qdrant.py --list                          # list both + space
"""

import os, sys, hashlib, time, json
from datetime import datetime
from pathlib import Path

MEMORY_ROOT = "/root/.claude/projects/-root/memory"
QDRANT_URL = "http://localhost:6333"
COLLECTIONS = {
    "system": "system_memory",
    "user": "user_memory",
}
# Space-level memory — auto-detected by CWD + available via --space flag
SPACES = {
    "factory-nsc": {
        "dir": "/root/factory-nsc/memory",
        "collection": "factory_nsc_memory",
    },
}
VECTOR_SIZE = 2048  # nemotron-3-embed-1b
FREE_MODEL = "nvidia/nemotron-3-embed-1b:free"

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY", "luNXwQs3maFYpeZeqAqI3Y_ZlzRrqt_aWZdVffPzRrQ")
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("CLAUDE_CODE_API_KEY")


def embed(text: str) -> list[float]:
    """OpenRouter free embeddings → hash fallback."""
    if key and key.startswith("sk-"):
        try:
            import requests
            resp = requests.post(
                "https://openrouter.ai/api/v1/embeddings",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": FREE_MODEL, "input": [text[:8000]]},
                timeout=30,
            )
            if resp.status_code == 200:
                emb = resp.json()["data"][0]["embedding"]
                if len(emb) < VECTOR_SIZE:
                    emb += [0.0] * (VECTOR_SIZE - len(emb))
                return emb[:VECTOR_SIZE]
        except Exception as e:
            print(f"   ⚠️  API: {e}", file=sys.stderr)

    # Hash fallback (deterministic, no API cost)
    h = hashlib.sha256(text.encode()).digest()
    return [
        (int.from_bytes(h[i : i + 4], "big") / 2**32 * 2 - 1)
        for i in range(0, VECTOR_SIZE * 4, 4)
    ][:VECTOR_SIZE]


def detect_space() -> str | None:
    """Auto-detect which space we're in based on CWD."""
    cwd = os.getcwd().rstrip("/")
    for name, cfg in SPACES.items():
        space_root = os.path.dirname(cfg["dir"])
        if cwd.startswith(space_root + "/") or cwd == space_root:
            return name
    return None


def read_memories(mem_type: str | None = None) -> list[dict]:
    """Read memories from system/ and/or user/ directories."""
    memories = []
    types_to_read = [mem_type] if mem_type else ["system", "user"]

    for t in types_to_read:
        mem_dir = Path(MEMORY_ROOT) / t
        if not mem_dir.exists():
            print(f"   ⚠️  Directory not found: {mem_dir}", file=sys.stderr)
            continue

        for f in sorted(mem_dir.glob("*.md")):
            if f.name in ("MEMORY.md", "README.md"):
                continue
            text = f.read_text()
            desc = ""
            if text.startswith("---"):
                parts = text.split("---", 2)
                if len(parts) >= 3:
                    for line in parts[1].split("\n"):
                        if line.startswith("description:"):
                            desc = line.split(":", 1)[1].strip().strip('"')
                    text = desc + " " + parts[2]

            memories.append({
                "name": f.stem,
                "description": desc,
                "text": text[:2000],
                "type": t,
                "filepath": str(f),
            })

    return memories


def read_space_memories(space_name: str) -> list[dict]:
    """Read memories from a space directory."""
    cfg = SPACES[space_name]
    mem_dir = Path(cfg["dir"])
    memories = []

    if not mem_dir.exists():
        print(f"   ⚠️  Space directory not found: {mem_dir}", file=sys.stderr)
        return memories

    for f in sorted(mem_dir.glob("*.md")):
        if f.name in ("MEMORY.md", "README.md"):
            continue
        text = f.read_text()
        desc = ""
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].split("\n"):
                    if line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"')
                text = desc + " " + parts[2]

        memories.append({
            "name": f.stem,
            "description": desc,
            "text": text[:2000],
            "type": space_name,
            "filepath": str(f),
        })

    return memories


def ensure_collection(coll_name: str):
    """Ensure a Qdrant collection exists; create it if missing."""
    try:
        client.get_collection(coll_name)
    except Exception:
        client.create_collection(
            collection_name=coll_name,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def sync_collection(mem_type: str):
    """Sync one memory type (system/user) to its Qdrant collection."""
    coll = COLLECTIONS[mem_type]
    memories = read_memories(mem_type)

    label = "🔧 system" if mem_type == "system" else "👤 user"
    print(f"\n{label}  {len(memories)} files → {coll}")

    if not memories:
        print(f"   (no files, skipping)")
        return

    # Use incremental upsert — ensure collection exists, then upsert
    ensure_collection(coll)

    points = []
    for i, m in enumerate(memories):
        vec = embed(m["text"])
        points.append(PointStruct(
            id=hashlib.md5(m["filepath"].encode()).hexdigest(),
            vector=vec,
            payload={
                "name": m["name"],
                "description": m["description"],
                "text": m["text"][:500],
                "type": m["type"],
                "synced_at": datetime.now().isoformat(),
            },
        ))
        if (i + 1) % 10 == 0:
            print(f"   {i + 1}/{len(memories)} embeddings generated")

    t0 = time.time()
    client.upsert(collection_name=coll, points=points)
    dt = (time.time() - t0) * 1000
    info = client.get_collection(coll)
    print(f"   ✅ {info.points_count} points in {dt:.1f}ms | {VECTOR_SIZE}d | {FREE_MODEL} | $0.00")


def sync_space(space_name: str):
    """Sync a space's memory files to its Qdrant collection."""
    cfg = SPACES[space_name]
    coll = cfg["collection"]
    memories = read_space_memories(space_name)

    print(f"\n🏭 {space_name}  {len(memories)} files → {coll}")

    if not memories:
        print(f"   (no files, skipping)")
        return

    # Use incremental upsert — ensure collection exists, then upsert
    ensure_collection(coll)

    points = []
    for i, m in enumerate(memories):
        vec = embed(m["text"])
        points.append(PointStruct(
            id=hashlib.md5(m["filepath"].encode()).hexdigest(),
            vector=vec,
            payload={
                "name": m["name"],
                "description": m["description"],
                "text": m["text"][:500],
                "type": space_name,
                "synced_at": datetime.now().isoformat(),
            },
        ))
        if (i + 1) % 10 == 0:
            print(f"   {i + 1}/{len(memories)} embeddings generated")

    t0 = time.time()
    client.upsert(collection_name=coll, points=points)
    dt = (time.time() - t0) * 1000
    info = client.get_collection(coll)
    print(f"   ✅ {info.points_count} points in {dt:.1f}ms | {VECTOR_SIZE}d | {FREE_MODEL} | $0.00")


def search_collections(query: str, mem_type: str | None = None, space_name: str | None = None, limit: int = 5):
    """Search collections and display results.

    If mem_type is set, search only that type.
    If space_name is set, search that space's collection.
    If neither is set, search all (system + user + auto-detected space).
    """
    colls = []  # list of (display_label, collection_name, type_tag)
    type_labels = []

    if mem_type:
        colls.append((mem_type, COLLECTIONS[mem_type], "🔧" if mem_type == "system" else "👤"))
        type_labels.append(mem_type)
    elif space_name:
        cfg = SPACES[space_name]
        colls.append((space_name, cfg["collection"], "🏭"))
        type_labels.append(space_name)
    else:
        # Search system + user
        for t in ("system", "user"):
            colls.append((t, COLLECTIONS[t], "🔧" if t == "system" else "👤"))
            type_labels.append(t)
        # Auto-detect space
        detected = detect_space()
        if detected:
            colls.append((detected, SPACES[detected]["collection"], "🏭"))
            type_labels.append(detected)

    type_label = "+".join(type_labels)

    vec = embed(query)

    all_results = []
    collection_timings = {}

    for t, coll, tag in colls:
        ensure_collection(coll)
        t0 = time.time()
        try:
            results = client.query_points(collection_name=coll, query=vec, limit=limit)
            dt = (time.time() - t0) * 1000
            collection_timings[coll] = dt

            if results.points:
                for r in results.points:
                    all_results.append({
                        "score": r.score,
                        "name": r.payload.get("name", "?"),
                        "description": r.payload.get("description", "")[:100],
                        "collection": coll,
                        "type": r.payload.get("type", t),
                        "tag": tag,
                    })
        except Exception as e:
            print(f"   ⚠️  Search error in {coll}: {e}", file=sys.stderr)
            collection_timings[coll] = -1

    # Sort by score descending, take top results
    all_results.sort(key=lambda x: x["score"], reverse=True)
    top_results = all_results[:limit]

    # Display
    timing_str = ", ".join(
        f"{coll}: {dt:.1f}ms" if dt >= 0 else f"{coll}: err"
        for coll, dt in collection_timings.items()
    )
    print(f"🔍 «{query}»  [{type_label}]  ({timing_str})")
    print(f"   {VECTOR_SIZE}d · {FREE_MODEL} · $0.00")

    if top_results:
        for r in top_results:
            bar = "█" * min(10, max(0, int(r["score"] * 10))) + "░" * max(0, 10 - min(10, max(0, int(r["score"] * 10))))
            print(f"  {bar} {r['score']:.4f}  {r['tag']} {r['name']}")
            if r["description"]:
                print(f"            {r['description']}")
    else:
        print("  (no results — try syncing first with: memory sync)")


def list_memories(mem_type: str | None = None, space_name: str | None = None):
    """List memory files with their type and description."""
    memories = read_memories(mem_type)

    # Also list space memories if detected
    if not mem_type and not space_name:
        detected = detect_space()
        if detected:
            space_mems = read_space_memories(detected)
            memories.extend(space_mems)
    elif space_name:
        memories = read_space_memories(space_name)

    if not memories:
        print("(no memory files found)")
        return

    # Group by type for display
    by_type = {}
    for m in memories:
        by_type.setdefault(m["type"], []).append(m)

    for t in sorted(by_type.keys()):
        items = by_type[t]
        if not items:
            continue
        if t == "system":
            label = f"🔧 system  ({len(items)} files)"
        elif t == "user":
            label = f"👤 user  ({len(items)} files)"
        else:
            label = f"🏭 {t}  ({len(items)} files)"
        print(f"\n{label}")
        for m in items:
            desc = m["description"][:80] if m["description"] else "(no description)"
            print(f"  {m['name']}")
            print(f"    {desc}")


# ── Main ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Parse flags
    mem_type = None
    space_name = None

    if "--type" in sys.argv:
        idx = sys.argv.index("--type")
        if idx + 1 < len(sys.argv):
            mem_type = sys.argv[idx + 1]
            if mem_type not in ("system", "user"):
                print(f"❌ Invalid --type: {mem_type}. Must be 'system' or 'user'.", file=sys.stderr)
                sys.exit(1)
        else:
            print("❌ --type requires a value: 'system' or 'user'", file=sys.stderr)
            sys.exit(1)

    if "--space" in sys.argv:
        idx = sys.argv.index("--space")
        if idx + 1 < len(sys.argv):
            space_name = sys.argv[idx + 1]
            if space_name not in SPACES:
                print(f"❌ Unknown space: {space_name}. Available: {', '.join(SPACES.keys())}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"❌ --space requires a value. Available: {', '.join(SPACES.keys())}", file=sys.stderr)
            sys.exit(1)

    if "--list" in sys.argv:
        list_memories(mem_type, space_name)
    elif "--search" in sys.argv:
        idx = sys.argv.index("--search")
        if idx + 1 >= len(sys.argv):
            print("❌ --search requires a query string", file=sys.stderr)
            sys.exit(1)
        query = sys.argv[idx + 1]
        search_collections(query, mem_type, space_name)
    else:
        # Sync mode
        types_to_sync = [mem_type] if mem_type else ["system", "user"]
        spaces_to_sync = [space_name] if space_name else []
        if not space_name and not mem_type:
            detected = detect_space()
            if detected:
                spaces_to_sync.append(detected)

        all_colls = [COLLECTIONS[t] for t in types_to_sync]
        for s in spaces_to_sync:
            all_colls.append(SPACES[s]["collection"])

        print(f"📄 Memory → Qdrant  ({VECTOR_SIZE}d, {FREE_MODEL}, $0.00)")
        print(f"   Collections: {', '.join(all_colls)}")

        for t in types_to_sync:
            sync_collection(t)
        for s in spaces_to_sync:
            sync_space(s)

        print(f"\n🏁 Sync complete.")
