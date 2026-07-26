# -*- coding: utf-8 -*-
import sys, json
try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen

def run(script_path, description="exec via py", use_transaction=False):
    with open(script_path, "rb") as f:
        code = f.read().decode("utf-8")
    payload = json.dumps({
        "code": code,
        "description": description,
        "use_transaction": use_transaction
    }).encode("utf-8")
    req = Request("http://localhost:48884/revit_mcp/execute_code/",
                  data=payload,
                  headers={"Content-Type": "application/json"})
    resp = urlopen(req)
    res = json.loads(resp.read().decode("utf-8"))
    out = res.get("output", "")
    print(out)
    if res.get("status") != "success":
        print("ERROR:", res.get("error"))

if __name__ == "__main__":
    path = sys.argv[1]
    desc = sys.argv[2] if len(sys.argv) > 2 else "exec"
    tx = "--tx" in sys.argv
    run(path, desc, tx)
