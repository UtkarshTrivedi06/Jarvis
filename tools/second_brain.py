"""
Jarvis Second Brain Knowledge Engine
Searches, indexes, and queries markdown files in the user's Second Brain workspace.
"""

import os
import re
from typing import List, Dict, Optional

class SecondBrainEngine:
    def __init__(self, root_dir: Optional[str] = None):
        if root_dir is None:
            # Locate d:/_Second Brain
            self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        else:
            self.root_dir = os.path.abspath(root_dir)

    def search_notes(self, query: str, limit: int = 5) -> List[Dict]:
        """Performs multi-token search across titles, headers, tags, and content."""
        query_terms = [q.lower() for q in query.split() if len(q) > 1]
        if not query_terms:
            return []

        results = []
        for root, dirs, files in os.walk(self.root_dir):
            # Skip noise directories
            if any(part.startswith(".") or part in ["node_modules", "__pycache__", "target", "build"] for part in root.split(os.sep)):
                continue
                
            for file in files:
                if not file.endswith(".md"):
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except Exception:
                    continue

                filename_lower = file.lower()
                content_lower = content.lower()
                
                score = 0
                matched_snippet = ""

                # Title match scoring
                for term in query_terms:
                    if term in filename_lower:
                        score += 20
                    if term in content_lower:
                        score += 5

                if score > 0:
                    # Extract title or first H1
                    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                    title = title_match.group(1).strip() if title_match else file.replace(".md", "")
                    
                    # Extract snippet
                    lines = content.splitlines()
                    for line in lines:
                        if any(term in line.lower() for term in query_terms):
                            matched_snippet = line.strip()[:140]
                            break
                    if not matched_snippet and lines:
                        matched_snippet = lines[0][:140]

                    rel_path = os.path.relpath(file_path, self.root_dir)
                    results.append({
                        "title": title,
                        "file_name": file,
                        "file_path": file_path,
                        "rel_path": rel_path,
                        "snippet": matched_snippet,
                        "score": score
                    })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def read_note(self, file_path_or_title: str) -> Optional[str]:
        """Reads note content given full path or partial name."""
        if os.path.exists(file_path_or_title) and os.path.isfile(file_path_or_title):
            try:
                with open(file_path_or_title, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            except Exception:
                return None
                
        # Search by name
        results = self.search_notes(file_path_or_title, limit=1)
        if results:
            return self.read_note(results[0]["file_path"])
        return None
