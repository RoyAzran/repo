"""Build a Hebrew (RTL) IDML package for the FME190 manual sample.

Page 1: original cover image + Hebrew label
Page 2: original drawings page (language-neutral)
Pages 3-4: Hebrew translation of the English safety pages, two RTL columns, threaded.
"""
import os, zipfile
from xml.sax.saxutils import escape
from content_he import C

W, H = 419.528, 595.276
HALF = H / 2
DOM = "14.0"
NS = 'xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"'
HDR = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

FONT = os.environ.get("IDML_FONT", "Arial")


def sy(y):  # page y -> spread y
    return y - HALF


def path(x1, y1, x2, y2):
    pts = [(x1, sy(y1)), (x1, sy(y2)), (x2, sy(y2)), (x2, sy(y1))]
    pp = "".join(
        f'<PathPointType Anchor="{x:.3f} {y:.3f}" LeftDirection="{x:.3f} {y:.3f}" RightDirection="{x:.3f} {y:.3f}"/>'
        for x, y in pts)
    return (f'<Properties><PathGeometry><GeometryPathType PathOpen="false"><PathPointArray>{pp}'
            f'</PathPointArray></GeometryPathType></PathGeometry></Properties>')


# ---------------- stories ----------------
stories = {}  # id -> xml


def story_xml(sid, paras):
    """paras: list of (paragraph_style, [(char_style, text), ...])"""
    body = []
    for i, (pst, runs) in enumerate(paras):
        last = i == len(paras) - 1
        rs = []
        for j, (cst, txt) in enumerate(runs):
            br = "" if (last or j != len(runs) - 1) else "<Br/>"
            # tabs stay as literal tab characters inside Content
            content = f"<Content>{escape(txt)}</Content>"
            rs.append(f'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/{cst}">{content}{br}</CharacterStyleRange>')
        body.append(f'<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/{pst}">{"".join(rs)}</ParagraphStyleRange>')
    stories[sid] = (
        f'{HDR}<idPkg:Story {NS} DOMVersion="{DOM}">'
        f'<Story Self="{sid}" AppliedTOCStyle="n" UserText="true" IsEndnoteStory="false" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">'
        f'<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="RightToLeftDirection"/>'
        f'<InCopyExportOption IncludeGraphicProxies="true" IncludeAllResources="false"/>'
        f'{"".join(body)}</Story></idPkg:Story>')


NOCS = "$ID/[No character style]"
main = []
for st, lead, txt in C:
    pst = {"h1": "HE Heading 1", "h2": "HE Heading 2", "warn": "HE Warning", "bodyb": "HE Body",
           "body": "HE Body", "item": "HE Item", "bullet": "HE Bullet"}[st]
    runs = []
    if lead:
        runs.append(("HE Bold" if st in ("item", "bodyb") else NOCS, lead))
    if txt:
        runs.append((NOCS, txt))
    main.append((pst, runs))
story_xml("u_main", main)
story_xml("u_cover", [("HE Cover Title", [(NOCS, "הוראות הפעלה")]),
                      ("HE Cover Sub", [(NOCS, "תרגום מהוראות היצרן המקוריות")])])
for n in (3, 4):
    story_xml(f"u_pill{n}", [("HE Pill", [(NOCS, "עברית")])])
    story_xml(f"u_folio{n}", [("HE Folio", [(NOCS, str(n))])])


# ---------------- page items ----------------
def text_frame(fid, sid, x1, y1, x2, y2, prev="n", nxt="n", fill="Swatch/None", inset=0):
    return (f'<TextFrame Self="{fid}" ParentStory="{sid}" PreviousTextFrame="{prev}" NextTextFrame="{nxt}" '
            f'ContentType="TextType" FillColor="{fill}" StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="1 0 0 1 0 0">'
            f'{path(x1, y1, x2, y2)}'
            f'<TextFramePreference TextColumnCount="1" TextColumnGutter="12" UseFixedColumnWidth="false" '
            f'FirstBaselineOffset="AscentOffset" VerticalJustification="TopAlign" AutoSizingType="Off" '
            f'InsetSpacing="{inset} {inset} {inset} {inset}"/>'
            f'</TextFrame>')


def image_frame(rid, link_name, x1, y1, x2, y2):
    gw, gh = x2 - x1, y2 - y1
    return (f'<Rectangle Self="{rid}" ContentType="GraphicType" StrokeWeight="0" FillColor="Swatch/None" '
            f'StrokeColor="Swatch/None" ItemTransform="1 0 0 1 0 0">{path(x1, y1, x2, y2)}'
            f'<FrameFittingOption FittingOnEmptyFrame="Proportionally"/>'
            f'<Image Self="{rid}_img" ItemTransform="1 0 0 1 {x1:.3f} {sy(y1):.3f}" ActualPpi="300 300" EffectivePpi="300 300" ImageRenderingIntent="UseColorSettings" Space="$ID/RGB">'
            f'<Properties><Profile type="string">$ID/None</Profile>'
            f'<GraphicBounds Left="0" Top="0" Right="{gw:.3f}" Bottom="{gh:.3f}"/></Properties>'
            f'<Link Self="{rid}_lnk" AssetURL="$ID/" AssetID="$ID/" LinkResourceURI="file:Links/{link_name}" '
            f'LinkResourceFormat="$ID/Portable Network Graphics (PNG)" StoredState="Normal" LinkClassID="35906" '
            f'LinkClientID="257" LinkResourceModified="false" LinkObjectModified="false" ShowInUI="true" '
            f'CanEmbed="true" CanUnembed="true" CanPackage="true" ImportPolicy="NoAutoImport" '
            f'ExportPolicy="NoAutoExport" LinkImportStamp="" LinkImportModificationTime="" LinkImportTime="" LinkResourceSize="0~0"/>'
            f'</Image></Rectangle>')


M, TOP, BOT, GUT = 28, 44, 555, 14
CW = (W - 2 * M - GUT) / 2
RX1, RX2 = W - M - CW, W - M        # right column (first in RTL)
LX1, LX2 = M, M + CW                # left column

pages_items = {
    1: [image_frame("r_cover", "cover.png", 0, 0, W, H),
        text_frame("tf_cover", "u_cover", 215, 486, 395, 530)],
    2: [image_frame("r_draw", "drawings.png", 0, 0, W, H)],
    3: [text_frame("tf3r", "u_main", RX1, TOP, RX2, BOT, prev="n", nxt="tf3l"),
        text_frame("tf3l", "u_main", LX1, TOP, LX2, BOT, prev="tf3r", nxt="tf4r"),
        text_frame("pill3", "u_pill3", W - M - 62, 18, W - M, 32, fill="Color/Black", inset=1.5),
        text_frame("folio3", "u_folio3", M, 568, M + 20, 580, fill="Color/Black", inset=1.5)],
    4: [text_frame("tf4r", "u_main", RX1, TOP, RX2, BOT, prev="tf3l", nxt="tf4l"),
        text_frame("tf4l", "u_main", LX1, TOP, LX2, BOT, prev="tf4r", nxt="n"),
        text_frame("pill4", "u_pill4", W - M - 62, 18, W - M, 32, fill="Color/Black", inset=1.5),
        text_frame("folio4", "u_folio4", W - M - 20, 568, W - M, 580, fill="Color/Black", inset=1.5)],
}

spreads = {}
for n, items in pages_items.items():
    spreads[f"s{n}"] = (
        f'{HDR}<idPkg:Spread {NS} DOMVersion="{DOM}">'
        f'<Spread Self="s{n}" PageTransitionType="None" PageTransitionDirection="NotApplicable" PageTransitionDuration="Medium" '
        f'ShowMasterItems="true" PageCount="1" BindingLocation="0" AllowPageShuffle="true" ItemTransform="1 0 0 1 0 0" FlattenerOverride="Default">'
        f'<Page Self="p{n}" TabOrder="" AppliedMaster="uMaster" OverrideList="" MasterPageTransform="1 0 0 1 0 0" Name="{n}" '
        f'AppliedTrapPreset="TrapPreset/$ID/kDefaultTrapStyleName" GeometricBounds="0 0 {H} {W}" ItemTransform="1 0 0 1 0 -{HALF}" '
        f'AppliedAlternateLayout="n" LayoutRule="UseMaster" SnapshotBlendingMode="IgnoreLayoutSnapshots" OptionalPage="false" GridStartingPoint="TopOutside" UseMasterGrid="true">'
        f'<Properties><PageColor type="enumeration">UseMasterColor</PageColor></Properties>'
        f'<MarginPreference ColumnCount="2" ColumnGutter="{GUT}" Top="{TOP}" Bottom="{H - BOT}" Left="{M}" Right="{M}" ColumnDirection="Horizontal" ColumnsPositions="0 {CW:.3f} {CW + GUT:.3f} {2 * CW + GUT:.3f}"/>'
        f'</Page>{"".join(items)}</Spread></idPkg:Spread>')

master = (
    f'{HDR}<idPkg:MasterSpread {NS} DOMVersion="{DOM}">'
    f'<MasterSpread Self="uMaster" ItemTransform="1 0 0 1 0 0" OverriddenPageItemProps="" NamePrefix="A" BaseName="Master" '
    f'ShowMasterItems="true" PageCount="1" PageColor="UseMasterColor" PrimaryTextFrame="n">'
    f'<Properties><PageColor type="enumeration">UseMasterColor</PageColor></Properties>'
    f'<Page Self="uMP" TabOrder="" AppliedMaster="n" OverrideList="" MasterPageTransform="1 0 0 1 0 0" Name="A" '
    f'AppliedTrapPreset="TrapPreset/$ID/kDefaultTrapStyleName" GeometricBounds="0 0 {H} {W}" ItemTransform="1 0 0 1 0 -{HALF}" '
    f'AppliedAlternateLayout="n" LayoutRule="Off" SnapshotBlendingMode="IgnoreLayoutSnapshots" OptionalPage="false" GridStartingPoint="TopOutside" UseMasterGrid="true">'
    f'<Properties><PageColor type="enumeration">UseMasterColor</PageColor></Properties>'
    f'<MarginPreference ColumnCount="2" ColumnGutter="{GUT}" Top="{TOP}" Bottom="{H - BOT}" Left="{M}" Right="{M}" ColumnDirection="Horizontal" ColumnsPositions="0 {CW:.3f} {CW + GUT:.3f} {2 * CW + GUT:.3f}"/>'
    f'</Page></MasterSpread></idPkg:MasterSpread>')

# ---------------- resources ----------------
graphic = (
    f'{HDR}<idPkg:Graphic {NS} DOMVersion="{DOM}">'
    '<Color Self="Color/Black" Model="Process" Space="CMYK" ColorValue="0 0 0 100" ColorOverride="Specialblack" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Black" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
    '<Color Self="Color/Paper" Model="Process" Space="CMYK" ColorValue="0 0 0 0" ColorOverride="Specialpaper" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Paper" ColorEditable="true" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
    '<Color Self="Color/Registration" Model="Registration" Space="CMYK" ColorValue="100 100 100 100" ColorOverride="Specialregistration" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Registration" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
    '<Color Self="Color/Stanley Yellow" Model="Process" Space="CMYK" ColorValue="0 15 100 0" ColorOverride="Normal" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Stanley Yellow" ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937"/>'
    '<Swatch Self="Swatch/None" Name="None" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
    '<StrokeStyle Self="StrokeStyle/$ID/Solid" Name="$ID/Solid"/>'
    '</idPkg:Graphic>')

fonts = (
    f'{HDR}<idPkg:Fonts {NS} DOMVersion="{DOM}">'
    f'<FontFamily Self="di_arial" Name="{FONT}">'
    f'<Font Self="di_arial_r" FontFamily="{FONT}" Name="{FONT}" PostScriptName="ArialMT" Status="Installed" FontStyleName="Regular" FontType="OpenTypeTrueType" WritingScript="0" FullName="Arial" FullNameNative="Arial" FontStyleNameNative="Regular" PlatformName="$ID/" Version=""/>'
    f'<Font Self="di_arial_b" FontFamily="{FONT}" Name="{FONT} Bold" PostScriptName="Arial-BoldMT" Status="Installed" FontStyleName="Bold" FontType="OpenTypeTrueType" WritingScript="0" FullName="Arial Bold" FullNameNative="Arial Bold" FontStyleNameNative="Bold" PlatformName="$ID/" Version=""/>'
    f'</FontFamily></idPkg:Fonts>')


def pstyle(name, size, lead, style="Regular", sb=0, sa=2, ri=0, fli=0, color="Color/Black", just="RightAlign"):
    return (f'<ParagraphStyle Self="ParagraphStyle/{name}" Name="{name}" Imported="false" NextStyle="ParagraphStyle/{name}" '
            f'KeyboardShortcut="0 0" PointSize="{size}" FontStyle="{style}" FillColor="{color}" '
            f'ParagraphDirection="RightToLeftDirection" ParagraphJustification="DefaultJustification" '
            f'Composer="$ID/HL Composer Optyca" CharacterDirection="DefaultDirection" DigitsType="DefaultDigits" '
            f'Justification="{just}" SpaceBefore="{sb}" SpaceAfter="{sa}" RightIndent="{ri}" FirstLineIndent="{fli}" Hyphenation="false">'
            f'<Properties><BasedOn type="object">ParagraphStyle/$ID/NormalParagraphStyle</BasedOn>'
            f'<AppliedFont type="string">{FONT}</AppliedFont><Leading type="unit">{lead}</Leading>'
            f'<TabList type="list"><ListItem type="record"><Alignment type="enumeration">LeftAlign</Alignment>'
            f'<AlignmentCharacter type="string">.</AlignmentCharacter><Leader type="string"></Leader>'
            f'<Position type="unit">{max(ri, 1)}</Position></ListItem></TabList></Properties></ParagraphStyle>')


styles = (
    f'{HDR}<idPkg:Styles {NS} DOMVersion="{DOM}">'
    '<RootCharacterStyleGroup Self="u79">'
    '<CharacterStyle Self="CharacterStyle/$ID/[No character style]" Imported="false" SplitDocument="false" EmitCss="true" StyleUniqueId="$ID/" IncludeClass="true" Name="$ID/[No character style]"/>'
    '<CharacterStyle Self="CharacterStyle/HE Bold" Imported="false" KeyboardShortcut="0 0" Name="HE Bold" FontStyle="Bold"/>'
    '</RootCharacterStyleGroup>'
    '<RootParagraphStyleGroup Self="u78">'
    '<ParagraphStyle Self="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[No paragraph style]" Imported="false" NextStyle="ParagraphStyle/$ID/[No paragraph style]" KeyboardShortcut="0 0"/>'
    '<ParagraphStyle Self="ParagraphStyle/$ID/NormalParagraphStyle" Name="$ID/NormalParagraphStyle" Imported="false" NextStyle="ParagraphStyle/$ID/NormalParagraphStyle" KeyboardShortcut="0 0">'
    '<Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn><PreviewColor type="enumeration">Nothing</PreviewColor></Properties></ParagraphStyle>'
    + pstyle("HE Heading 1", 12, 14, "Bold", sb=6, sa=3)
    + pstyle("HE Heading 2", 8.5, 10.5, "Bold", sb=5, sa=2)
    + pstyle("HE Warning", 7.5, 9.6, "Bold", sa=3)
    + pstyle("HE Body", 7.5, 9.6, sa=2.5)
    + pstyle("HE Item", 7.5, 9.6, sa=2, ri=9, fli=-9)
    + pstyle("HE Bullet", 7.5, 9.6, sa=2, ri=8, fli=-8)
    + pstyle("HE Pill", 8, 10, "Bold", sa=0, color="Color/Paper", just="CenterAlign")
    + pstyle("HE Folio", 7, 9, "Bold", sa=0, color="Color/Paper", just="CenterAlign")
    + pstyle("HE Cover Title", 15, 18, "Bold", sa=2)
    + pstyle("HE Cover Sub", 8, 10, sa=0)
    + '</RootParagraphStyleGroup>'
    '<TOCStyle Self="TOCStyle/$ID/DefaultTOCStyleName" TitleStyle="ParagraphStyle/$ID/[No paragraph style]" Title="Contents" Name="$ID/DefaultTOCStyleName" RunIn="false" IncludeHidden="false" IncludeBookDocuments="false" CreateBookmarks="true" SetStoryDirection="RightToLeftDirection" NumberedParagraphs="IncludeFullParagraph"/>'
    '<RootCellStyleGroup Self="u7e"><CellStyle Self="CellStyle/$ID/[None]" AppliedParagraphStyle="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[None]"/></RootCellStyleGroup>'
    '<RootTableStyleGroup Self="u7d"><TableStyle Self="TableStyle/$ID/[No table style]" Name="$ID/[No table style]"/>'
    '<TableStyle Self="TableStyle/$ID/[Basic Table]" Name="$ID/[Basic Table]"/></RootTableStyleGroup>'
    '<RootObjectStyleGroup Self="u80">'
    '<ObjectStyle Self="ObjectStyle/$ID/[None]" Name="$ID/[None]" AppliedParagraphStyle="ParagraphStyle/$ID/[No paragraph style]" FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0"/>'
    '<ObjectStyle Self="ObjectStyle/$ID/[Normal Graphics Frame]" Name="$ID/[Normal Graphics Frame]" AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle" FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0"/>'
    '<ObjectStyle Self="ObjectStyle/$ID/[Normal Text Frame]" Name="$ID/[Normal Text Frame]" AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle" FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0"/>'
    '<ObjectStyle Self="ObjectStyle/$ID/[Normal Grid]" Name="$ID/[Normal Grid]" AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle" FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0"/>'
    '</RootObjectStyleGroup>'
    '<TrapPreset Self="TrapPreset/$ID/kDefaultTrapStyleName" Name="$ID/kDefaultTrapStyleName"/>'
    '</idPkg:Styles>')

prefs = (
    f'{HDR}<idPkg:Preferences {NS} DOMVersion="{DOM}">'
    f'<DocumentPreference PageHeight="{H}" PageWidth="{W}" PagesPerDocument="4" FacingPages="false" '
    f'DocumentBleedTopOffset="0" DocumentBleedBottomOffset="0" DocumentBleedInsideOrLeftOffset="0" DocumentBleedOutsideOrRightOffset="0" '
    f'DocumentBleedUniformSize="true" AllowPageShuffle="true" OverprintBlack="true" PageBinding="LeftEdge" ColumnDirection="Horizontal" '
    f'ColumnGuideLocked="true" MasterTextFrame="false" SnippetImportUsesOriginalLocation="false" Intent="PrintIntent" CreatePrimaryTextFrame="false"/>'
    f'<MarginPreference ColumnCount="2" ColumnGutter="{GUT}" Top="{TOP}" Bottom="{H - BOT}" Left="{M}" Right="{M}" ColumnDirection="Horizontal" ColumnsPositions="0 {CW:.3f} {CW + GUT:.3f} {2 * CW + GUT:.3f}"/>'
    f'<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" StoryDirection="RightToLeftDirection"/>'
    f'</idPkg:Preferences>')

tags = (f'{HDR}<idPkg:Tags {NS} DOMVersion="{DOM}"><XMLTag Self="XMLTag/Root" Name="Root">'
        f'<Properties><TagColor type="enumeration">LightGray</TagColor></Properties></XMLTag></idPkg:Tags>')
backing = (f'{HDR}<idPkg:BackingStory {NS} DOMVersion="{DOM}"><XmlStory Self="u_bs" UserText="true" IsEndnoteStory="false" '
           f'AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">'
           f'<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle">'
           f'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"/></ParagraphStyleRange>'
           f'</XmlStory></idPkg:BackingStory>')

story_ids = list(stories)
designmap = (
    f'{HDR}<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="14.0(130)" ?>\n'
    f'<Document {NS} DOMVersion="{DOM}" Self="d" StoryList="{" ".join(story_ids)}" Name="FME190_HE.indd" ZeroPoint="0 0" '
    f'ActiveLayer="uLayer" CMYKProfile="Coated FOGRA39 (ISO 12647-2:2004)" RGBProfile="sRGB IEC61966-2.1" '
    f'SolidColorIntent="UseColorSettings" AfterBlendingIntent="UseColorSettings" DefaultImageIntent="UseColorSettings" '
    f'RGBPolicy="PreserveEmbeddedProfiles" CMYKPolicy="CombinationOfPreserveAndSafeCmyk" AccurateLABSpots="false">'
    '<idPkg:Graphic src="Resources/Graphic.xml"/>'
    '<idPkg:Fonts src="Resources/Fonts.xml"/>'
    '<idPkg:Styles src="Resources/Styles.xml"/>'
    '<idPkg:Preferences src="Resources/Preferences.xml"/>'
    '<idPkg:Tags src="XML/Tags.xml"/>'
    '<Layer Self="uLayer" Name="Layer 1" Visible="true" Locked="false" IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true">'
    '<Properties><LayerColor type="enumeration">LightBlue</LayerColor></Properties></Layer>'
    '<idPkg:MasterSpread src="MasterSpreads/MasterSpread_uMaster.xml"/>'
    + "".join(f'<idPkg:Spread src="Spreads/Spread_{s}.xml"/>' for s in spreads)
    + '<Section Self="uSec" Length="4" Name="" ContinueNumbering="false" IncludeSectionPrefix="false" '
      'PageNumberStyle="Arabic" PageStart="p1" SectionPrefix="" Marker="" PageNumberStart="1" AlternateLayoutLength="4" AlternateLayout=""/>'
    + '<idPkg:BackingStory src="XML/BackingStory.xml"/>'
    + "".join(f'<idPkg:Story src="Stories/Story_{s}.xml"/>' for s in story_ids)
    + '</Document>')

out = os.path.join(OUT_DIR, os.environ.get("IDML_OUT", "FME190_HE.idml"))
with zipfile.ZipFile(out, "w") as z:
    z.writestr(zipfile.ZipInfo("mimetype"), "application/vnd.adobe.indesign-idml-package", compress_type=zipfile.ZIP_STORED)
    def w(name, data):
        z.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)
    w("META-INF/container.xml", HDR + '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
      '<rootfiles><rootfile full-path="designmap.xml" media-type="text/xml"/></rootfiles></container>')
    w("designmap.xml", designmap)
    w("Resources/Graphic.xml", graphic)
    w("Resources/Fonts.xml", fonts)
    w("Resources/Styles.xml", styles)
    w("Resources/Preferences.xml", prefs)
    w("XML/Tags.xml", tags)
    w("XML/BackingStory.xml", backing)
    w("MasterSpreads/MasterSpread_uMaster.xml", master)
    for s, x in spreads.items():
        w(f"Spreads/Spread_{s}.xml", x)
    for s, x in stories.items():
        w(f"Stories/Story_{s}.xml", x)
print("wrote", out)
