"""
14_build_latex_pdf.py
=====================
Generate a Springer-style TWO-COLUMN LaTeX manuscript + PDF from
reports/MANUSCRIPT_IJDSA.md, using pandoc (-> .tex) and pdflatex (-> .pdf).

Outputs:
  MMI_submission_package/Main_Manuscript_IJDSA_twocolumn.tex
  MMI_submission_package/Main_Manuscript_IJDSA_twocolumn.pdf
"""
import os
import re
import subprocess

MD = "reports/MANUSCRIPT_IJDSA.md"
OUTDIR = "MMI_submission_package"
STEM = "Main_Manuscript_IJDSA_twocolumn"
FIG = os.path.abspath("outputs/figures")

FIG_BLOCK = {  # caption text -> (file, width factor); pandoc auto-numbers
    "Receiver Operating Characteristic curve for outbreak-month detection, built from strictly temporal out-of-fold predictions (AUC = 0.936).":
        ("roc_curve.png", 0.9),
    "Grouped driver hierarchy from the Gradient Boosting Regressor: seasonality (74.0%) and autoregressive momentum (20.8%) dominate, with vulnerability (4.0%) and climate (1.2%) modest.":
        ("feature_importance.png", 1.9),
    "Between-state vulnerability: composite risk score versus NITI Aayog Health Index, illustrating cross-state stratification of chronic burden.":
        ("risk_vs_vulnerability.png", 0.95),
    "State-level composite dengue outbreak risk for the 15 modelled states (others grey, out-of-sample).":
        ("india_risk_map.png", 0.85),
    "Box 1. The Dengue Outbreak Rapid Assessment Scale - a paper-based field tool for district health officers, validated against the full model (Spearman rho = 0.76).":
        ("practitioner_scorecard.png", 1.9),
}


UNI = {
    "²": "\\textsuperscript{2}", "ρ": "$\\rho$", "±": "$\\pm$",
    "×": "$\\times$", "≈": "$\\approx$", "≥": "$\\ge$", "≤": "$\\le$",
    "→": "$\\to$", "°C": "\\,$^{\\circ}$C", "°": "\\,$^{\\circ}$",
    "—": "---", "–": "--", "•": "-", "’": "'", "‘": "'",
    "“": "``", "”": "''",
}


def latexsafe(s):
    for k, v in UNI.items():
        s = s.replace(k, v)
    return s


def build_pandoc_md():
    with open(MD, encoding="utf-8") as f:
        text = f.read()  # xelatex handles Unicode natively

    title = re.search(r"^# (.+)$", text, re.M).group(1)

    # abstract = block between '## Abstract' and the first '---'
    abs = re.search(r"## Abstract\s*(.+?)\n---", text, re.S).group(1).strip()
    # collapse to a single indented block-scalar body (no escaping needed)
    abs_lines = [ln.strip() for ln in abs.splitlines() if ln.strip()]
    abs_block = "\n".join("  " + ln for ln in abs_lines)

    # body = from '## 1. Introduction' onward
    body = text[text.index("## 1. Introduction"):]

    # inject figures where the legends section begins
    fig_md = ["## 7. Figures and Legends\n"]
    for cap, (fn, w) in FIG_BLOCK.items():
        path = os.path.join(FIG, fn).replace("\\", "/")
        star = "{width=\\linewidth}" if w > 1.5 else "{width=0.95\\columnwidth}"
        fig_md.append(f"![{cap}]({path}){star}\n")
    body = re.sub(r"## 7\. Figure Legends.*?(?=\n## 8\.)",
                  lambda _m: "\n".join(fig_md) + "\n", body, flags=re.S)

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
    pandoc_md = os.path.join(OUTDIR, "_pandoc_src.md")
    with open(pandoc_md, "w", encoding="utf-8") as f:
        f.write(yaml + body)
    return pandoc_md


def fix_longtables(tex):
    """Convert pandoc longtables (illegal in twocolumn) to full-width table* floats."""
    pat = re.compile(
        r"\{\\def\\LTcaptype\{none\}[^\n]*\n\\begin\{longtable\}\[\]\{(.*?)\}(.*?)"
        r"\\end\{longtable\}\n\}", re.S)

    def repl(m):
        colspec = m.group(1).replace("\\linewidth", "\\textwidth")
        body = m.group(2)
        for tok in ("\\noalign{}", "\\endhead", "\\endfirsthead", "\\endlastfoot"):
            body = body.replace(tok, "")
        body = body.replace("\\bottomrule", "")  # drop the longtable foot rule
        body = "\n".join(ln for ln in body.splitlines() if ln.strip())
        return ("\\begin{table*}[t]\\centering\\footnotesize\n"
                "\\begin{tabular}{" + colspec + "}\n" + body +
                "\n\\bottomrule\n\\end{tabular}\\end{table*}")

    return pat.sub(repl, tex)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    src = build_pandoc_md()
    tex = os.path.join(OUTDIR, STEM + ".tex")
    pdf = os.path.join(OUTDIR, STEM + ".pdf")

    common = [
        "pandoc", src, "--standalone",
        "-V", "documentclass=article",
        "-V", "classoption=twocolumn",
        "-V", "geometry:margin=1.6cm",
        "-V", "fontsize=10pt",
        "-V", "mainfont=Times New Roman",
        "-V", "linkcolor=blue",
        "--metadata", "link-citations=true",
    ]
    subprocess.run(common + ["-o", tex], check=True)
    with open(tex, encoding="utf-8") as f:
        fixed = fix_longtables(f.read())
    with open(tex, "w", encoding="utf-8") as f:
        f.write(fixed)
    print(f"Saved {tex}")

    ok = False
    for _ in range(2):  # twice for cross-references
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
                            f"-output-directory={OUTDIR}", tex],
                           capture_output=True, text=True)
        ok = (r.returncode == 0)
    if ok and os.path.exists(pdf):
        print(f"Saved {pdf}")
        for ext in (".aux", ".log", ".out"):
            p = os.path.join(OUTDIR, STEM + ext)
            if os.path.exists(p):
                os.remove(p)
    else:
        print("PDF build issue (tex produced):")
        print(r.stdout[-1800:])


if __name__ == "__main__":
    main()
