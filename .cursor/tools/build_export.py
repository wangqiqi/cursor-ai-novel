#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_export.py · 外发打包（EPUB3 / 分章 TXT / 合并 Markdown）

用途：把 `章节/` 下的正文打包成可交付文件。只依赖 Python 3 标准库（EPUB 用 zipfile 手写）。
**源只能是 `章节/`**（控制层 `主题/` 不进外发包）。只写 `build/`，不动正文。

用法：
    python3 .cursor/tools/build_export.py                          # 三种格式全出
    python3 .cursor/tools/build_export.py --format epub
    python3 .cursor/tools/build_export.py --title "书名" --author "署名"
    python3 .cursor/tools/build_export.py --strip-structural       # 去掉「本节完/本章完」标记
    python3 .cursor/tools/build_export.py --strip-viewpoint        # 再去掉 `> 【视角：…】` 行
    python3 .cursor/tools/build_export.py --root <项目根>

产出（默认）：
    build/<书名>_全文.md
    build/<书名>_分章/<NN>_<章名>.txt
    build/<书名>.epub
    build/<书名>_统计报告.md
退出码：0 成功；1 无正文；2 参数错误。
"""

import argparse
import html
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, datetime, timezone


def strip_illegal_xml(s):
    """去掉 XML 1.0 不允许的控制字符（保留 \\t \\n \\r）。"""
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", s)

CHAP_RE = re.compile(r"第\s*0*(\d+)\s*章")
SEC_RE = re.compile(r"第\s*0*(\d+)\s*节")


def cjk_count(t):
    return len(re.findall(r"[\u4e00-\u9fff]", t))


def natural_key(s):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", s)]


def read(p):
    return open(p, encoding="utf-8").read()


def chapter_title(entry):
    """`第01章_初雪` → `第01章 初雪`；不合规范的目录名原样返回。"""
    m = CHAP_RE.match(entry)
    if m:
        num = int(m.group(1))
        rest = entry[m.end():].lstrip("_·- 　")
        return f"第{num:02d}章 {rest}".strip() if rest else f"第{num:02d}章"
    return entry.replace("_", " ").strip()


def section_title(text):
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+)$", line.strip())
        if m:
            return m.group(1).strip()
    return None


def strip_leading_h1(text):
    """去掉节文件开头的第一个 H1（章标题由章目录提供，避免重复）。"""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue
        if s.startswith("# "):
            return "\n".join(lines[:i] + lines[i + 1:])
        return text
    return text


def clean_prose(text, strip_structural, strip_viewpoint):
    """把工作稿转为阅读稿：去节级 H1、去完成标记、按需去视角标记、规范空行。"""
    text = strip_leading_h1(text)
    out = []
    for line in text.splitlines():
        s = line.strip()
        if strip_structural and re.match(r"^##\s*(本节完|本章完)\s*$", s):
            continue
        if strip_viewpoint and re.match(r"^>\s*【视角", s):
            continue
        out.append(line.rstrip())
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def collect(root):
    base = os.path.join(root, "章节")
    if not os.path.isdir(base):
        return []
    chapters = []
    for entry in sorted(os.listdir(base), key=natural_key):
        d = os.path.join(base, entry)
        if os.path.isdir(d):
            secs = []
            for fn in sorted(os.listdir(d), key=natural_key):
                if fn.endswith(".md"):
                    secs.append(os.path.join(d, fn))
            if secs:
                chapters.append((entry, secs))
        elif entry.endswith(".md"):        # 扁平布局（旧项目）
            chapters.append((entry[:-3], [d]))
    return chapters


def discover_meta(root):
    """从 主题/总览.md 猜书名；找不到就用目录名。"""
    title = None
    for rel in ("主题/总览.md", "主题/_meta/总览.md"):
        p = os.path.join(root, rel)
        if os.path.isfile(p):
            m = re.search(r"^#\s*总览\s*[·:：-]\s*(.+)$", read(p), re.M)
            if m and m.group(1).strip():
                title = m.group(1).strip()
            break
    if not title:
        for rel in ("主题/总览.md",):
            p = os.path.join(root, rel)
            if os.path.isfile(p):
                m = re.search(r"\|\s*\*\*项目名\*\*\s*\|\s*([^|<]+)", read(p))
                if m and m.group(1).strip() and not m.group(1).strip().startswith("<"):
                    title = m.group(1).strip()
    return title or os.path.basename(os.path.abspath(root))


def build_markdown(title, chapters, out_path, cleaner, keep_section_titles):
    parts = [f"# {title}\n"]
    stats = []
    for cname, secs in chapters:
        ctitle = chapter_title(cname)
        blocks = []
        for s in secs:
            raw = read(s)
            st = section_title(raw)
            body = cleaner(raw)
            if keep_section_titles and st:
                body = f"### {st}\n\n{body}"
            blocks.append(body)
        text = "\n\n".join(blocks)
        parts.append(f"\n## {ctitle}\n\n{text}")
        stats.append((ctitle, cjk_count(text)))
    parts.append("")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    return stats


def build_txt(title, chapters, out_dir, cleaner):
    os.makedirs(out_dir, exist_ok=True)
    stats = []
    for i, (cname, secs) in enumerate(chapters, 1):
        ctitle = chapter_title(cname)
        text = "\n\n".join(cleaner(read(s)) for s in secs)
        safe = re.sub(r"[\\/:*?\"<>|]", "_", ctitle)
        p = os.path.join(out_dir, f"{i:03d}_{safe}.txt")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(f"{ctitle}\n\n{text}")
        stats.append((ctitle, cjk_count(text), p))
    return stats


CSS = """body { font-family: serif; line-height: 1.8; margin: 5%; }
h1 { font-size: 1.5em; margin: 1.2em 0 1em; }
p { text-indent: 2em; margin: 0 0 0.6em; }
"""

XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh" lang="zh">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
<h1>{title}</h1>
{body}
</body>
</html>
"""

CONTAINER = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""


def text_to_paragraphs(text):
    """去掉 H1（已作章标题），其余非空行转 <p>。"""
    lines = text.splitlines()
    out = []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.append(f"<p>{html.escape(s)}</p>")
    return "\n".join(out)


def build_epub(title, author, lang, chapters, out_path, cleaner):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    names = []
    chapters_html = []
    for i, (cname, secs) in enumerate(chapters, 1):
        ctitle = chapter_title(cname)
        text = "\n\n".join(cleaner(read(s)) for s in secs)
        fn = f"chap{i:03d}.xhtml"
        names.append((fn, ctitle))
        chapters_html.append((fn, XHTML.format(title=html.escape(ctitle),
                                               body=text_to_paragraphs(text))))

    nav_items = "\n".join(
        f'      <li><a href="{fn}">{html.escape(h)}</a></li>' for fn, h in names
    )
    nav = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh" lang="zh">
<head><meta charset="utf-8"/><title>目录</title></head>
<body>
  <nav epub:type="toc" id="toc">
    <h1>目录</h1>
    <ol>
{nav_items}
    </ol>
  </nav>
</body>
</html>
"""

    uid = f"urn:uuid:{re.sub(r'[^a-zA-Z0-9]', '-', title)}-{date.today().isoformat()}"
    mod = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = "\n".join(f'    <item id="c{i:03d}" href="{fn}" media-type="application/xhtml+xml"/>'
                         for i, (fn, _h) in enumerate(names, 1))
    spine = "\n".join(f'    <itemref idref="c{i:03d}"/>' for i in range(1, len(names) + 1))
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{lang}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{html.escape(uid)}</dc:identifier>
    <meta property="dcterms:modified">{mod}</meta>
    <dc:title>{html.escape(title)}</dc:title>
    <dc:language>{lang}</dc:language>
    <dc:creator>{html.escape(author)}</dc:creator>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="css" href="style.css" media-type="text/css"/>
{manifest}
  </manifest>
  <spine>
{spine}
  </spine>
</package>
"""

    # XML 1.0 不允许 C0 控制字符（\x00-\x08\x0b\x0c\x0e-\x1f）：写入前剥除
    opf = strip_illegal_xml(opf)
    nav = strip_illegal_xml(nav)
    chapters_html = [(fn, strip_illegal_xml(body)) for fn, body in chapters_html]

    with zipfile.ZipFile(out_path, "w") as z:
        # mimetype 必须是第一个条目且不压缩
        zi = zipfile.ZipInfo("mimetype")
        zi.compress_type = zipfile.ZIP_STORED
        z.writestr(zi, "application/epub+zip")
        z.writestr(zipfile.ZipInfo("META-INF/container.xml"), CONTAINER, zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("OEBPS/content.opf"), opf, zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("OEBPS/nav.xhtml"), nav, zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("OEBPS/style.css"), CSS, zipfile.ZIP_DEFLATED)
        for fn, body in chapters_html:
            z.writestr(zipfile.ZipInfo(f"OEBPS/{fn}"), body, zipfile.ZIP_DEFLATED)

    # 自检：结构可读 **且每个 XML 部件真的良构**（testzip 看不出格式错误）
    with zipfile.ZipFile(out_path) as z:
        bad = z.testzip()
        names_in = set(z.namelist())
        problems = []
        for nm in sorted(n for n in names_in if n.endswith((".xhtml", ".opf", ".xml"))):
            try:
                ET.fromstring(z.read(nm))
            except ET.ParseError as exc:
                problems.append(f"{nm}: {exc}")
    need = {"mimetype", "META-INF/container.xml", "OEBPS/content.opf", "OEBPS/nav.xhtml"}
    missing = need - names_in
    return (bad is None and not missing and not problems), sorted(missing) + problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--format", default="md,txt,epub")
    ap.add_argument("--title", default=None)
    ap.add_argument("--author", default="佚名")
    ap.add_argument("--lang", default="zh")
    ap.add_argument("--out", default="build")
    ap.add_argument("--strip-structural", action="store_true",
                    help="去掉 `## 本节完` / `## 本章完`")
    ap.add_argument("--strip-viewpoint", action="store_true",
                    help="再去掉 `> 【视角：…】` 行")
    ap.add_argument("--keep-section-titles", action="store_true",
                    help="在合并 Markdown 中保留节标题（降为 ###）；默认不保留")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    root = args.root or os.path.dirname(os.path.dirname(here))
    chapters = collect(root)
    if not chapters:
        print(f"✗ 未找到正文：{os.path.join(root, '章节')}", file=sys.stderr)
        return 1

    title = args.title or discover_meta(root)
    safe_title = re.sub(r'[\\/:*?"<>|]', "_", title).strip() or "未命名"
    if safe_title != title:
        print(f"  ⚠ 书名含路径非法字符，文件名改用：{safe_title}", file=sys.stderr)
    author = args.author
    out_dir = os.path.join(root, args.out)
    fmts = [f.strip() for f in args.format.split(",") if f.strip()]
    known = {"md", "txt", "epub"}
    unknown = [f for f in fmts if f not in known]
    if unknown or not fmts:
        print(f"✗ 未知/空的 --format：{unknown or fmts}（可选 md, txt, epub，逗号分隔）", file=sys.stderr)
        return 2

    def cleaner(t):
        return clean_prose(t, args.strip_structural, args.strip_viewpoint)

    print(f"外发打包 · 《{title}》· {len(chapters)} 章 · 署名 {author}")
    print(f"源：{os.path.relpath(os.path.join(root, '章节'), root)}"
          f"（仅正文层；`主题/` 不进包）")

    made = []
    stats = []
    if "md" in fmts:
        p = os.path.join(out_dir, f"{safe_title}_全文.md")
        s = build_markdown(title, chapters, p, cleaner, args.keep_section_titles)
        stats = s
        made.append(p)
    if "txt" in fmts:
        p = os.path.join(out_dir, f"{safe_title}_分章")
        s = build_txt(title, chapters, p, cleaner)
        stats = stats or [(h, n) for h, n, _ in s]
        made.append(p)
    if "epub" in fmts:
        p = os.path.join(out_dir, f"{safe_title}.epub")
        ok, missing = build_epub(title, author, args.lang, chapters, p, cleaner)
        if not ok:
            print(f"  ✗ EPUB 结构自检未过，缺：{missing}", file=sys.stderr)
            return 1
        made.append(p)

    total = sum(n for _h, n in stats)
    rep = os.path.join(out_dir, f"{safe_title}_统计报告.md")
    os.makedirs(out_dir, exist_ok=True)
    with open(rep, "w", encoding="utf-8") as fh:
        fh.write(f"# 外发统计 · {title}\n\n")
        fh.write(f"- 生成时间：{date.today().isoformat()}\n- 署名：{author}\n")
        fh.write(f"- 章数：{len(stats)}\n- 总汉字：{total}\n")
        fh.write(f"- 平均章汉字：{total // max(1, len(stats))}\n\n")
        fh.write("| 序 | 章 | 汉字 |\n|---|----|------|\n")
        for i, (h, n) in enumerate(stats, 1):
            fh.write(f"| {i} | {h} | {n} |\n")
    made.append(rep)

    for p in made:
        print(f"  ✓ {os.path.relpath(p, root)}")
    print(f"\n✓ 合计 {total} 汉字 · {len(stats)} 章")
    print("提示：`build/` 被 .gitignore 忽略（外发产物，可重跑）；")
    print("      版本化推介材料请写 `主题/推介包.md`。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
