import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent.parent.parent
        / ".config"
        / "claude"
        / "scripts"
        / "lib"
    ),
)


class TestTipGeneralizer:
    def test_generalize_user_path(self):
        from tip_generalizer import generalize_text

        result = generalize_text("/Users/takeuchishougo/projects/app/src/index.ts")
        assert "/Users/takeuchishougo/" not in result
        assert "{user_home}/" in result

    def test_generalize_commit_hash(self):
        from tip_generalizer import generalize_text

        result = generalize_text("commit abc1234def5678 broke the build")
        assert "abc1234def5678" not in result
        assert "{hash}" in result

    def test_generalize_version(self):
        from tip_generalizer import generalize_text

        result = generalize_text("upgrade to 3.14.1 caused regression")
        assert "3.14.1" not in result
        assert "{version}" in result

    def test_generalize_port(self):
        from tip_generalizer import generalize_text

        result = generalize_text("server listening on port 3000")
        assert "3000" not in result
        assert "{port}" in result

    def test_generalize_preserves_meaning(self):
        from tip_generalizer import generalize_text

        result = generalize_text("TypeError: Cannot read properties of undefined")
        assert "TypeError" in result
        assert "undefined" in result

    def test_generalize_entry(self):
        from tip_generalizer import generalize_entry

        entry = {
            "message": "Error in /Users/foo/app/src/main.ts at port 8080",
            "command": "npm test",
            "importance": 0.8,
        }
        result = generalize_entry(entry)
        assert "generalized_message" in result
        assert "/Users/foo/" not in result["generalized_message"]
        assert result["importance"] == 0.8

    def test_generalize_home_linux(self):
        from tip_generalizer import generalize_text

        result = generalize_text("/home/ubuntu/app/main.py")
        assert "/home/ubuntu/" not in result
        assert "{user_home}/" in result

    def test_generalize_ip_address(self):
        from tip_generalizer import generalize_text

        result = generalize_text("connecting to 192.168.1.100")
        assert "192.168.1.100" not in result
        assert "{ip}" in result
