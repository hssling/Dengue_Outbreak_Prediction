"""
29_build_latex_pdf.py
=====================
Produce the LaTeX source and a PDF of the R1 manuscript.

  Main_Manuscript_IJDSA_R1.tex   two-column LaTeX, generated with pandoc
  Main_Manuscript_IJDSA_R1.pdf   rendered from the clean .docx

The PDF is produced from the Word file rather than from LaTeX on purpose: the
.docx is the file being submitted, so rendering it through Word guarantees the
PDF a reader sees is byte-for-byte the same layout the editor opens. If a LaTeX
engine is installed, the .tex is additionally compiled as a cross-check.

Figure numbering follows order of first mention in the text, so the mapping from
manuscript figure number to source file is imported from the docx builder rather
than duplicated here.
"""

import importlib.util
import os
import re
import shutil
import subprocess
import sys

MD = "reports/MANUSCRIPT_IJDSA_R1.md"
OUTDIR = "MMI_submission_package/IJDSA_R1"
STEM = "Main_Manuscript_IJDSA_R1"
DOCX = f"{OUTDIR}/{STEM}_clean.docx"
FIGDIR = os.path.abspath("outputs/figures_real")

_spec = importlib.util.spec_from_file_location("b23", "src/23_build_revision_docx.py")
_b23 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_b23)
FIGURES = _b23.FIGURES


# --------------------------------------------------------------------------- #
def build_pandoc_source():
    """Rewrite the manuscript into a pandoc-friendly file with real figures."""
    text = open(MD, encoding="utf-8").read()
    title = re.search(r"^# (.+)$", text, re.M).group(1)

    abstract = re.search(r"## Abstract\s*(.+?)\n---", text, re.S).group(1).strip()
    abs_block = "\n".join("  " + ln.strip()
                          for ln in abstract.splitlines() if ln.strip())

    body = text[text.index("## 1. Introduction"):]

    # Replace the legends section with actual figures carrying their captions.
    # Figures are copied beside the .tex and renamed to match their manuscript
    # number, so the LaTeX bundle is self-contained and portable: absolute local
    # paths would not compile on the journal's system, and the source filenames
    # do not correspond to the figure numbers.
    figdir = os.path.join(OUTDIR, "figures")
    os.makedirs(figdir, exist_ok=True)
    legends = re.search(r"## 7\. Figure Legends(.*?)(?=\n## 8\.)", body, re.S)
    if legends:
        blocks = ["## 7. Figures and Legends\n"]
        for m in re.finditer(r"\*\*Figure (\d)\.\*\*\s*(.+?)(?=\n\n|\Z)",
                             legends.group(1), re.S):
            n, cap = int(m.group(1)), " ".join(m.group(2).split())
            fname, _ = FIGURES[n]
            src_png = os.path.join(FIGDIR, fname)
            dest = os.path.join(figdir, f"Figure{n}.png")
            if os.path.exists(src_png):
                shutil.copyfile(src_png, dest)
            cap = cap.replace("**", "").replace("*", "")
            blocks.append(f"![Figure {n}. {cap}](figures/Figure{n}.png)"
                          "{width=\\linewidth}\n")
        body = body[:legends.start()] + "\n".join(blocks) + "\n" + body[legends.end():]

    yaml = ("---\n"
            "title: |\n"
            f"  {title}\n"
            "author:\n"
            "  - Siddalingaiah H S$^{1,*}$\n"
            "  - Sowjanya D$^{1}$\n"
            "  - Rangaswamy H V$^{1}$\n"
            "abstract: |\n"
            f"{abs_block}\n"
            "---\n\n")

    src = os.path.join(OUTDIR, "_pandoc_src_R1.md")
    with open(src, "w", encoding="utf-8") as f:
        f.write(yaml + body)
    return src


def fix_longtables(tex):
    """pandoc emits longtable, which is illegal in a twocolumn document."""
    pat = re.compile(
        r"\{\\def\\LTcaptype\{none\}[^\n]*\n\\begin\{longtable\}\[\]\{(.*?)\}(.*?)"
        r"\\end\{longtable\}\n\}", re.S)

    def repl(m):
        colspec = m.group(1).replace("\\linewidth", "\\textwidth")
        body = m.group(2)
        for tok in ("\\noalign{}", "\\endhead", "\\endfirsthead", "\\endlastfoot"):
            body = body.replace(tok, "")
        body = body.replace("\\bottomrule", "")
        body = "\n".join(ln for ln in body.splitlines() if ln.strip())
        return ("\\begin{table*}[t]\\centering\\footnotesize\n"
                "\\begin{tabular}{" + colspec + "}\n" + body +
                "\n\\bottomrule\n\\end{tabular}\\end{table*}")

    return pat.sub(repl, tex)


def build_tex(src):
    tex = os.path.join(OUTDIR, STEM + ".tex")
    cmd = [
        "pandoc", src, "--standalone",
        "-V", "documentclass=article",
        "-V", "classoption=twocolumn",
        "-V", "geometry:margin=1.6cm",
        "-V", "fontsize=10pt",
        "-V", "mainfont=Times New Roman",
        "--metadata", "link-citations=true",
        "-o", tex,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    fixed = fix_longtables(open(tex, encoding="utf-8").read())
    with open(tex, "w", encoding="utf-8") as f:
        f.write(fixed)
    return tex


def build_pdf_from_docx():
    """Render the submitted .docx through Word for an exact-layout PDF."""
    if not os.path.exists(DOCX):
        return None, f"missing {DOCX}"
    pdf = os.path.join(OUTDIR, STEM + ".pdf")
    try:
        from docx2pdf import convert
        convert(os.path.abspath(DOCX), os.path.abspath(pdf))
    except Exception as e:                       # Word unavailable or COM error
        return None, str(e)
    return (pdf, None) if os.path.exists(pdf) else (None, "converter produced no file")


def compile_tex(tex):
    """Optional cross-check: compile the .tex if any LaTeX engine is present."""
    engine = next((e for e in ("xelatex", "pdflatex", "lualatex")
                   if shutil.which(e)), None)
    if not engine:
        return None
    out = os.path.join(OUTDIR, STEM + "_latex.pdf")
    for _ in range(2):
        subprocess.run([engine, "-interaction=nonstopmode",
                        f"-output-directory={OUTDIR}", tex],
                       capture_output=True, text=True)
    produced = os.path.join(OUTDIR, STEM + ".pdf")
    if os.path.exists(produced) and produced != out:
        shutil.move(produced, out)
    return out if os.path.exists(out) else None


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    src = build_pandoc_source()
    tex = build_tex(src)
    print(f"Saved {tex}  ({os.path.getsize(tex)/1024:.0f} KB)")

    pdf, err = build_pdf_from_docx()
    if pdf:
        print(f"Saved {pdf}  ({os.path.getsize(pdf)/1024:.0f} KB)  [rendered from .docx via Word]")
    else:
        print(f"[warn] PDF not produced from .docx: {err}")

    latex_pdf = compile_tex(tex)
    if latex_pdf:
        print(f"Saved {latex_pdf}  [LaTeX cross-check]")
    else:
        print("[info] no LaTeX engine installed; .tex not compiled "
              "(the submitted PDF comes from the .docx)")

    if os.path.exists(src):
        os.remove(src)
    return 0 if pdf else 1


if __name__ == "__main__":
    sys.exit(main())
