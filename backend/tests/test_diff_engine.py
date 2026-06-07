from app.services.diff_engine import diff_engine


class TestDiffEngine:
    def test_compute_delta_new_text(self):
        delta = diff_engine.compute_delta("", "new content here")
        assert "new content here" in delta

    def test_compute_delta_no_change(self):
        delta = diff_engine.compute_delta("same text", "same text")
        assert delta == ""

    def test_compute_delta_with_addition(self):
        old_text = "line one\nline two\n"
        new_text = "line one\nline two\nline three\n"
        delta = diff_engine.compute_delta(old_text, new_text)
        assert "+line three" in delta

    def test_compute_delta_with_removal(self):
        old_text = "line one\nline two\nline three\n"
        new_text = "line one\nline three\n"
        delta = diff_engine.compute_delta(old_text, new_text)
        assert "-line two" in delta

    def test_has_significant_change_true(self):
        delta = """--- previous
+++ current
@@ -1,1 +1,2 @@
 old
+new"""
        assert diff_engine.has_significant_change(delta)

    def test_has_significant_change_false(self):
        assert not diff_engine.has_significant_change("")

    def test_has_significant_change_minimal(self):
        delta = "no diff markers here"
        assert not diff_engine.has_significant_change(delta, min_change_ratio=0.01)
