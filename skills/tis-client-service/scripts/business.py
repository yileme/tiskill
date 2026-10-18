#!/usr/bin/env python3
"""Offline, evidence-bearing business drafts. No network or customer-file copying."""
import argparse
import ctypes
import sys
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

BASE = Path(__file__).resolve().parents[1]
FIELDS = "client contact language_direction audience purpose locale deadline timezone source_refs target_refs resources deliverables count_basis process staffing schedule location platform participants background materials preparation technical_test quote_expiry payment revision_rounds cancellation confidentiality ai_permission acceptance storage_rights taxes discount rush".split()
UNITS = {"word", "1000_word", "character", "page", "image", "hour", "item", "person_hour", "person_half_day", "person_day"}
RANGES = {"tech": ("0", ".2"), "terms": ("0", ".1"), "preprocessing": ("0", ".1"), "style": ("0", ".5"), "pm": (".1", ".2"), "initial_self": ("1", "1"), "bilingual": (".2", "1"), "monolingual": (".1", ".5"), "proof": (".05", ".5"), "final": (".05", ".5"), "qa": ("0", ".2"), "tm_maintenance": ("0", ".05")}


def number(x):
    if x is None:
        return None
    if isinstance(x, bool) or not isinstance(x, (str, int, Decimal)):
        raise ValueError("Numbers must be decimal strings or integers")
    try:
        n = Decimal(x)
    except InvalidOperation:
        raise ValueError("Invalid decimal") from None
    if not n.is_finite() or n < 0 or n > Decimal("1e18"):
        raise ValueError("Negative, nonfinite or excessive number")
    return n


def ident(x):
    if not isinstance(x, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", x):
        raise ValueError("Unsafe identifier")
    return x


def fact(x):
    if not isinstance(x, dict) or set(x) != {"value", "state", "source"}:
        raise ValueError("Fact requires value, state, source only")
    if x["state"] not in {"confirmed", "proposed", "pending"}:
        raise ValueError("Invalid fact state")
    s = x["source"]
    if not isinstance(s, dict) or set(s) != {"message", "excerpt"} or any(v is not None and not isinstance(v, str) for v in s.values()):
        raise ValueError("Source requires message and excerpt (null when unavailable)")
    if x["value"] is None and x["state"] != "pending":
        raise ValueError("Unknown must be pending")
    if x["state"] != "pending" and not all(s.values()):
        raise ValueError("Known/proposed facts require evidence")
    return x["value"]


def unknown():
    return {"value": None, "state": "pending", "source": {"message": None, "excerpt": None}}


def validate(d):
    if not isinstance(d, dict) or d.get("schema") != 1 or d.get("status") != "precontract_draft":
        raise ValueError("schema 1 and precontract_draft required")
    ident(d.get("id"))
    if d.get("service") not in {"translation", "interpreting", "localization"}:
        raise ValueError("Unknown service")
    if not isinstance(d.get("facts"), dict):
        raise ValueError("facts required")
    for v in d["facts"].values(): fact(v)
    for k in FIELDS: d["facts"].setdefault(k, unknown())
    for key in ("conflicts", "decisions"):
        if not isinstance(d.get(key), list): raise ValueError(key + " must be list")
        for v in d[key]: fact(v)
    q = d.get("quote")
    if not isinstance(q, dict) or set(q) != {"currency", "minor_units", "scopes", "pm", "adjustments"}: raise ValueError("Invalid quote keys")
    c = fact(q["currency"])
    if c is not None and (not isinstance(c, str) or not re.fullmatch("[A-Z]{3}", c)): raise ValueError("Currency must be ISO-style code")
    m = fact(q["minor_units"])
    if m is not None and (type(m) is not int or m not in range(5)): raise ValueError("minor_units 0..4")
    for key in ("scopes", "pm", "adjustments"):
        if not isinstance(q[key], list): raise ValueError(key + " must be list")
    return d


def calculate(d):
    validate(d)
    q = d["quote"]; pending = []; rows = {}; coverage = set(); scopes = set()
    def val(f, label):
        v = fact(f)
        if v is None or f["state"] != "confirmed": pending.append(label)
        return v
    currency = val(q["currency"], "currency")
    minor = val(q["minor_units"], "minor_units")
    quantum = Decimal(1).scaleb(-minor) if minor is not None else None
    def rounded(n): return n.quantize(quantum, rounding=ROUND_HALF_UP) if n is not None and quantum is not None else None
    def num(f, label): return number(val(f, label))
    def put(key, amount, embedded=False, kind="work"):
        ident(key)
        if key in rows: raise ValueError("Duplicate line id")
        rows[key] = {"amount": rounded(amount), "embedded_pm": embedded, "kind": kind}
    def workload(spec):
        if set(spec) != {"quantity", "unit", "rate", "rate_unit", "basis"}: raise ValueError("Invalid workload keys")
        qty = num(spec["quantity"], "quantity"); rate = num(spec["rate"], "rate")
        unit = val(spec["unit"], "unit"); ru = val(spec["rate_unit"], "rate_unit")
        basis = val(spec["basis"], "basis")
        for u in [unit, ru]:
            if u is not None and u not in UNITS: raise ValueError("Unknown unit")
        factor = Decimal(1)
        if unit is not None and ru is not None and unit != ru:
            if unit == "word" and ru == "1000_word": factor = Decimal(".001")
            else: raise ValueError("Unit mismatch")
        if unit in {"word", "1000_word", "character"} and basis is not None:
            if not isinstance(basis, dict) or set(basis) != {"side", "spaces", "method"} or basis["side"] not in {"source", "target"} or basis["spaces"] not in {"included", "excluded", "not_applicable"} or not basis["method"]:
                raise ValueError("Count basis requires source/target, spaces and method")
        return qty * rate * factor if None not in (qty, rate, unit, ru, basis) else None
    for s in q["scopes"]:
        if set(s) != {"id", "model", "lines"}: raise ValueError("Invalid scope keys")
        ident(s["id"])
        if s["id"] in scopes: raise ValueError("Multiple models for same scope")
        scopes.add(s["id"])
        model = s["model"]
        if model not in {"itemized", "coefficient", "localization", "interpreting"}: raise ValueError("Unknown model")
        if not isinstance(s["lines"], list) or not s["lines"]: pending.append("empty scope")
        if model == "coefficient" and len(s["lines"]) != 1: raise ValueError("One coefficient line per scope")
        for line in s["lines"]:
            allowed = {"id", "coverage", "pricing", "included_pm", "factors", "weights", "time"}
            if set(line) - allowed: raise ValueError("Unknown line fields")
            for key, owner in [("factors", "coefficient"), ("weights", "localization"), ("time", "interpreting")]:
                if key in line and model != owner: raise ValueError("Model-specific field on wrong model")
            cov = val(line["coverage"], "coverage")
            if cov is not None:
                if not isinstance(cov, list) or not cov or any(not isinstance(x, str) or not x for x in cov): raise ValueError("coverage must list unique work keys")
                if len(set(cov)) != len(cov) or coverage.intersection(cov): raise ValueError("Duplicate charged coverage")
                coverage.update(cov)
            embedded = val(line["included_pm"], "included_pm")
            if embedded is not None and type(embedded) is not bool: raise ValueError("included_pm must be boolean")
            price = dict(line["pricing"])
            if model == "localization" and "weights" in line:
                weights = val(line["weights"], "weights"); weighted = None
                if weights is not None:
                    if not isinstance(weights, list) or not weights: raise ValueError("weights required")
                    weighted = Decimal(0); groups = set()
                    for w in weights:
                        if set(w) != {"group", "count", "weight"} or w["group"] in groups: raise ValueError("Invalid weight group")
                        groups.add(w["group"]); count=number(w["count"]); weight=number(w["weight"])
                        if count is None or weight is None: weighted=None; break
                        weighted += count * weight
                if fact(price["unit"]) != "word": raise ValueError("Weighted quantity must be words")
                supplied = number(fact(price["quantity"]))
                if supplied is not None and weighted != supplied: raise ValueError("Weighted count conflicts")
                price["quantity"] = dict(line.get("weights", unknown()), value=str(weighted) if weighted is not None else None)
            if model == "interpreting":
                t = val(line.get("time", unknown()), "negotiated time")
                if t is not None:
                    if not isinstance(t, dict) or set(t) != {"people", "sessions_per_person", "unit", "hours_per_unit", "agreement"}: raise ValueError("Time keys; no extra days multiplier")
                    people=number(t["people"]); sessions=number(t["sessions_per_person"]); hours=number(t["hours_per_unit"])
                    if people is None or sessions is None or hours is None or hours == 0 or people == 0 or people != people.to_integral_value() or not t["agreement"]: raise ValueError("Negotiated people/time/hours/agreement required")
                    if t["unit"] not in {"person_hour", "person_half_day", "person_day"} or fact(price["unit"]) != t["unit"]: raise ValueError("Time unit mismatch")
                    if t["unit"] == "person_hour" and hours != 1: raise ValueError("Hour must equal one hour")
                    if number(fact(price["quantity"])) != people * sessions: raise ValueError("Person-time count mismatch")
            amount = workload(price)
            if model == "interpreting" and t is None: amount = None
            if model == "coefficient":
                f = val(line.get("factors", unknown()), "coefficients")
                if f is None: amount = None
                else:
                    if set(f) != {"difficulty", "qualification", "translation_type", "process"}: raise ValueError("Invalid coefficients")
                    ranges = {"difficulty": {"low": ("0","1"), "mid":("1","1"), "high":("1","2")}, "qualification": {"junior":("1","1"), "intermediate":("1","3"), "associate":("3","5"), "senior":("5","10")}, "translation_type":{"mtpe":(".3","1"), "human":("1","1")}}
                    mult=Decimal(1)
                    for k, table in ranges.items():
                        pair=f[k]
                        if set(pair) != {"category", "value"} or pair["category"] not in table: raise ValueError("Coefficient category")
                        n=number(pair["value"]); lo,hi=map(Decimal,table[pair["category"]])
                        if n is None or not lo <= n <= hi: raise ValueError("Coefficient outside user excerpt range")
                        mult *= n
                    proc=f["process"]
                    if not isinstance(proc,dict) or not proc: raise ValueError("Explicit process coefficients required")
                    total=Decimal(0)
                    for k,v in proc.items():
                        if k not in RANGES: raise ValueError("Unknown process coefficient")
                        n=number(v);lo,hi=map(Decimal,RANGES[k])
                        if n is None or not lo <= n <= hi: raise ValueError("Process coefficient range")
                        total += n
                    if "pm" in proc and embedded is not True: raise ValueError("Coefficient PM must be marked included")
                    if amount is not None: amount *= mult * total
            put(line["id"], amount, embedded)
    work_ids=set(rows)
    for pm in q["pm"]:
        if set(pm) != {"id", "basis", "percent"}: raise ValueError("Invalid PM fields")
        basis=val(pm["basis"], "PM basis"); percent=num(pm["percent"], "PM percent")
        amount=None
        if basis is not None:
            if not isinstance(basis,list) or not basis or len(set(basis))!=len(basis) or any(k not in work_ids or rows[k]["embedded_pm"] is not False for k in basis): raise ValueError("PM basis includes PM/tax/unknown/embedded PM")
            if any(rows[k].get("pm_charged") for k in basis): raise ValueError("Repeated PM basis")
            for k in basis: rows[k]["pm_charged"]=True
            values=[rows[k]["amount"] for k in basis]
            if percent is not None and all(x is not None for x in values): amount=sum(values)*percent/100
        put(pm["id"],amount,True,"pm")
    for a in q["adjustments"]:
        if set(a) != {"id", "kind", "amount", "rule"}: raise ValueError("Adjustment requires explicit amount and rule")
        kind=a["kind"]
        if kind not in {"tax", "discount", "rush", "condition", "extra"}: raise ValueError("Unknown adjustment")
        amount=num(a["amount"],kind); rule=val(a["rule"],kind+" rule")
        put(a["id"], amount if rule is not None else None, True, kind)
    for k,v in d["facts"].items():
        if v["state"] != "confirmed" or v["value"] is None: pending.append(k)
    if d["conflicts"]: pending.append("unresolved conflicts")
    if not rows: pending.append("no priced scope")
    if any(x["amount"] is None for x in rows.values()): pending.append("unpriced lines")
    subtotal=sum(((-1 if v["kind"]=="discount" else 1)*v["amount"] for v in rows.values() if v["amount"] is not None),Decimal(0))
    if subtotal < 0: raise ValueError("Discount exceeds known subtotal")
    return {"currency":currency,"status":"provisional" if pending else "priced_draft_not_contract", "lines":{k: str(v["amount"]) if v["amount"] is not None else None for k,v in rows.items()},"known_subtotal":str(subtotal) if quantum is not None else None,"total": None if pending else str(subtotal),"pending":sorted(set(pending))}


def show(v):
    return json.dumps(v,ensure_ascii=False) if v is not None else "待确认 / null"


def render(d):
    result=calculate(d)
    evidence=[]
    for k,v in d["facts"].items(): evidence.append(f"- {k}: {show(v['value'])} [{v['state']}] — {show(v['source'])}")
    brief="# 项目简报 V01\n\n状态：precontract_draft；未接受，报价不等于合同。\n\n"+"\n".join(evidence)
    quote="# 报价 V01\n\n未签约草案。已知小计不代表最终应付总额。\n\n```json\n"+json.dumps(result,ensure_ascii=False,indent=2)+"\n```\n\n## 计价事实、口径和来源\n\n```json\n"+json.dumps(d["quote"],ensure_ascii=False,indent=2)+"\n```"
    log="# 变更与决策 V01\n\n不从生成文件推定任何客户接受或变更批准。\n\n"+show({k:d[k] for k in ["conflicts","decisions"]})
    comm="# 沟通草稿（未发送）\n\n## 询价回复与缺项澄清\n\n感谢咨询。以下信息仍需确认："+", ".join(result["pending"])+"。\n\n## 报价说明\n\n请核对附件报价V01的工作范围、计数口径与未定费用。该文件是讨论草案，未形成接受记录。\n\n## 范围变更\n\n拟议变更、原范围、费用与时间影响及同意人：待确认；获各方同意后另存修订版。\n\n## 交付与验收\n\n实际交付文件、核验结果、验收人及期限：待确认。不得提前声称已经交付。\n\n## 结项\n\n反馈、修正、付款、资料保存/归还/销毁及权利限制：待确认。\n"
    return {"briefs/brief_V01.md":brief+"\n", "quotations/quote_V01.md":quote+"\n", "correspondence/drafts_V01.md":comm, "decisions/change_log_V01.md":log+"\n", "briefs/brief_V01.json":json.dumps(d,ensure_ascii=False,indent=2)+"\n"}


def root_from_config(config):
    p=Path(json.loads(Path(config).expanduser().read_text())["path"]).expanduser()
    if not p.is_absolute() or not p.is_dir(): raise ValueError("Existing absolute library path required")
    # Refuse any symlink in root path, not just final component.
    if any(x.is_symlink() for x in [p,*p.parents]): raise ValueError("Symlink library root")
    return p.resolve()


@contextmanager
def lock(root):
    p=root/".tiskill-business.lock"
    fd=os.open(p,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,"w") as f:
        fcntl.flock(f,fcntl.LOCK_EX); yield


def publish(root,name,files,folders=()):
    target=root/name
    if target.exists() or target.is_symlink(): raise ValueError("Destination exists; never overwrite")
    stage=Path(tempfile.mkdtemp(prefix=".business-",dir=root))
    try:
        for folder in folders: (stage/folder).mkdir(parents=True,exist_ok=True)
        for rel,text in files.items():
            p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding="utf-8")
        # Under shared lock; os.rename is atomic on this local filesystem.
        if target.exists() or target.is_symlink(): raise ValueError("Destination collision")
        if sys.platform == "darwin":
            libc = ctypes.CDLL(None, use_errno=True)
            rename = libc.renamex_np
            rename.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
            rename.restype = ctypes.c_int
            if rename(os.fsencode(stage), os.fsencode(target), 4):
                raise OSError(ctypes.get_errno(), "Exclusive atomic publication failed")
        elif sys.platform.startswith("linux"):
            libc = ctypes.CDLL(None, use_errno=True)
            if not hasattr(libc, "renameat2"): raise ValueError("Exclusive atomic rename unavailable")
            rename = libc.renameat2
            rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
            rename.restype = ctypes.c_int
            if rename(-100, os.fsencode(stage), -100, os.fsencode(target), 1):
                raise OSError(ctypes.get_errno(), "Exclusive atomic publication failed")
        else:
            raise ValueError("Atomic project creation supports macOS/Linux only")
    finally:
        if stage.exists(): shutil.rmtree(stage)
    return target


def create(root,d,confirm=False):
    if not confirm: raise ValueError("Existing user authorization required (--confirm)")
    files=render(d); ident(d["id"])
    if not any(v["value"] is not None and v["state"] == "confirmed" and all(v["source"].values()) for v in d["facts"].values()):
        raise ValueError("Blank templates cannot create customer projects")
    with lock(root):
        folder=root/"06-客户项目"
        if folder.is_symlink(): raise ValueError("Symlink project folder")
        folder.mkdir(exist_ok=True)
        return publish(folder,d["id"],files,["originals/source","originals/target","resources","deliverables"])


def init_library(root,confirm=False):
    if not confirm: raise ValueError("Existing authorization required (--confirm)")
    with lock(root):
        knowledge={"业务知识.md":(BASE/"references/business-knowledge.md").read_text(),"来源.md":(BASE/"references/sources.md").read_text(),"简报模板.md":(BASE/"templates/brief.md").read_text(),"简报模板.json":(BASE/"templates/brief.json").read_text(),"索引.md":"# 业务知识\n\n[[业务知识]] · [[来源]] · [[简报模板]]\n"}
        for name,files in [("05-业务知识",knowledge),("06-客户项目",{"索引.md":"# 客户项目\n\n尚未创建真实客户项目。授权后从真实对话建立 precontract_draft；报价不代表合同。\n"})]:
            p=root/name
            if p.is_symlink(): raise ValueError("Symlink folder")
            if p.exists():
                # Idempotent only if owned expected files match; preserve all other content.
                if any(not (p/k).is_file() or (p/k).is_symlink() or (p/k).read_text()!=v for k,v in files.items()): raise ValueError("Existing library content differs; preserve and review")
            else: publish(root,name,files)
    return root


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=["validate","preview","quote","brief","create","init-library"])
    parser.add_argument("--input",type=Path)
    parser.add_argument("--config",type=Path,default=Path.home()/".tiskill/library.json")
    parser.add_argument("--confirm",action="store_true")
    a=parser.parse_args()
    try:
        if a.command=="init-library": print(init_library(root_from_config(a.config),a.confirm));return
        if not a.input: raise ValueError("--input required")
        d=json.loads(a.input.read_text())
        if a.command=="create": print(create(root_from_config(a.config),d,a.confirm))
        elif a.command in {"validate","preview"}: print(json.dumps(calculate(d),ensure_ascii=False,indent=2))
        else: print(render(d)["quotations/quote_V01.md" if a.command=="quote" else "briefs/brief_V01.md"])
    except (ValueError,KeyError,TypeError,OSError,InvalidOperation) as e: parser.exit(2,str(e)+"\n")

if __name__=="__main__": main()
