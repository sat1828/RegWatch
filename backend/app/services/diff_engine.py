from __future__ import annotations

import difflib


class DiffEngine:
    @staticmethod
    def compute_delta(old_text: str, new_text: str) -> str:
        if not old_text:
            return new_text

        old_lines = old_text.splitlines(keepends=True)
        new_lines = new_text.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile="previous",
            tofile="current",
            lineterm="\n",
        )
        return "".join(diff)

    @staticmethod
    def has_significant_change(
        delta: str, min_change_ratio: float = 0.01
    ) -> bool:
        if not delta:
            return False

        added = 0
        removed = 0
        for line in delta.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                added += 1
            elif line.startswith("-") and not line.startswith("---"):
                removed += 1

        total_changes = added + removed
        if total_changes == 0:
            return False

        total_lines = len(delta.splitlines())
        change_ratio = total_changes / max(total_lines, 1)
        return change_ratio >= min_change_ratio


diff_engine = DiffEngine()
