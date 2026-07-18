# -*- coding: utf-8 -*-
"""Renders content.DOCUMENT into a .pdf family teaching guide, using reportlab."""
import os
import re
import sys

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle

sys.path.insert(0, os.path.dirname(__file__))
from content import DOCUMENT, ASSETS

HERE = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(os.path.dirname(HERE), ASSETS)
OUT_PATH = os.path.join(os.path.dirname(HERE), "Family_Guide_Retail_SQL_Agent.pdf")

FONT_DIR = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("Georgia", os.path.join(FONT_DIR, "georgia.ttf")))
pdfmetrics.registerFont(TTFont("Georgia-Bold", os.path.join(FONT_DIR, "georgiab.ttf")))
pdfmetrics.registerFont(TTFont("Georgia-Italic", os.path.join(FONT_DIR, "georgiai.ttf")))
pdfmetrics.registerFont(TTFont("Calibri", os.path.join(FONT_DIR, "calibri.ttf")))
pdfmetrics.registerFont(TTFont("Calibri-Bold", os.path.join(FONT_DIR, "calibrib.ttf")))
pdfmetrics.registerFont(TTFont("Calibri-Italic", os.path.join(FONT_DIR, "calibrii.ttf")))
pdfmetrics.registerFont(TTFont("Consolas", os.path.join(FONT_DIR, "consola.ttf")))

INK = HexColor("#232B3A")
INDIGO = HexColor("#2D3F6B")
AMBER = HexColor("#B56E12")
GREEN = HexColor("#2E5C44")
MUTED = HexColor("#5B5748")
PAGE_BG = HexColor("#FBF8F2")

CALLOUT_FILL = {"kid": HexColor("#FCEFD8"), "business": HexColor("#E7F2EC"), "note": HexColor("#E7EBF5")}
CALLOUT_BAR = {"kid": HexColor("#E0952E"), "business": HexColor("#3F7D5C"), "note": HexColor("#2D3F6B")}
CALLOUT_LABEL = {"kid": AMBER, "business": GREEN, "note": INDIGO}


def markup_to_reportlab(text):
    """Convert **bold** / *italic* markdown into reportlab inline tags, and escape XML."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return text


styles = {
    "h1": ParagraphStyle("h1", fontName="Georgia-Bold", fontSize=20, leading=24,
                          textColor=INDIGO, spaceBefore=16, spaceAfter=10,
                          borderColor=AMBER),
    "h2": ParagraphStyle("h2", fontName="Georgia-Bold", fontSize=14, leading=18,
                          textColor=GREEN, spaceBefore=10, spaceAfter=6),
    "body": ParagraphStyle("body", fontName="Calibri", fontSize=10.7, leading=15.5,
                            textColor=INK, spaceAfter=8, alignment=TA_LEFT),
    "callout_label": ParagraphStyle("callout_label", fontName="Calibri-Bold", fontSize=9,
                                     leading=11, spaceAfter=3),
    "callout_body": ParagraphStyle("callout_body", fontName="Calibri", fontSize=10.3,
                                    leading=14.5, textColor=INK),
    "caption": ParagraphStyle("caption", fontName="Calibri-Italic", fontSize=8.5,
                               leading=11, textColor=MUTED, alignment=TA_CENTER,
                               spaceAfter=10),
    "code": ParagraphStyle("code", fontName="Consolas", fontSize=8.7, leading=12,
                            textColor=HexColor("#9BE89B")),
    "bullet": ParagraphStyle("bullet", fontName="Calibri", fontSize=10.5, leading=14.5,
                              textColor=INK),
    "cover_title": ParagraphStyle("cover_title", fontName="Georgia-Bold", fontSize=27,
                                   leading=33, textColor=INDIGO, alignment=TA_CENTER,
                                   spaceAfter=10),
    "cover_sub": ParagraphStyle("cover_sub", fontName="Calibri-Italic", fontSize=14,
                                 leading=19, textColor=AMBER, alignment=TA_CENTER,
                                 spaceAfter=22),
    "cover_meta": ParagraphStyle("cover_meta", fontName="Calibri", fontSize=10.5,
                                  leading=15, textColor=MUTED, alignment=TA_CENTER,
                                  spaceAfter=6),
    "term": ParagraphStyle("term", fontName="Calibri-Bold", fontSize=9.7, leading=13,
                            textColor=INDIGO),
    "definition": ParagraphStyle("definition", fontName="Calibri", fontSize=9.7,
                                  leading=13.5, textColor=INK),
    "quiz_q": ParagraphStyle("quiz_q", fontName="Calibri-Bold", fontSize=10.7,
                              leading=15, textColor=INK, spaceBefore=8, spaceAfter=3),
    "quiz_opt": ParagraphStyle("quiz_opt", fontName="Calibri", fontSize=9.7, leading=13,
                                textColor=INK, leftIndent=16),
    "quiz_ans": ParagraphStyle("quiz_ans", fontName="Calibri-Italic", fontSize=9.3,
                                leading=13, textColor=MUTED, leftIndent=16,
                                spaceAfter=10),
}


def para(text, style="body"):
    return Paragraph(markup_to_reportlab(text), styles[style])


def build_callout(style, label, text):
    bar = Table([[""]], colWidths=[0.09 * inch], rowHeights=[None])
    inner = [[para(label.upper(), "callout_label")], [para(text, "callout_body")]]
    inner_table = Table(inner, colWidths=[6.0 * inch])
    inner_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CALLOUT_FILL[style]),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
        ("TOPPADDING", (0, 1), (-1, 1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
        ("TEXTCOLOR", (0, 0), (0, 0), CALLOUT_LABEL[style]),
    ]))
    outer = Table([[inner_table]], colWidths=[6.0 * inch])
    outer.setStyle(TableStyle([
        ("LINEBEFORE", (0, 0), (0, 0), 4, CALLOUT_BAR[style]),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return outer


def build_image(path, caption, width_in):
    full = os.path.join(ASSETS_DIR, path)
    from PIL import Image as PILImage
    with PILImage.open(full) as im:
        w, h = im.size
    ratio = h / w
    img = Image(full, width=width_in * inch, height=width_in * inch * ratio)
    flow = [img]
    if caption:
        flow.append(Spacer(1, 4))
        flow.append(para(caption, "caption"))
    return [KeepTogether(flow)]


def build_code(text):
    t = Table([[Paragraph(text.replace("&", "&amp;").replace("<", "&lt;"), styles["code"])]],
               colWidths=[6.0 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), INK),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def build_bullets(items, numbered=False):
    kind = "1" if numbered else "bullet"
    lis = [ListItem(para(it, "bullet"), leftIndent=14) for it in items]
    return ListFlowable(lis, bulletType=kind, start=1 if numbered else None,
                         bulletFontName="Calibri", bulletFontSize=9.5,
                         leftIndent=20, spaceBefore=2, spaceAfter=8)


def build_glossary(items):
    rows = []
    for term, definition in items:
        rows.append([para(term, "term"), para(definition, "definition")])
    t = Table(rows, colWidths=[1.5 * inch, 4.5 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#F3EFE3")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, HexColor("#E4DFD3")),
    ]))
    return t


def build_quiz(items):
    flow = []
    for i, item in enumerate(items, 1):
        flow.append(para(f"{i}. {item['q']}", "quiz_q"))
        if item["options"]:
            for opt in item["options"]:
                flow.append(para("• " + opt, "quiz_opt"))
        flow.append(para("**Answer:** " + item["answer"], "quiz_ans"))
    return flow


def build_cover(block, story):
    story.append(Spacer(1, 2.0 * inch))
    story.append(para(block["title"], "cover_title"))
    story.append(para(block["subtitle"], "cover_sub"))
    for line in block["meta"]:
        story.append(para(line, "cover_meta"))
    story.append(PageBreak())


def h1_flow(text):
    p = para(text, "h1")
    rule = HRFlowable(width="100%", thickness=1.4, color=AMBER, spaceBefore=2, spaceAfter=10)
    return [p, rule]


def main():
    doc = SimpleDocTemplate(
        OUT_PATH, pagesize=LETTER,
        leftMargin=0.85 * inch, rightMargin=0.85 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        title="How Our Robot Answers Business Questions",
    )

    story = []
    for block in DOCUMENT:
        t = block["type"]
        if t == "cover":
            build_cover(block, story)
        elif t == "heading":
            if block["level"] == 1:
                story.extend(h1_flow(block["text"]))
            else:
                story.append(para(block["text"], "h2"))
        elif t == "para":
            story.append(para(block["text"], "body"))
        elif t == "callout":
            story.append(build_callout(block["style"], block["label"], block["text"]))
            story.append(Spacer(1, 10))
        elif t == "image":
            story.extend(build_image(block["path"], block.get("caption", ""),
                                      block.get("width_in", 6.0)))
            story.append(Spacer(1, 4))
        elif t == "code":
            story.append(build_code(block["text"]))
            story.append(Spacer(1, 8))
        elif t == "bullets":
            story.append(build_bullets(block["items"]))
        elif t == "numbered":
            story.append(build_bullets(block["items"], numbered=True))
        elif t == "glossary":
            story.append(build_glossary(block["items"]))
            story.append(Spacer(1, 8))
        elif t == "quiz":
            story.extend(build_quiz(block["items"]))
        elif t == "divider":
            story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED,
                                     spaceBefore=6, spaceAfter=6))
        elif t == "pagebreak":
            story.append(PageBreak())
        else:
            raise ValueError(f"Unknown block type: {t}")

    doc.build(story)
    print("Saved:", OUT_PATH)


if __name__ == "__main__":
    main()
