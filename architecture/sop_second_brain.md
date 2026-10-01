# 🧠 SOP: Second Brain Knowledge & Note Search Engine

## Purpose
Specifies the discovery, parsing, and retrieval of Markdown notes in the user's Second Brain workspace (`d:/_Second Brain`).

## Indexing & Search Flow
1. **Target Directory:**
   - Base path: `d:/_Second Brain` (excluding `.git`, `.tmp`, `node_modules`, `__pycache__`).
2. **Parsing Rules:**
   - Extract title from YAML frontmatter, H1 (`# ...`), or filename.
   - Extract tags (`#tag` or frontmatter tags).
   - Index first 500 characters as summary snippet.
3. **Query Matching:**
   - Token-based search across filenames, headers, tags, and content.
   - Ranked scoring: Exact title match > Tag match > Content snippet match.
4. **Action Execution:**
   - Return top note matches with file paths.
   - Ability to open the matched note directly in default editor / VS Code.
