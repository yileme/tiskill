"""Run browser regressions with disposable CAT data. Requires installed Playwright/Chrome."""
import os
from pathlib import Path
import subprocess
import tempfile
import threading
from cat import server


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / ".ekko-tmp/browser-tests"
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output) as temp:
        server.DATA = Path(temp)
        data = server.initial()
        data["segments"] = [dict(id=str(i),source=source,target="Translation "+str(i),status="draft",version=1)
                            for i,source in enumerate(["第一段原文", "第二段原文"],1)]
        data["history"] = {"1":[{"target":"","status":"empty"}]}
        server.write_data(data)
        http = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        env = {**os.environ,"CAT_FIXTURE_URL":f"http://127.0.0.1:{http.server_port}","CAT_TEST_OUTPUT":str(output)}
        try:
            for name in ["evidence", "layout", "chat", "terminology"]:
                subprocess.run(["node",f"cat/test_{name}.cjs"],env=env,cwd=root,check=True,timeout=120)
        finally:
            http.shutdown();http.server_close()

if __name__ == "__main__": main()
