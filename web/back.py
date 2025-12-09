from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import sys
import pathlib
import time

app = Flask(__name__, static_folder='.')
CORS(app)

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]  # /home/.../PI
SCRIPT_PATH = PROJECT_ROOT / "request_for_YPI" / "render_document.py"
ALLOWED_ROOT = (PROJECT_ROOT / "request_for_YPI").resolve()


@app.route('/')
def index():
    # main UI
    return send_from_directory(str(pathlib.Path(__file__).parent), 'result.html')


@app.route('/markdown_view')
def markdown_view():
    # alternate page that directly shows markdown (result_markdown.html)
    return send_from_directory(str(pathlib.Path(__file__).parent), 'result_markdown.html')


@app.route('/run', methods=['POST'])
def run_indicator():
    data = request.get_json() or {}
    indicator = data.get("indicator")
    if not indicator:
        return jsonify({"error": "Missing indicator"}), 400

    indicator_rel = pathlib.Path(indicator)
    indicator_path = (PROJECT_ROOT / indicator_rel).resolve()
    # security: ensure path is inside request_for_YPI
    if not str(indicator_path).startswith(str(ALLOWED_ROOT)):
        return jsonify({"error": "Indicator path not allowed"}), 400

    # build command to run render_document.py
    cmd = [sys.executable, str(SCRIPT_PATH), str(indicator_rel)]
    if data.get("country"):
        cmd += ["--country", str(data["country"])]
    if data.get("domain"):
        cmd += ["--domain", str(data["domain"])]
    if data.get("asn"):
        cmd += ["--asn", str(data["asn"])]

    env = os.environ.copy()
    env["IYP_THINKING"] = "1" if data.get("thinking") else "0"
    env["IYP_SOURCE"] = "1" if data.get("iyp_source") else "0"

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(PROJECT_ROOT), timeout=300)
    except subprocess.TimeoutExpired as e:
        return jsonify({"error": "timeout", "details": str(e)}), 504
    except Exception as e:
        return jsonify({"error": "execution failed", "details": str(e)}), 500

    # gather markdown files in the indicator folder
    md_list = []
    latest_markdown = None
    latest_markdown_content = None
    try:
        if indicator_path.is_dir():
            files = [p for p in indicator_path.glob("*.md") if p.is_file()]
            files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            md_list = [p.name for p in files]
            if files:
                latest_markdown = (indicator_rel / files[0].name).as_posix()
                try:
                    latest_markdown_content = files[0].read_text(encoding="utf-8")
                except Exception:
                    latest_markdown_content = None
    except Exception:
        # ignore read errors but include empty results
        pass

    return jsonify({
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "markdown_files": md_list,
        "indicator": str(indicator_rel),
        "latest_markdown": latest_markdown,
        "latest_markdown_content": latest_markdown_content
    })


@app.route('/markdown', methods=['GET'])
def get_markdown():
    rel = request.args.get("path")
    fname = request.args.get("file")
    if not rel or not fname:
        return jsonify({"error": "Missing path or file"}), 400

    target_dir = (PROJECT_ROOT / pathlib.Path(rel)).resolve()
    # security check
    if not str(target_dir).startswith(str(ALLOWED_ROOT)):
        return jsonify({"error": "Path not allowed"}), 400

    target_file = (target_dir / fname).resolve()
    if not str(target_file).startswith(str(ALLOWED_ROOT)):
        return jsonify({"error": "File not allowed"}), 400
    if not target_file.is_file():
        return jsonify({"error": "File not found"}), 404

    try:
        content = target_file.read_text(encoding="utf-8")
    except Exception as e:
        return jsonify({"error": "read_failed", "details": str(e)}), 500

    return jsonify({"path": str(target_file.relative_to(PROJECT_ROOT)), "content": content})


if __name__ == "__main__":
    # run from project root venv
    app.run(host="0.0.0.0", port=5000, debug=True)