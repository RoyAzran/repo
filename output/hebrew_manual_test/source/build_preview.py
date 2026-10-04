import html, base64
from content_he import C
def b64(p): return base64.b64encode(open(p,'rb').read()).decode()
paras=[]
for st, lead, txt in C:
    l = html.escape(lead).replace("\t", " ")
    t = html.escape(txt).replace("\t", " ")
    if st == "item":
        num, rest = lead.split("\t", 1)
        paras.append(f'<p class="item"><span class="n">{html.escape(num)}</span><b>{html.escape(rest)}</b>{t}</p>')
    elif st == "bullet":
        paras.append(f'<p class="item"><span class="n">•</span>{html.escape(txt[2:])}</p>')
    elif st in ("h1","h2"): paras.append(f'<p class="{st}">{l}</p>')
    elif st in ("warn","bodyb"): paras.append(f'<p class="body"><b>{l}</b></p>')
    else: paras.append(f'<p class="body">{t}</p>')
body = "\n".join(paras)
cover, draw = b64("Links/cover.png"), b64("Links/drawings.png")
doc = f"""<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>
@page {{ size: 148mm 210mm; margin: 0 }}
body {{ margin:0; font-family: 'Liberation Sans', Arial, sans-serif; }}
.page {{ width:148mm; height:210mm; position:relative; overflow:hidden; page-break-after:always; }}
.page img.full {{ width:100%; height:100%; display:block }}
.cover-t {{ position:absolute; right:8.6mm; top:171.5mm; text-align:right }}
.cover-t .a {{ font-weight:700; font-size:15pt }} .cover-t .b {{ font-size:8pt }}
.pill {{ position:absolute; right:9.9mm; top:6.3mm; width:21.9mm; background:#000; color:#fff; font:700 8pt/14pt 'Liberation Sans'; text-align:center; border-radius:7pt }}
.folio {{ position:absolute; bottom:5mm; background:#000; color:#fff; font:700 7pt/12pt 'Liberation Sans'; width:7mm; text-align:center }}
.flow {{ position:absolute; top:15.5mm; right:9.9mm; left:9.9mm; height:180.3mm; column-count:2; column-gap:4.9mm; column-fill:auto; font-size:7.5pt; line-height:9.6pt }}
.flow p {{ margin:0 0 2pt }}
.h1 {{ font-weight:700; font-size:12pt; line-height:14pt; margin:6pt 0 3pt!important }}
.h2 {{ font-weight:700; font-size:8.5pt; line-height:10.5pt; margin:5pt 0 2pt!important }}
.item {{ padding-right:9pt; text-indent:-9pt }} .item .n {{ display:inline-block; width:9pt; text-indent:0; font-weight:700 }}
.flow > :first-child {{ margin-top:0!important }}
.rule {{ position:absolute; bottom:12mm; left:9.9mm; right:9.9mm; border-top:.5pt solid #000 }}
</style></head><body>
<div class="page"><img class="full" src="data:image/png;base64,{cover}"><div class="cover-t"><div class="a">הוראות הפעלה</div><div class="b">תרגום מהוראות היצרן המקוריות</div></div></div>
<div class="page"><img class="full" src="data:image/png;base64,{draw}"></div>
<div class="page" id="p3"><div class="pill">עברית</div><div class="flow" id="f3"></div><div class="rule"></div><div class="folio" style="left:9.9mm">3</div></div>
<div class="page" id="p4"><div class="pill">עברית</div><div class="flow" id="f4"></div><div class="rule"></div><div class="folio" style="right:9.9mm">4</div></div>
<div id="src" style="display:none">{body}</div>
<script>
// flow paragraphs: fill page 3 until it overflows, rest to page 4
const src=[...document.getElementById('src').children], f3=document.getElementById('f3'), f4=document.getElementById('f4');
let tgt=f3;
for (const p of src) {{ tgt.appendChild(p); if (tgt===f3 && f3.scrollWidth>f3.clientWidth+1) {{ tgt=f4; f4.appendChild(p); }} }}
document.title = (f4.scrollWidth>f4.clientWidth+1) ? 'OVERFLOW' : 'OK';
</script></body></html>"""
open("preview.html","w").write(doc)
