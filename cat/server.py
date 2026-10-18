#!/usr/bin/env python3
"""Loopback-only, local-first CAT editor with an agent translation conversation."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import tempfile
from threading import RLock
from uuid import uuid4
from urllib.error import URLError, HTTPError
from urllib.parse import parse_qs, quote, urlsplit, unquote
from urllib.request import Request, urlopen

try:  # imported as cat.server (tests) or executed directly as cat/server.py
    from . import exports, agent, resources
except ImportError:
    import exports, agent, resources

PUBLIC = Path(__file__).with_name("public")
DEFAULT_CSP = "default-src 'self'; script-src 'self'; style-src 'self'; base-uri 'none'; form-action 'self'"
# Exported HTML carries its own inline stylesheet and is meant to be opened or printed.
EXPORT_CSP = "default-src 'none'; style-src 'unsafe-inline'"
EXPORT_TYPES = {
    ".md": "text/markdown; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
DATA = Path(os.environ.get("TIS_CAT_DATA", str(Path.home() / ".tiskill/cat")))
LOCK = RLock()
MAX_BODY = 250_000


def initial():
    return {"id": "local", "title": "我的翻译练习", "revision": 0, "segments": [], "history": {}, "chats": {}}


def read_data():
    path = DATA / "project.json"
    return json.loads(path.read_text()) if path.exists() else initial()


def write_data(data):
    DATA.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".project-", dir=DATA)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, DATA / "project.json")
    finally:
        if os.path.exists(name):
            os.unlink(name)


def public(data):
    return {key: deepcopy(data[key]) for key in ("id", "title", "revision", "segments")}


def lookup(data, ident):
    return next((s for s in data["segments"] if s["id"] == ident), None)


def change(data, segment, target, status):
    data["history"].setdefault(segment["id"], []).append({key: segment[key] for key in ("target", "status")})
    segment["target"], segment["status"] = target, status
    segment["version"] += 1
    data["revision"] += 1
    write_data(data)
    return {"segment": deepcopy(segment)}


def propose(segment, message, history, action="discussion"):
    result = agent.respond(segment, message, history, action)
    after = result.get("after")
    proposal = None
    if isinstance(after, str) and after.strip() and after.strip() != segment["target"].strip() and len(after) <= 20_000:
        proposal = {"segmentId": segment["id"], "expectedVersion": segment["version"],
                    "before": segment["target"], "after": after.strip(), "reason": str(result.get("reason") or "根据本轮讨论调整译文")[:1000]}
    return {"reply": result["reply"][:5000], "proposal": proposal}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print("%s %s" % (self.address_string(), format % args))

    def send(self, code, value, content_type="application/json; charset=utf-8", filename=None, csp=DEFAULT_CSP):
        body = (json.dumps(value, ensure_ascii=False).encode() if isinstance(value, (dict, list)) else value)
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if csp:
            self.send_header("Content-Security-Policy", csp)
        if filename:
            # ASCII fallback plus RFC 5987 form, so Chinese titles survive the download.
            self.send_header("Content-Disposition",
                             'attachment; filename="export%s"; filename*=UTF-8\'\'%s'
                             % (Path(filename).suffix, quote(filename)))
        self.end_headers()
        self.wfile.write(body)

    def fail(self, status, message):
        self.send(status, {"error": message})

    def parse(self):
        size = int(self.headers.get("Content-Length", "0"))
        if size < 1 or size > MAX_BODY:
            raise ValueError("请求内容为空或过长。")
        data = json.loads(self.rfile.read(size))
        if not isinstance(data, dict):
            raise ValueError("请求必须是对象。")
        return data

    def allowed(self):
        host = self.headers.get("Host", "")
        origin = self.headers.get("Origin")
        valid = {"127.0.0.1", "localhost"}
        if urlsplit("http://" + host).hostname not in valid:
            self.fail(403, "只接受本机访问。")
            return False
        if self.command != "GET" and origin != "http://" + host:
            self.fail(403, "来源校验失败。")
            return False
        return True

    def do_GET(self):
        if not self.allowed(): return
        path = urlsplit(self.path).path
        if path in ("/api/libraries", "/api/library.csv") or (path.startswith("/api/libraries/") and path.endswith("/export")):
            try:
                with LOCK:
                    project=read_data()["id"]
                    if path=="/api/libraries": self.send(200,resources.list_libraries(DATA,project))
                    else:
                        ident=(parse_qs(urlsplit(self.path).query).get("id") or [""])[0] if path == "/api/library.csv" else path.split("/")[-2]
                        self.send(200,resources.export_library(DATA,ident,project),"text/csv; charset=utf-8",filename=ident+".csv")
            except ValueError as error: self.fail(400,str(error))
            return
        if path == "/api/resources":
            q=parse_qs(urlsplit(self.path).query)
            try:
                result=resources.search_resources(DATA, kind=q.get("kind",[""])[0], sourceLocale=q.get("sourceLocale",[""])[0], targetLocale=q.get("targetLocale",[""])[0], query=q.get("query",[""])[0], project=read_data()["id"])
                self.send(200,result)
            except ValueError as error: self.fail(400,str(error))
            return
        details_match = re.fullmatch(r"/api/segments/([^/]+)/details", path)
        if details_match:
            ident = unquote(details_match.group(1))
            with LOCK:
                data = read_data()
                if lookup(data, ident) is None: return self.fail(404, "段落不存在。")
                self.send(200, {"segmentId": ident, "projectId": data["id"],
                               "note": data.get("notes", {}).get(ident, ""),
                               "history": data["history"].get(ident, [])})
            return
        if path == "/api/project":
            with LOCK: self.send(200, public(read_data()))
            return
        if path in ("/api/export.md", "/api/export.html", "/api/export.docx"):
            mode = (parse_qs(urlsplit(self.path).query).get("mode") or ["stacked"])[0]
            if mode not in exports.MODES: return self.fail(400, "导出方式必须是 target、stacked 或 table。")
            with LOCK: doc = read_data()
            suffix = path.rsplit(".", 1)[1]
            if suffix == "md":
                body = exports.export_markdown(doc, mode).encode()
                csp = DEFAULT_CSP
            elif suffix == "html":
                body = exports.export_html(doc, mode).encode()
                csp = EXPORT_CSP
            else:
                body = exports.export_docx(doc, mode)
                csp = None
            self.send(200, body, EXPORT_TYPES["." + suffix], filename=exports.filename(doc, mode, suffix), csp=csp)
            return
        static_files = {"/": "index.html", "/index.html": "index.html", "/style.css": "style.css", "/app.js": "app.js", "/markdown.js": "markdown.js", "/resources.js": "resources.js", "/details.js": "details.js", "/layout.js": "layout.js"}
        if path not in static_files:
            self.fail(404, "页面不存在。")
            return
        file = PUBLIC / static_files[path]
        mime = {".html": "text/html", ".css": "text/css", ".js": "text/javascript"}[file.suffix]
        self.send(200, file.read_bytes(), mime + "; charset=utf-8")

    def do_DELETE(self): self.mutate()

    def do_PATCH(self): self.mutate()
    def do_POST(self): self.mutate()

    def mutate(self):
        if not self.allowed(): return
        try:
            body = self.parse()
            path = urlsplit(self.path).path
            if path == "/api/libraries" and self.command in {"POST","PATCH"}:
                payload=dict(body)
                if "csv" in payload: payload["csvContent"]=payload.pop("csv")
                if "id" in payload: payload["libraryId"]=payload.pop("id")
                with LOCK: result=resources.mount_library(DATA,payload,read_data()["id"])
                self.send(200,result); return
            if path == "/api/resources" and self.command == "PATCH":
                try:
                    with LOCK: result=resources.update_resource(DATA,body,read_data()["id"])
                except resources.ResourceConflict as error: return self.fail(409,str(error))
                self.send(200,result); return
            if path == "/api/resources" and self.command == "POST":
                with LOCK:
                    data=read_data()
                    seg=lookup(data,body.get("segmentId")) if body.get("kind")=="tm" else None
                    result=resources.add_resource(DATA,body,segment=seg,project=data["id"])
                self.send(200,result); return
            if path == "/api/term-search" and self.command == "POST":
                query=body.get("query")
                if not isinstance(query,str) or not 1<=len(query.strip())<=200: raise ValueError("请输入 1–200 字的术语")
                with LOCK:
                    data=read_data(); seg=lookup(data,body.get("segmentId"))
                    snapshot=deepcopy(seg) if seg else {"source":query,"target":""}
                try: result=agent.respond(snapshot,"查询术语："+query,[],"terminology")
                except ValueError as error: return self.fail(503,str(error))
                self.send(200,{"reply":result["reply"]}); return
            if path == "/api/chat" and self.command == "POST":
                ident, message = body.get("segmentId"), body.get("message")
                if not isinstance(message, str) or not 1 <= len(message.strip()) <= 4000:
                    raise ValueError("请输入 1–4000 字的问题。")
                with LOCK:
                    data = read_data(); segment = lookup(data, ident)
                    if segment is None: return self.fail(404, "段落不存在。")
                    snapshot = deepcopy(segment); history = deepcopy(data["chats"].get(ident, []))
                try: result = propose(snapshot, message, history, body.get("action", "discussion"))
                except (URLError, HTTPError, TimeoutError, ValueError) as error: return self.fail(503, str(error) if isinstance(error, ValueError) else "Agent 连接失败，请重试。")
                with LOCK:
                    data = read_data(); data["chats"].setdefault(ident, []).extend([{"role": "user", "text": message}, {"role": "assistant", "text": result["reply"]}]); write_data(data)
                self.send(200, result); return
            with LOCK:
                data = read_data()
                if path == "/api/project" and self.command == "POST":
                    title, segments = body.get("title"), body.get("segments")
                    if not isinstance(title, str) or not 1 <= len(title) <= 120 or not isinstance(segments, list) or not 1 <= len(segments) <= 1000:
                        raise ValueError("请输入标题及 1–1000 个段落。")
                    if data["segments"] and body.get("confirmReplace") is not True:
                        return self.fail(409, "现有文稿需要确认替换。")
                    sources = [s.get("source") if isinstance(s, dict) else None for s in segments]
                    if any(not isinstance(s, str) or not s.strip() or len(s) > 10000 for s in sources):
                        raise ValueError("原文段落必须为非空文本，单段不超过一万字。")
                    doc = initial(); doc["id"] = str(uuid4()); doc["title"] = title.strip(); doc["revision"] = data["revision"] + 1
                    doc["segments"] = [{"id": str(i), "source": s.strip(), "target": "", "status": "empty", "version": 0} for i, s in enumerate(sources, 1)]
                    write_data(doc); self.send(200, public(doc)); return
                note_match = re.fullmatch(r"/api/segments/([^/]+)/note", path)
                if note_match and self.command == "PATCH":
                    ident = unquote(note_match.group(1))
                    if lookup(data, ident) is None: return self.fail(404, "段落不存在。")
                    note, expected = body.get("note"), body.get("expectedNote")
                    if not isinstance(note, str) or len(note) > 5000 or not isinstance(expected, str):
                        raise ValueError("备注必须为不超过 5000 字的文本，并提供原备注。")
                    if (body.get("projectId", data["id"]) != data["id"]
                            or expected != data.get("notes", {}).get(ident, "")):
                        return self.fail(409, "备注或文稿已变化，请重新载入后合并修改。")
                    data.setdefault("notes", {})[ident] = note
                    write_data(data)
                    self.send(200, {"segmentId": ident, "projectId": data["id"], "note": note}); return
                if path.startswith("/api/segments/") and self.command == "PATCH":
                    segment = lookup(data, unquote(path.rsplit("/", 1)[1]))
                    if segment is None: return self.fail(404, "段落不存在。")
                    target, version = body.get("target"), body.get("expectedVersion")
                    if not isinstance(target, str) or len(target) > 20000: raise ValueError("译文长度无效。")
                    if type(version) is not int or version != segment["version"]: return self.fail(409, "译文已变化，请刷新后重试。")
                    status = body.get("status", "draft" if target.strip() else "empty")
                    if status not in ("empty", "draft", "confirmed"): raise ValueError("段落状态无效。")
                    self.send(200, change(data, segment, target, status)); return
                if path == "/api/proposals/apply" and self.command == "POST":
                    proposal = body.get("proposal"); proposal = proposal if isinstance(proposal, dict) else {}
                    segment = lookup(data, proposal.get("segmentId"))
                    if segment is None: return self.fail(404, "段落不存在。")
                    if type(proposal.get("expectedVersion")) is not int or proposal["expectedVersion"] != segment["version"] or proposal.get("before") != segment["target"]:
                        return self.fail(409, "建议已过期，请重新讨论当前译文。")
                    after = proposal.get("after")
                    if not isinstance(after, str) or not after.strip() or len(after) > 20000: raise ValueError("建议译文无效。")
                    self.send(200, change(data, segment, after, "draft")); return
                if path == "/api/undo" and self.command == "POST":
                    segment = lookup(data, body.get("segmentId"))
                    if segment is None: return self.fail(404, "段落不存在。")
                    if type(body.get("expectedVersion")) is not int or body["expectedVersion"] != segment["version"]: return self.fail(409, "译文已变化，请刷新后重试。")
                    history = data["history"].get(segment["id"], [])
                    if not history: return self.fail(409, "没有可撤销的修改。")
                    previous = history.pop(); segment.update(previous); segment["version"] += 1; data["revision"] += 1
                    write_data(data); self.send(200, {"segment": segment}); return
            self.fail(404, "接口不存在。")
        except OSError:
            self.fail(503, "本地存储暂不可用；输入未提交，请保留后重试。")
        except (ValueError, json.JSONDecodeError) as error:
            self.fail(400, str(error))


def main():
    parser = argparse.ArgumentParser(description="Local tiskill CAT editor")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"CAT editor: http://127.0.0.1:{server.server_port} | agent: Codex", flush=True)
    server.serve_forever()


if __name__ == "__main__": main()
