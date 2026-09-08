#!/usr/bin/env python3
"""The gate CI runs on every change: standard library only, one network call per product.

  1. .claude-plugin/marketplace.json must parse and be named helmet-duck, the name users
     see in every install id.
  2. every entry must carry a name, a source and a version; names must be unique.
  3. a source that is a folder of this repository must hold a plugin manifest agreeing on
     the version. A GitHub source must be one of the owner's repositories, and the version
     pinned here must equal the version in that repository's .claude-plugin/plugin.json on
     its main branch, fetched from GitHub. A marketplace that promises a version the
     product does not have is the one defect this file exists to catch.
  4. English is the only language of this repository.
  5. every workflow must pin its actions to a commit SHA and declare its permissions.

Exit 0 only when everything holds. Findings are printed as a table.
"""
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
OWNER = "garitac"
MARKETPLACE_NAME = "helmet-duck"
RAW = "https://raw.githubusercontent.com/%s/%s/.claude-plugin/plugin.json"


def _fetch_manifest(repo, ref="main"):
    req = urllib.request.Request(RAW % (repo, ref), headers={"User-Agent": "helmet-duck-marketplace-check"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def check_marketplace(rows):
    try:
        market = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        rows.append(("marketplace.json parses", True, ""))
    except (OSError, ValueError) as exc:
        rows.append(("marketplace.json parses", False, str(exc)[:80]))
        return
    rows.append(("marketplace is named %s" % MARKETPLACE_NAME, market.get("name") == MARKETPLACE_NAME, str(market.get("name"))))
    plugins = market.get("plugins", [])
    names = [p.get("name") for p in plugins]
    rows.append(("%d product(s), names unique" % len(plugins), len(set(names)) == len(names) and None not in names, ", ".join(map(str, names))))
    for entry in plugins:
        name, src, version = entry.get("name"), entry.get("source"), entry.get("version")
        if not (name and src and version):
            rows.append(("entry %s complete" % name, False, "name, source and version are all required"))
            continue
        if isinstance(src, str):
            manifest = ROOT / src / ".claude-plugin" / "plugin.json"
            try:
                found = json.loads(manifest.read_text(encoding="utf-8"))
                ok = found.get("version") == version and found.get("name") == name
                rows.append(("%s: folder %s agrees" % (name, src), ok, "" if ok else "manifest says %s %s" % (found.get("name"), found.get("version"))))
            except (OSError, ValueError) as exc:
                rows.append(("%s: folder %s agrees" % (name, src), False, str(exc)[:80]))
        elif isinstance(src, dict) and src.get("source") == "github":
            repo = src.get("repo", "")
            if not re.fullmatch(r"%s/[A-Za-z0-9._-]+" % re.escape(OWNER), repo):
                rows.append(("%s: repository is the owner's" % name, False, repo))
                continue
            rows.append(("%s: repository is the owner's" % name, True, repo))
            try:
                found = _fetch_manifest(repo, src.get("ref", "main"))
            except (urllib.error.URLError, ValueError, OSError) as exc:
                rows.append(("%s: pinned %s equals the manifest on %s" % (name, version, repo), False, "fetch failed: %s" % str(exc)[:70]))
                continue
            ok = found.get("version") == version and found.get("name") == name
            rows.append(("%s: pinned %s equals the manifest on %s" % (name, version, repo), ok,
                         "" if ok else "manifest says %s %s" % (found.get("name"), found.get("version"))))
        else:
            rows.append(("%s: source understood" % name, False, repr(src)[:60]))


# Cyrillic, Hebrew and Arabic, Indic, Thai, Japanese kana, CJK ideographs, Hangul and
# full-width forms, built from code points so this file stays ASCII and passes its own check.
NON_LATIN_RANGES = ((0x0400, 0x04FF), (0x0590, 0x06FF), (0x0900, 0x0DFF), (0x0E00, 0x0E7F),
                    (0x3040, 0x30FF), (0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xAC00, 0xD7AF),
                    (0xFF00, 0xFFEF))
NON_LATIN = re.compile("[" + "".join("%s-%s" % (chr(a), chr(b)) for a, b in NON_LATIN_RANGES) + "]")
TEXT_SUFFIXES = {".py", ".md", ".json", ".yml", ".yaml", ".txt"}


def check_english_only(rows):
    hits = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix not in TEXT_SUFFIXES or p.relative_to(ROOT).parts[0] in (".git", "__pycache__"):
            continue
        try:
            for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if NON_LATIN.search(line):
                    hits.append("%s:%d" % (p.relative_to(ROOT), n))
        except (OSError, UnicodeDecodeError):
            continue
    rows.append(("english only (no non-Latin scripts)", not hits, ", ".join(hits[:6])))


def check_workflows(rows):
    unpinned, unscoped = [], []
    for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        text = wf.read_text(encoding="utf-8")
        for m in re.finditer(r"^\s*-?\s*uses:\s*(\S+)", text, re.M):
            if not re.search(r"@[0-9a-f]{40}$", m.group(1)):
                unpinned.append("%s: %s" % (wf.name, m.group(1)))
        if not re.search(r"^permissions:", text, re.M):
            unscoped.append(wf.name)
    rows.append(("workflow actions pinned to a commit SHA", not unpinned, ", ".join(unpinned)))
    rows.append(("workflows declare permissions", not unscoped, ", ".join(unscoped)))


def main():
    rows = []
    check_marketplace(rows)
    check_english_only(rows)
    check_workflows(rows)
    width = max(len(r[0]) for r in rows)
    for name, ok, note in rows:
        print("  %-5s %-*s %s" % ("ok" if ok else "FAIL", width, name, note))
    failed = [r for r in rows if not r[1]]
    print("\n%s" % ("CHECK PASS" if not failed else "CHECK FAIL (%d)" % len(failed)))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
