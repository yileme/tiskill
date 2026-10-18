#!/usr/bin/env python3
# Export a local CAT project as single-language, stacked, or side-by-side output.
#
# Fonts follow the usual bilingual-deliverable convention: Latin text uses the Latin
# font, CJK text uses the CJK font. In DOCX this is expressed with w:rFonts
# (w:ascii/w:hAnsi for Latin, w:eastAsia for CJK). In HTML the Latin font is listed
# first and the CJK font second, so each script picks the first family that has the
# glyphs it needs.
import io
import os
import re
from xml.sax.saxutils import escape as xml_escape
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile, ZipInfo

MODES = ("target", "stacked", "table")
MODE_LABELS = {"target": "译文", "stacked": "上下对照", "table": "左右对照"}

# Characters that are not valid in XML 1.0, including the vertical tab found in
# some source documents. They must never reach an exported file.
INVALID_XML = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]")
INVALID_FILENAME = re.compile(r'[\\/:*?"<>|\x00-\x1f]')
WML = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

A4_PORTRAIT = (11906, 16838)
A4_LANDSCAPE = (16838, 11906)
MARGIN = 1134


def fonts():
    return (os.environ.get("TIS_CAT_CJK_FONT", "SimSun"),
            os.environ.get("TIS_CAT_LATIN_FONT", "Arial"))


def clean(text):
    return INVALID_XML.sub("", str(text or ""))


def safe_name(text, fallback="tiskill-CAT"):
    name = INVALID_FILENAME.sub("", clean(text)).strip().strip(".")
    name = re.sub(r"\s+", " ", name)
    return (name or fallback)[:80]


def filename(doc, mode, extension):
    return f"{safe_name(doc.get('title'))}-{MODE_LABELS[mode]}.{extension}"


def segments(doc):
    return [(clean(seg.get("source", "")), clean(seg.get("target", ""))) for seg in doc.get("segments", [])]


def check_mode(mode):
    if mode not in MODES:
        raise ValueError("导出方式必须是 target、stacked 或 table。")


# ── Markdown ───────────────────────────────────────────────────────────────

def export_markdown(doc, mode="stacked"):
    # Markdown cannot carry font settings; use the HTML or DOCX export for that.
    check_mode(mode)
    title = clean(doc.get("title"))
    rows = segments(doc)
    if mode == "target":
        body = [f"# {title}（译文）", ""]
        for _source, target in rows:
            if target.strip():
                body.extend([target, ""])
        return "\n".join(body).rstrip() + "\n"
    if mode == "stacked":
        parts = [f"# {title}"]
        for index, (source, target) in enumerate(rows, 1):
            parts.append(f"## {index}\n\n原文：{source}\n\n译文：{target}")
        return "\n\n".join(parts) + "\n"
    lines = [f"# {title}（左右对照）", "", "| 原文 | 译文 |", "| --- | --- |"]
    cell = lambda t: t.replace("|", "&#124;").replace("\n", "<br>")
    lines += [f"| {cell(source)} | {cell(target)} |" for source, target in rows]
    return "\n".join(lines).rstrip() + "\n"


# ── HTML ───────────────────────────────────────────────────────────────────

HTML_TEMPLATE = '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  :root {{ --latin: {latin}; --cjk: {cjk}; }}
  body {{ font-family: {family}; white-space: pre-wrap; overflow-wrap: anywhere; font-size: 11pt; line-height: 1.65; color: #1c221e; margin: 32px auto; max-width: 46em; }}
  h1 {{ font-size: 15pt; margin: 0 0 4px; }}
  .meta {{ color: #6b736d; font-size: 9.5pt; margin: 0 0 22px; }}
  .pair {{ margin: 0 0 16px; break-inside: avoid; }}
  .src {{ color: #3a4640; margin: 0 0 4px; }}
  .tgt {{ margin: 0; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #b9bcb2; padding: 7px 9px; text-align: left; vertical-align: top; }}
  th {{ background: #eceae3; font-weight: 700; }}
  tbody tr:nth-child(even) {{ background: #faf9f5; }}
  @page {{ size: A4 {orientation}; margin: 18mm; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="meta">导出方式：{label} ｜ 中文 {cjk} ／ 西文 {latin} ｜ 由 tiskill CAT 本机导出</p>
{body}
</body>
</html>
'''


def export_html(doc, mode="stacked", cjk=None, latin=None):
    check_mode(mode)
    cjk = cjk or fonts()[0]
    latin = latin or fonts()[1]
    title = xml_escape(clean(doc.get("title")))
    # Latin family first: it has no CJK glyphs, so Chinese falls through to the CJK family.
    family = f'"{latin}", "{cjk}", "宋体", "Songti SC", serif'
    rows = segments(doc)
    if mode == "target":
        body = "\n".join(f"<p>{xml_escape(target)}</p>" for _s, target in rows if target.strip())
        orientation = "portrait"
    elif mode == "stacked":
        body = "\n".join(
            f'<section class="pair"><p class="src">{xml_escape(source)}</p><p class="tgt">{xml_escape(target)}</p></section>'
            for source, target in rows)
        orientation = "portrait"
    else:
        body = "\n".join(
            f'<tr><td class="src">{xml_escape(source)}</td><td class="tgt">{xml_escape(target)}</td></tr>'
            for source, target in rows)
        body = ('<table><thead><tr><th>原文</th><th>译文</th></tr></thead><tbody>\n'
                + body + "\n</tbody></table>")
        orientation = "landscape"
    return HTML_TEMPLATE.format(title=title, family=family, latin=latin, cjk=cjk,
                                label=MODE_LABELS[mode], body=body, orientation=orientation)


# ── DOCX ───────────────────────────────────────────────────────────────────

def _runs(text, bold=False, size=None):
    parts = []
    for index, line in enumerate(text.split("\n")):
        if index:
            parts.append("<w:br/>")
        parts.append(f'<w:t xml:space="preserve">{xml_escape(line)}</w:t>')
    options = ("<w:b/>" if bold else "") + (f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>' if size else "")
    return f"<w:r>{'<w:rPr>' + options + '</w:rPr>' if options else ''}{''.join(parts)}</w:r>"


def _paragraph(text, bold=False, size=None):
    keep = "<w:pPr><w:keepNext/></w:pPr>" if bold else ""
    return f"<w:p>{keep}{_runs(text, bold, size)}</w:p>"


def _cell(text, width, shade=None):
    properties = f'<w:tcW w:w="{width}" w:type="dxa"/>' + (f'<w:shd w:val="clear" w:fill="{shade}"/>' if shade else "")
    return f"<w:tc><w:tcPr>{properties}</w:tcPr>{_paragraph(text)}</w:tc>"


def _table(doc, content_width):
    column = content_width // 2
    borders = ("<w:tblBorders>" + "".join(
        f'<w:{edge} w:val="single" w:sz="4" w:space="0" w:color="B9BCB2"/>'
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV")) + "</w:tblBorders>")
    header = f'<w:tr><w:trPr><w:tblHeader/></w:trPr>{_cell("原文", column, "ECEAE3")}{_cell("译文", column, "ECEAE3")}</w:tr>'
    body = "".join(f"<w:tr>{_cell(source, column)}{_cell(target, column)}</w:tr>"
                   for source, target in segments(doc))
    grid = f'<w:tblGrid><w:gridCol w:w="{column}"/><w:gridCol w:w="{column}"/></w:tblGrid>'
    return f'<w:tbl><w:tblPr><w:tblW w:w="{content_width}" w:type="dxa"/>{borders}</w:tblPr>{grid}{header}{body}</w:tbl>'


def export_docx(doc, mode="stacked", cjk=None, latin=None):
    check_mode(mode)
    cjk = cjk or fonts()[0]
    latin = latin or fonts()[1]
    size = A4_LANDSCAPE if mode == "table" else A4_PORTRAIT
    content_width = size[0] - MARGIN * 2
    title = clean(doc.get("title"))
    blocks = [f'<w:p><w:pPr><w:jc w:val="center"/></w:pPr>{_runs(title, bold=True, size=32)}</w:p>']
    if mode == "target":
        blocks += [_paragraph(target) for _source, target in segments(doc) if target.strip()]
    elif mode == "stacked":
        for source, target in segments(doc):
            blocks.append(_paragraph(source).replace("<w:p>", "<w:p><w:pPr><w:keepNext/></w:pPr>", 1))
            blocks.append(_paragraph(target))
    else:
        blocks.append(_table(doc, content_width))
    sect = (f'<w:sectPr><w:pgSz w:w="{size[0]}" w:h="{size[1]}"/>'
            f'<w:pgMar w:top="{MARGIN}" w:right="{MARGIN}" w:bottom="{MARGIN}" w:left="{MARGIN}"/>'
            "</w:sectPr>")
    document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                f'<w:document xmlns:w="{WML}"><w:body>{"".join(blocks)}{sect}</w:body></w:document>')
    styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              f'<w:styles xmlns:w="{WML}"><w:docDefaults><w:rPrDefault><w:rPr>'
              f'<w:rFonts w:ascii="{xml_escape(latin)}" w:hAnsi="{xml_escape(latin)}" '
              f'w:eastAsia="{xml_escape(cjk)}" w:cs="{xml_escape(latin)}"/>'
              '<w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr>'
              '<w:spacing w:after="120" w:line="276" w:lineRule="auto"/>'
              '</w:pPr></w:pPrDefault></w:docDefaults>'
              '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>'
              "</w:styles>")
    content_types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="xml" ContentType="application/xml"/>'
                     '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                     '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
                     "</Types>")
    root_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                 "</Relationships>")
    document_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                     '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                     '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                     "</Relationships>")
    parts = [("[Content_Types].xml", content_types), ("_rels/.rels", root_rels),
             ("word/document.xml", document), ("word/styles.xml", styles),
             ("word/_rels/document.xml.rels", document_rels)]
    stream = io.BytesIO()
    stamp = (2026, 1, 1, 0, 0, 0)  # Fixed stamps keep repeated exports byte-identical.
    with ZipFile(stream, "w", ZIP_DEFLATED) as archive:
        for name, text in parts:
            info = ZipInfo(name, stamp)
            info.compress_type = ZIP_STORED if name == "[Content_Types].xml" else ZIP_DEFLATED
            archive.writestr(info, text)
    return stream.getvalue()
