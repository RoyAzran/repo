"""Build the Hebrew catalog sample from catalog_spec.py.

Outputs:
  catalog_HE.pdf          Hebrew pages (Chromium render of the same layout)
  Catalog_HE.idml         InDesign file: text-free original art + live Hebrew text frames
  catalog_review.pdf      one file to review: original vs Hebrew side by side + text table
"""
import base64, html, json, os, subprocess, zipfile
from statistics import median
from xml.sax.saxutils import escape
from PIL import Image
from catalog_spec import PAGES

for _pg in PAGES.values():  # keep ™ attached to the Latin word it follows in RTL text
    for _b in _pg["blocks"]:
        if isinstance(_b["he"], str):
            _b["he"] = _b["he"].replace("™", "™\u200e").replace("®", "®\u200e")

H = 595.276
CHROME = next(os.path.join(r, "chrome-linux/chrome") for r in
              sorted(os.path.join("/opt/pw-browsers", d) for d in os.listdir("/opt/pw-browsers") if d.startswith("chromium-")))


# ---------------- colour sampling ----------------
def sample_color(page, box):
    o = Image.open(f"orig150_p{page}.png").convert("RGB")
    n = Image.open(f"nt150_p{page}.png").convert("RGB")
    k = 150 / 72
    x1, y1, x2, y2 = [int(v * k) for v in box]
    px = []
    for y in range(max(0, y1), min(o.height, y2)):
        for x in range(max(0, x1), min(o.width, x2)):
            a, b = o.getpixel((x, y)), n.getpixel((x, y))
            d = sum(abs(a[i] - b[i]) for i in range(3))
            if d > 60:
                px.append((d, a))
    if not px:
        return "#000000"
    # keep the pixels that differ most from the text-free background: the solid core of the glyphs
    px.sort(key=lambda t: t[0])
    core = [a for _, a in px[-max(3, len(px) // 6):]]
    c = tuple(int(median(p[i] for p in core)) for i in range(3))
    return "#%02x%02x%02x" % c


for pn, pg in PAGES.items():
    for b in pg["blocks"]:
        auto = sample_color(pn, b["box"])
        x1, y1, x2, y2 = b["box"]
        nl = (b["he"].count("\n") + 1) if isinstance(b["he"], str) else 1
        lead_ = b.get("lead", round(b["size"] * 1.2, 2))
        need = max(nl * lead_, (nl - 1) * lead_ + b["size"] * 1.45) + 2
        if y2 - y1 < need:
            cy = (y1 + y2) / 2
            b["box"] = (x1, round(cy - need / 2, 2), x2, round(cy + need / 2, 2))
        b["color"] = b.get("color", auto) if b.get("color", "auto") != "auto" else auto
        if isinstance(b["he"], list):
            b["runs"] = [(t, auto if c == "auto" else c, w) for t, c, w in b["he"]]
        else:
            b["runs"] = [(b["he"], b["color"], b["weight"])]


def b64(p):
    return base64.b64encode(open(p, "rb").read()).decode()


FONT_CSS = "".join(
    f"@font-face{{font-family:'Heebo';font-weight:{w};src:url(data:font/ttf;base64,{b64(f'fonts/Heebo-{s}.ttf')})}}"
    for s, w in (("Regular", 400), ("Bold", 700), ("Black", 900)))
WCSS = {"Regular": 400, "Bold": 700, "Black": 900}


# ---------------- Hebrew pages (HTML -> PDF) ----------------
def page_html(pn, pg):
    w = pg["w"]
    out = [f'<div class="page pg{pn}" style="width:{w}pt"><img class="bg" src="data:image/png;base64,{b64(f"Links/bg_p{pn}.png")}">']
    for i, b in enumerate(pg["blocks"]):
        x1, y1, x2, y2 = b["box"]
        lead = b.get("lead", round(b["size"] * 1.2, 2))
        direction = "ltr" if b.get("ltr") else "rtl"
        paras = []
        for para in (b["he"].split("\n") if isinstance(b["he"], str) else [None]):
            if para is None:
                inner = "".join(f'<span style="color:{c};font-weight:{WCSS[wt]}">{html.escape(t)}</span>' for t, c, wt in b["runs"])
            else:
                inner = html.escape(para)
            paras.append(f"<p>{inner}</p>")
        out.append(
            f'<div class="blk" data-id="{pn}-{i}" style="left:{x1}pt;top:{y1}pt;width:{x2 - x1}pt;height:{y2 - y1}pt;'
            f'font-size:{b["size"]}pt;line-height:{lead}pt;font-weight:{WCSS[b["weight"]]};color:{b["color"]};'
            f'text-align:{b["align"]};direction:{direction};white-space:{"nowrap" if b.get("nowrap") else "normal"}">{"".join(paras)}</div>')
    out.append("</div>")
    return "".join(out)


named = "".join(f"@page p{pn}{{size:{pg['w']}pt {H}pt;margin:0}} .pg{pn}{{page:p{pn}}}" for pn, pg in PAGES.items())
he_html = f"""<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>{FONT_CSS}{named}
body{{margin:0;font-family:Heebo,sans-serif}}
.page{{position:relative;height:{H}pt;overflow:hidden;break-after:page}}
.bg{{position:absolute;left:0;top:0;width:100%;height:100%}}
.blk{{position:absolute;display:flex;flex-direction:column;justify-content:center}}
.blk p{{margin:0}}
</style></head><body>{"".join(page_html(pn, pg) for pn, pg in PAGES.items())}
<script>
const bad=[...document.querySelectorAll('.blk')].filter(b=>b.scrollWidth>b.clientWidth+1||b.scrollHeight>b.clientHeight+1).map(b=>b.dataset.id+'('+b.scrollWidth+'x'+b.scrollHeight+'>'+b.clientWidth+'x'+b.clientHeight+')');
document.title='OVER:'+bad.join(',');
</script></body></html>"""
open("catalog_HE.html", "w").write(he_html)
flags = ["--headless", "--no-sandbox", "--disable-gpu", "--virtual-time-budget=4000"]
subprocess.run([CHROME, *flags, "--no-pdf-header-footer", "--print-to-pdf=catalog_HE.pdf", "catalog_HE.html"],
               check=True, stderr=subprocess.DEVNULL)
dom = subprocess.run([CHROME, *flags, "--dump-dom", "catalog_HE.html"], capture_output=True, text=True).stdout
print("overflowing blocks:", dom.split("<title>")[1].split("</title>")[0])

# render Hebrew pages to PNG for the review sheet
subprocess.run(["pdftoppm", "-r", "150", "-png", "catalog_HE.pdf", "he150"], check=True)
he_pngs = sorted(f for f in os.listdir(".") if f.startswith("he150-"))


# ---------------- review sheet ----------------
def img_tag(p):
    return f'<img src="data:image/png;base64,{b64(p)}">'


sheets = []
for (pn, pg), hp in zip(PAGES.items(), he_pngs):
    sheets.append(f"""<section class="sheet">
<header><span>Catalog page {pn}</span><span class="t">Original (Italian) &nbsp;→&nbsp; Hebrew draft</span></header>
<div class="pair"><figure>{img_tag(f"orig150_p{pn}.png")}<figcaption>Original · Italian</figcaption></figure>
<figure>{img_tag(hp)}<figcaption>Hebrew · עברית</figcaption></figure></div></section>""")
rows = []
for pn, pg in PAGES.items():
    for b in pg["blocks"]:
        he = b["he"] if isinstance(b["he"], str) else "".join(t for t, _, _ in b["he"])
        if he.replace("\n", " ") == b["it"].replace("\n", " "):
            continue
        rows.append(f'<tr><td class="pg">{pn}</td><td class="it">{html.escape(b["it"]).replace(chr(10), "<br>")}</td>'
                    f'<td class="he" dir="rtl">{html.escape(he).replace(chr(10), "<br>")}</td><td class="ok"></td></tr>')
review = f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONT_CSS}
@page{{size:297mm 210mm;margin:0}}
body{{margin:0;font-family:Heebo,sans-serif;color:#1a1a1a}}
.sheet{{width:297mm;height:210mm;box-sizing:border-box;padding:7mm 10mm 6mm;break-after:page;background:#f2f2f0;display:flex;flex-direction:column}}
header{{display:flex;justify-content:space-between;font-weight:700;font-size:11pt;margin-bottom:3mm}}
header .t{{font-weight:400;color:#555}}
.pair{{flex:1;display:flex;gap:8mm;justify-content:center;min-height:0}}
figure{{margin:0;display:flex;flex-direction:column;align-items:center;min-height:0}}
figure img{{height:178mm;box-shadow:0 1px 4px rgba(0,0,0,.25);background:#fff}}
figcaption{{font-size:9pt;margin-top:2mm;color:#444;font-weight:700}}
.cover{{justify-content:center;padding:20mm 24mm;background:#fff}}
.cover h1{{font-size:26pt;margin:0 0 4mm}} .cover p{{font-size:11pt;line-height:1.55;margin:0 0 3mm;max-width:210mm}}
.bar{{height:5mm;background:#ffcc00;margin-bottom:8mm;width:40mm}}
.tbl{{background:#fff;height:auto;min-height:210mm;break-after:auto}}
table{{border-collapse:collapse;width:100%;font-size:8.5pt}}
th,td{{border:.5pt solid #bbb;padding:1.6mm 2mm;vertical-align:top;text-align:left}}
th{{background:#ffcc00}} td.pg{{width:9mm;text-align:center}} td.he{{text-align:right}} td.ok{{width:16mm}}
tr{{break-inside:avoid}}
</style></head><body>
<section class="sheet cover"><div class="bar"></div><h1>Stanley laser-levels catalog — Hebrew test</h1>
<p><b>What this is:</b> 5 pages of the Italian Stanley catalog converted to Hebrew automatically. Each sheet shows the original on the left and the Hebrew draft on the right. The last pages list every text change (Italian → Hebrew) with a column to tick off.</p>
<p><b>How it was made:</b> the Italian text was removed from the original PDF, so the photos, colours and logos are the original artwork. Hebrew text was then placed in the same positions, in the same colours, in the free Hebrew font Heebo. The same pages are also delivered as an InDesign file (IDML) with editable Hebrew text frames.</p>
<p><b>What to look for:</b> translation wording, headline phrasing (pages 2 and 4 are marketing copy and were adapted, not translated word for word), text size and alignment, and anything that still needs a designer's touch.</p>
<p><b>Not changed on purpose:</b> product codes, laser safety values, the website address and text that is part of photos or icons.</p></section>
{"".join(sheets)}
<section class="sheet tbl"><header><span>All text changes</span><span class="t">Tick ✓ when approved</span></header>
<table><tr><th>Page</th><th>Original (Italian)</th><th style="text-align:right">Hebrew</th><th>OK?</th></tr>{"".join(rows)}</table></section>
</body></html>"""
open("catalog_review.html", "w").write(review)
subprocess.run([CHROME, *flags, "--no-pdf-header-footer", "--print-to-pdf=catalog_review.pdf", "catalog_review.html"],
               check=True, stderr=subprocess.DEVNULL)

# ---------------- IDML ----------------
DOM = "14.0"
NS = 'xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"'
HDR = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
HALF = H / 2
colors = {}


def color_ref(hexc):
    hexc = hexc.lower()
    if hexc not in colors:
        r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
        colors[hexc] = f"Color/HE {hexc[1:]}"
    return colors[hexc]


def path(x1, y1, x2, y2):
    pts = [(x1, y1 - HALF), (x1, y2 - HALF), (x2, y2 - HALF), (x2, y1 - HALF)]
    pp = "".join(f'<PathPointType Anchor="{x:.3f} {y:.3f}" LeftDirection="{x:.3f} {y:.3f}" RightDirection="{x:.3f} {y:.3f}"/>' for x, y in pts)
    return f'<Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>{pp}</PathPointArray></GeometryPathType></PathGeometry></Properties>'


JUST = {"right": "RightAlign", "left": "LeftAlign", "center": "CenterAlign"}
stories, spreads = {}, {}
for pn, pg in PAGES.items():
    w = pg["w"]
    items = [f'<Rectangle Self="bg{pn}" ContentType="GraphicType" StrokeWeight="0" FillColor="Swatch/None" StrokeColor="Swatch/None" ItemTransform="1 0 0 1 0 0" Locked="true">{path(0, 0, w, H)}'
             f'<Image Self="bg{pn}i" ItemTransform="1 0 0 1 0 {-HALF:.3f}" ActualPpi="300 300" EffectivePpi="300 300" Space="$ID/RGB">'
             f'<Properties><Profile type="string">$ID/None</Profile><GraphicBounds Left="0" Top="0" Right="{w:.3f}" Bottom="{H:.3f}"/></Properties>'
             f'<Link Self="bg{pn}l" AssetURL="$ID/" AssetID="$ID/" LinkResourceURI="file:Links/bg_p{pn}.png" LinkResourceFormat="$ID/Portable Network Graphics (PNG)" '
             f'StoredState="Normal" LinkClassID="35906" LinkClientID="257" LinkResourceModified="false" LinkObjectModified="false" ShowInUI="true" '
             f'CanEmbed="true" CanUnembed="true" CanPackage="true" ImportPolicy="NoAutoImport" ExportPolicy="NoAutoExport" '
             f'LinkImportStamp="" LinkImportModificationTime="" LinkImportTime="" LinkResourceSize="0~0"/></Image></Rectangle>']
    for i, b in enumerate(pg["blocks"]):
        sid, fid = f"st_{pn}_{i}", f"tf_{pn}_{i}"
        x1, y1, x2, y2 = b["box"]
        lead = b.get("lead", round(b["size"] * 1.2, 2))
        pdir = "LeftToRightDirection" if b.get("ltr") else "RightToLeftDirection"
        paras = b["he"].split("\n") if isinstance(b["he"], str) else [None]
        psr = []
        for k, para in enumerate(paras):
            runs = b["runs"] if para is None else [(para, b["color"], b["weight"])]
            br = "<Br/>" if k < len(paras) - 1 else ""
            crs = "".join(f'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]" PointSize="{b["size"]}" '
                          f'FontStyle="{wt}" FillColor="{color_ref(c)}"><Properties><AppliedFont type="string">Heebo</AppliedFont>'
                          f'<Leading type="unit">{lead}</Leading></Properties><Content>{escape(t)}</Content>'
                          f'{br if j == len(runs) - 1 else ""}</CharacterStyleRange>' for j, (t, c, wt) in enumerate(runs))
            psr.append(f'<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/HE Catalog" Justification="{JUST[b["align"]]}" '
                       f'ParagraphDirection="{pdir}">{crs}</ParagraphStyleRange>')
        stories[sid] = (f'{HDR}<idPkg:Story {NS} DOMVersion="{DOM}"><Story Self="{sid}" AppliedTOCStyle="n" UserText="true" IsEndnoteStory="false" '
                        f'TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n"><StoryPreference OpticalMarginAlignment="false" '
                        f'OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="{pdir}"/>'
                        f'<InCopyExportOption IncludeGraphicProxies="true" IncludeAllResources="false"/>{"".join(psr)}</Story></idPkg:Story>')
        items.append(f'<TextFrame Self="{fid}" ParentStory="{sid}" PreviousTextFrame="n" NextTextFrame="n" ContentType="TextType" '
                     f'FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="1 0 0 1 0 0">{path(x1, y1, x2, y2)}'
                     f'<TextFramePreference TextColumnCount="1" FirstBaselineOffset="AscentOffset" VerticalJustification="CenterAlign" '
                     f'AutoSizingType="Off" InsetSpacing="0 0 0 0"/></TextFrame>')
    spreads[f"s{pn}"] = (
        f'{HDR}<idPkg:Spread {NS} DOMVersion="{DOM}"><Spread Self="s{pn}" PageTransitionType="None" ShowMasterItems="true" PageCount="1" '
        f'BindingLocation="0" AllowPageShuffle="true" ItemTransform="1 0 0 1 0 0" FlattenerOverride="Default">'
        f'<Page Self="p{pn}" Name="{pn}" AppliedMaster="n" OverrideList="" MasterPageTransform="1 0 0 1 0 0" '
        f'GeometricBounds="0 0 {H} {w}" ItemTransform="1 0 0 1 0 {-HALF:.3f}" AppliedAlternateLayout="n" LayoutRule="Off" '
        f'SnapshotBlendingMode="IgnoreLayoutSnapshots" OptionalPage="false" GridStartingPoint="TopOutside" UseMasterGrid="true">'
        f'<Properties><PageColor type="enumeration">UseMasterColor</PageColor></Properties>'
        f'<MarginPreference ColumnCount="1" ColumnGutter="12" Top="20" Bottom="20" Left="20" Right="20" ColumnDirection="Horizontal" ColumnsPositions="0 {w - 40:.3f}"/>'
        f'</Page>{"".join(items)}</Spread></idPkg:Spread>')

color_xml = "".join(
    f'<Color Self="{ref}" Model="Process" Space="RGB" ColorValue="{int(h[1:3], 16)} {int(h[3:5], 16)} {int(h[5:7], 16)}" '
    f'ColorOverride="Normal" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="{ref[6:]}" ColorEditable="true" '
    f'ColorRemovable="true" Visible="true" SwatchCreatorID="7937"/>' for h, ref in colors.items())
graphic = (f'{HDR}<idPkg:Graphic {NS} DOMVersion="{DOM}">'
           '<Color Self="Color/Black" Model="Process" Space="CMYK" ColorValue="0 0 0 100" ColorOverride="Specialblack" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Black" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
           '<Color Self="Color/Paper" Model="Process" Space="CMYK" ColorValue="0 0 0 0" ColorOverride="Specialpaper" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Paper" ColorEditable="true" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
           '<Color Self="Color/Registration" Model="Registration" Space="CMYK" ColorValue="100 100 100 100" ColorOverride="Specialregistration" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Registration" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
           f'{color_xml}<Swatch Self="Swatch/None" Name="None" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
           '<StrokeStyle Self="StrokeStyle/$ID/Solid" Name="$ID/Solid"/></idPkg:Graphic>')
fonts = (f'{HDR}<idPkg:Fonts {NS} DOMVersion="{DOM}"><FontFamily Self="di_heebo" Name="Heebo">'
         + "".join(f'<Font Self="di_heebo_{s}" FontFamily="Heebo" Name="Heebo {s}" PostScriptName="Heebo-{s}" Status="Installed" FontStyleName="{s}" '
                   f'FontType="OpenTypeTrueType" WritingScript="0" FullName="Heebo {s}" FullNameNative="Heebo {s}" FontStyleNameNative="{s}" PlatformName="$ID/" Version=""/>'
                   for s in ("Regular", "Bold", "Black")) + '</FontFamily></idPkg:Fonts>')
styles = (f'{HDR}<idPkg:Styles {NS} DOMVersion="{DOM}">'
          '<RootCharacterStyleGroup Self="u79"><CharacterStyle Self="CharacterStyle/$ID/[No character style]" Imported="false" Name="$ID/[No character style]"/></RootCharacterStyleGroup>'
          '<RootParagraphStyleGroup Self="u78">'
          '<ParagraphStyle Self="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[No paragraph style]" Imported="false" NextStyle="ParagraphStyle/$ID/[No paragraph style]" KeyboardShortcut="0 0"/>'
          '<ParagraphStyle Self="ParagraphStyle/$ID/NormalParagraphStyle" Name="$ID/NormalParagraphStyle" Imported="false" NextStyle="ParagraphStyle/$ID/NormalParagraphStyle" KeyboardShortcut="0 0"><Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn></Properties></ParagraphStyle>'
          '<ParagraphStyle Self="ParagraphStyle/HE Catalog" Name="HE Catalog" Imported="false" NextStyle="ParagraphStyle/HE Catalog" KeyboardShortcut="0 0" '
          'ParagraphDirection="RightToLeftDirection" ParagraphJustification="DefaultJustification" Composer="$ID/HL Composer Optyca" Justification="RightAlign" Hyphenation="false">'
          '<Properties><BasedOn type="object">ParagraphStyle/$ID/NormalParagraphStyle</BasedOn><AppliedFont type="string">Heebo</AppliedFont></Properties></ParagraphStyle>'
          '</RootParagraphStyleGroup>'
          '<RootCellStyleGroup Self="u7e"><CellStyle Self="CellStyle/$ID/[None]" AppliedParagraphStyle="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[None]"/></RootCellStyleGroup>'
          '<RootTableStyleGroup Self="u7d"><TableStyle Self="TableStyle/$ID/[No table style]" Name="$ID/[No table style]"/><TableStyle Self="TableStyle/$ID/[Basic Table]" Name="$ID/[Basic Table]"/></RootTableStyleGroup>'
          '<RootObjectStyleGroup Self="u80"><ObjectStyle Self="ObjectStyle/$ID/[None]" Name="$ID/[None]"/>'
          '<ObjectStyle Self="ObjectStyle/$ID/[Normal Graphics Frame]" Name="$ID/[Normal Graphics Frame]"/>'
          '<ObjectStyle Self="ObjectStyle/$ID/[Normal Text Frame]" Name="$ID/[Normal Text Frame]"/></RootObjectStyleGroup>'
          '</idPkg:Styles>')
prefs = (f'{HDR}<idPkg:Preferences {NS} DOMVersion="{DOM}"><DocumentPreference PageHeight="{H}" PageWidth="419.528" '
         f'PagesPerDocument="{len(PAGES)}" FacingPages="false" PageBinding="LeftEdge" AllowPageShuffle="true" Intent="PrintIntent" '
         f'CreatePrimaryTextFrame="false"/></idPkg:Preferences>')
tags = f'{HDR}<idPkg:Tags {NS} DOMVersion="{DOM}"><XMLTag Self="XMLTag/Root" Name="Root"><Properties><TagColor type="enumeration">LightGray</TagColor></Properties></XMLTag></idPkg:Tags>'
backing = (f'{HDR}<idPkg:BackingStory {NS} DOMVersion="{DOM}"><XmlStory Self="u_bs" UserText="true" IsEndnoteStory="false" AppliedTOCStyle="n" '
           f'TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n"><ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle">'
           f'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"/></ParagraphStyleRange></XmlStory></idPkg:BackingStory>')
first = f"p{next(iter(PAGES))}"
designmap = (f'{HDR}<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="14.0(130)" ?>\n'
             f'<Document {NS} DOMVersion="{DOM}" Self="d" StoryList="{" ".join(stories)}" Name="Catalog_HE.indd" ZeroPoint="0 0" ActiveLayer="uLayer" '
             f'CMYKProfile="Coated FOGRA39 (ISO 12647-2:2004)" RGBProfile="sRGB IEC61966-2.1" SolidColorIntent="UseColorSettings" '
             f'AfterBlendingIntent="UseColorSettings" DefaultImageIntent="UseColorSettings" RGBPolicy="PreserveEmbeddedProfiles" '
             f'CMYKPolicy="CombinationOfPreserveAndSafeCmyk" AccurateLABSpots="false">'
             '<idPkg:Graphic src="Resources/Graphic.xml"/><idPkg:Fonts src="Resources/Fonts.xml"/><idPkg:Styles src="Resources/Styles.xml"/>'
             '<idPkg:Preferences src="Resources/Preferences.xml"/><idPkg:Tags src="XML/Tags.xml"/>'
             '<Layer Self="uLayer" Name="Layer 1" Visible="true" Locked="false" IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true"><Properties><LayerColor type="enumeration">LightBlue</LayerColor></Properties></Layer>'
             + "".join(f'<idPkg:Spread src="Spreads/Spread_{s}.xml"/>' for s in spreads)
             + f'<Section Self="uSec" Length="{len(PAGES)}" Name="" ContinueNumbering="false" IncludeSectionPrefix="false" PageNumberStyle="Arabic" PageStart="{first}" SectionPrefix="" Marker="" PageNumberStart="1"/>'
             '<idPkg:BackingStory src="XML/BackingStory.xml"/>'
             + "".join(f'<idPkg:Story src="Stories/Story_{s}.xml"/>' for s in stories) + '</Document>')
with zipfile.ZipFile("Catalog_HE.idml", "w") as z:
    z.writestr(zipfile.ZipInfo("mimetype"), "application/vnd.adobe.indesign-idml-package", compress_type=zipfile.ZIP_STORED)
    files = {"META-INF/container.xml": HDR + '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="designmap.xml" media-type="text/xml"/></rootfiles></container>',
             "designmap.xml": designmap, "Resources/Graphic.xml": graphic, "Resources/Fonts.xml": fonts,
             "Resources/Styles.xml": styles, "Resources/Preferences.xml": prefs, "XML/Tags.xml": tags, "XML/BackingStory.xml": backing,
             **{f"Spreads/Spread_{s}.xml": x for s, x in spreads.items()}, **{f"Stories/Story_{s}.xml": x for s, x in stories.items()}}
    for n, d in files.items():
        z.writestr(n, d, compress_type=zipfile.ZIP_DEFLATED)
print("colors:", json.dumps({f"{pn}-{i}": b["color"] for pn, pg in PAGES.items() for i, b in enumerate(pg["blocks"])}))
