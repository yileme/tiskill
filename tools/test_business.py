import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("business",ROOT/"skills/tis-client-service/scripts/business.py")
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)

def f(value,state="confirmed"):
    return {"value":value,"state":state,"source":{"message":"synthetic-test-only","excerpt":"Synthetic fixture, not a customer order"}}

def line():
    return {"id":"translation","coverage":f(["doc-main-translation"]),"included_pm":f(False),"pricing":{"quantity":f("1000"),"unit":f("word"),"rate":f("120"),"rate_unit":f("1000_word"),"basis":f({"side":"source","spaces":"excluded","method":"synthetic word count"})}}

def draft():
    return {"schema":1,"id":"synthetic","status":"precontract_draft","service":"translation","facts":{k:f("explicitly agreed or not applicable in synthetic fixture") for k in b.FIELDS},"conflicts":[],"decisions":[],"quote":{"currency":f("CNY"),"minor_units":f(2),"scopes":[{"id":"main","model":"itemized","lines":[line()]}],"pm":[],"adjustments":[]}}

class Business(unittest.TestCase):
    def test_thousand_word_rounding(self):
        d=draft();self.assertEqual(b.calculate(d)["total"],"120.00")
        p=d["quote"]["scopes"][0]["lines"][0]["pricing"];p.update(quantity=f("1"),rate=f("1.005"),rate_unit=f("word"))
        self.assertEqual(b.calculate(d)["total"],"1.01")
    def test_missing_and_conflicts(self):
        for change in [lambda d:d["facts"].pop("payment"),lambda d:d["conflicts"].append(f("date conflict")),lambda d:d["quote"]["scopes"][0]["lines"][0]["pricing"].update(rate=b.unknown())]:
            d=draft();change(d);self.assertIsNone(b.calculate(d)["total"])
    def test_proposed_is_not_final(self):
        d=draft();d["quote"]["scopes"][0]["lines"][0]["pricing"]["rate"]["state"]="proposed"
        self.assertEqual(b.calculate(d)["known_subtotal"],"120.00");self.assertIsNone(b.calculate(d)["total"])
    def test_invalid_numbers(self):
        for n in ["NaN","Infinity","-1",1.2,True,"1e999","not-number"]:
            with self.subTest(n=n),self.assertRaises(ValueError): b.number(n)
    def test_units_and_basis(self):
        for update in [{"rate_unit":f("page")},{"basis":f({"side":"both"})},{"unit":f("words")}]:
            d=draft();d["quote"]["scopes"][0]["lines"][0]["pricing"].update(update)
            with self.assertRaises(ValueError): b.calculate(d)
    def test_pm(self):
        d=draft();d["quote"]["pm"]=[{"id":"pm","basis":f(["translation"]),"percent":f("10")}]
        self.assertEqual(b.calculate(d)["total"],"132.00")
        for basis in [["pm"],["tax"],["translation","translation"]]:
            x=copy.deepcopy(d);x["quote"]["pm"][0]["basis"]=f(basis)
            with self.assertRaises(ValueError): b.calculate(x)
        d["quote"]["scopes"][0]["lines"][0]["included_pm"]=f(True)
        with self.assertRaises(ValueError): b.calculate(d)
    def test_duplicate_model_coverage_pm(self):
        d=draft();d["quote"]["scopes"].append(copy.deepcopy(d["quote"]["scopes"][0]))
        with self.assertRaises(ValueError): b.calculate(d)
        d["quote"]["scopes"][1]["id"]="other"
        with self.assertRaises(ValueError): b.calculate(d)
        d=draft();d["quote"]["pm"]=[{"id":k,"basis":f(["translation"]),"percent":f("10")} for k in ["pm1","pm2"]]
        with self.assertRaises(ValueError): b.calculate(d)
    def test_coefficients_additive(self):
        d=draft();s=d["quote"]["scopes"][0];s["model"]="coefficient";l=s["lines"][0]
        l["factors"]=f({"difficulty":{"category":"mid","value":"1"},"qualification":{"category":"junior","value":"1"},"translation_type":{"category":"human","value":"1"},"process":{"initial_self":"1","bilingual":".5","pm":".1"}})
        l["included_pm"]=f(True)
        self.assertEqual(b.calculate(d)["total"],"192.00")
        d["quote"]["pm"]=[{"id":"pm","basis":f(["translation"]),"percent":f("10")}]
        with self.assertRaises(ValueError): b.calculate(d)
        d["quote"]["pm"]=[];l["factors"]["value"]["difficulty"]["value"]="2"
        with self.assertRaises(ValueError): b.calculate(d)
    def test_localization(self):
        d=draft();s=d["quote"]["scopes"][0];s["model"]="localization";l=s["lines"][0]
        l["weights"]=f([{"group":"new","count":"500","weight":"1"},{"group":"repeat","count":"1000","weight":".5"}])
        self.assertEqual(b.calculate(d)["total"],"120.00")
        l["pricing"]["quantity"]=b.unknown();self.assertEqual(b.calculate(d)["total"],"120.00")
        l["pricing"]["quantity"]=f("2000")
        with self.assertRaises(ValueError): b.calculate(d)
    def test_interpreting(self):
        d=draft();d["service"]="interpreting";s=d["quote"]["scopes"][0];s["model"]="interpreting";l=s["lines"][0]
        l["pricing"]={"quantity":f("2"),"unit":f("person_half_day"),"rate":f("800"),"rate_unit":f("person_half_day"),"basis":f("per interpreter; one negotiated session")}
        l["time"]=f({"people":"2","sessions_per_person":"1","unit":"person_half_day","hours_per_unit":"3","agreement":"synthetic explicit agreement"})
        self.assertEqual(b.calculate(d)["total"],"1600.00")
        l["time"]["value"]["days"]="2"
        with self.assertRaises(ValueError): b.calculate(d)
        l["time"]=b.unknown();self.assertIsNone(b.calculate(d)["total"]);self.assertIsNone(b.calculate(d)["lines"]["translation"])
    def test_pending_costs_and_adjustments(self):
        d=draft();d["quote"]["adjustments"]=[{"id":"travel","kind":"extra","amount":b.unknown(),"rule":f("actual travel expense awaiting quote")}]
        x=b.calculate(d);self.assertEqual(x["known_subtotal"],"120.00");self.assertIsNone(x["total"]);self.assertIsNone(x["lines"]["travel"])
        d["quote"]["adjustments"]=[{"id":"discount","kind":"discount","amount":f("20"),"rule":f("fixed agreed deduction")}]
        self.assertEqual(b.calculate(d)["total"],"100.00")
        d["quote"]["adjustments"][0]["amount"]=f("200")
        with self.assertRaises(ValueError): b.calculate(d)
    def test_fact_evidence(self):
        d=draft();d["facts"]["client"]["source"]={"message":None,"excerpt":None}
        with self.assertRaises(ValueError): b.calculate(d)
    def test_render_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="business-test-") as td:
            root=Path(td);d=draft();d["facts"]["payment"]=b.unknown()
            with self.assertRaises(ValueError): b.create(root,d)
            p=b.create(root,d,True)
            self.assertIn("synthetic-test-only",(p/"briefs/brief_V01.md").read_text())
            self.assertIn("待确认",(p/"briefs/brief_V01.md").read_text())
            self.assertEqual(json.loads((p/"briefs/brief_V01.json").read_text())["status"],"precontract_draft")
            self.assertTrue((p/"originals/source").is_dir())
            with self.assertRaises(ValueError): b.create(root,d,True)
            d["id"]="../outside"
            with self.assertRaises(ValueError): b.create(root,d,True)
    def test_blank_template_refused(self):
        d=json.loads((ROOT/"skills/tis-client-service/templates/brief.json").read_text())
        with tempfile.TemporaryDirectory(prefix="business-test-") as td:
            with self.assertRaises(ValueError): b.create(Path(td),d,True)
            self.assertFalse((Path(td)/"06-客户项目").exists())

    def test_wrong_model_fields(self):
        d=draft();d["quote"]["scopes"][0]["lines"][0]["factors"]=f({})
        with self.assertRaises(ValueError): b.calculate(d)

    def test_symlinks_and_library(self):
        with tempfile.TemporaryDirectory(prefix="business-test-") as td:
            root=Path(td);b.init_library(root,True);b.init_library(root,True)
            self.assertEqual([p.name for p in (root/"06-客户项目").iterdir()],["索引.md"])
            (root/"06-客户项目/linked").symlink_to(root,target_is_directory=True)
            d=draft();d["id"]="linked"
            with self.assertRaises(ValueError): b.create(root,d,True)
            (root/"05-业务知识/业务知识.md").write_text("user edit")
            with self.assertRaises(ValueError): b.init_library(root,True)
            self.assertEqual((root/"05-业务知识/业务知识.md").read_text(),"user edit")

if __name__=="__main__": unittest.main()
