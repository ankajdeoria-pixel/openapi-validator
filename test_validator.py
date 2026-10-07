import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V = ROOT / "validator.py"
R = ROOT / "rules.yaml"


def run(p, r=R):
    return subprocess.run(
        [sys.executable, str(V), str(p), str(r)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def put(t, s):
    p = t / "openapi.yaml"
    p.write_text(s)
    return p


def test_valid():
    r = run(ROOT / "openapi.yaml")
    assert r.returncode == 0, r.stdout + r.stderr


def test_duplicate(tmp_path):
    p = put(
        tmp_path,
        """openapi: 3.0.3
components:
  securitySchemes:
    BearerAuth:
      type: http
    BearerAuth:
      type: http
""",
    )
    r = run(p)
    assert r.returncode == 1
    assert "AUTH-008" in r.stdout


def test_malformed(tmp_path):
    p = put(tmp_path, "openapi: [3.0.3\n")
    r = run(p)
    assert r.returncode == 1
    assert "Invalid OpenAPI YAML" in r.stderr


def test_failures(tmp_path):
    p = put(
        tmp_path,
        """openapi: 3.0.3
info:
  title: Bad
  version: 1
paths:
  /users:
    get:
      responses:
        "200": {description: ok}
components: {}
""",
    )
    r = run(p)
    assert r.returncode == 1
    assert "AUTH-003" in r.stdout
    assert "AUTH-004" in r.stdout
    assert "AUTH-009" in r.stdout
    assert "AUTH-012" in r.stdout


def test_missing_file(tmp_path):
    r = run(tmp_path / "missing.yaml")
    assert r.returncode == 2
    assert "file not found" in r.stderr.lower()
