# Hebrew text blocks for the Stanley laser-levels catalog sample.
# Coordinates are PDF points from the top-left of each page, taken from the
# original Italian text positions (pdftotext -bbox-layout).
# Block fields:
#   box    (x1, y1, x2, y2)  area the Italian text occupied
#   it     original Italian (for the review sheet)
#   he     Hebrew text; "\n" separates paragraphs
#   size   font size in pt; lead = leading in pt
#   weight Regular | Bold | Black
#   align  right | left | center
#   color  "auto" (sampled from the original) or hex; runs may override per word

PAGES = {
    1: dict(w=419.528, blocks=[
        dict(box=(31, 136, 250, 156), it="LIVELLE LASER", he="פלסי לייזר", size=18, weight="Bold", align="left"),
        dict(box=(32, 572, 200, 584), it="www.STANLEY.it", he="www.STANLEY.it", size=9.5, weight="Bold", align="left"),
    ]),
    2: dict(w=419.528, blocks=[
        dict(box=(30, 122, 405, 182), it="ALLINEAMENTO", he="יישור", size=58, lead=60, weight="Black", align="right"),
        dict(box=(78, 196, 398, 274), it="PERFETTO", he="מושלם", size=66, lead=70, weight="Black", align="center"),
    ]),
    3: dict(w=413.858, blocks=[
        dict(box=(36, 145, 362, 173), it="Le livelle STANLEY® sono perfette per livellamenti veloci e precisi. La nuova gamma è molto versatile e consente di lavorare in interni con risultati professionali.",
             he="פלסי ה-STANLEY® מושלמים לפילוס מהיר ומדויק. הסדרה החדשה רב-גונית במיוחד ומאפשרת עבודה בחללי פנים עם תוצאות מקצועיות.",
             size=9.5, lead=14.6, weight="Regular", align="right"),
        dict(box=(36, 193, 362, 268), it="Le livelle laser sono disponibili anche nella versione a raggio verde, molto più visibile. Design compatto ed ergonomico, rivestimento di protezione in gomma, meccanismo di bloccaggio del pendolo sono le principali caratteristiche. Il nuovo supporto multidirezionale STANLEY® QUICKLINK™ 2.0 consente il posizionamento praticamente ovunque, per qualsiasi necessità d’uso.",
             he="פלסי הלייזר זמינים גם בגרסה עם קרן ירוקה, הנראית הרבה יותר. עיצוב קומפקטי וארגונומי, ציפוי מגן מגומי ומנגנון נעילת מטוטלת הם המאפיינים העיקריים. המעמד הרב-כיווני החדש STANLEY® QUICKLINK™ 2.0 מאפשר הצבה כמעט בכל מקום, לכל צורך.",
             size=9.5, lead=14.6, weight="Regular", align="right"),
    ]),
    4: dict(w=411.024, blocks=[
        dict(box=(36, 32, 380, 60), it="LIVELLE A RAGGIO VERDE", he="פלסים עם קרן ירוקה", size=22, weight="Bold", align="right"),
        dict(box=(131, 104, 368, 158), it="RAGGIO", he="קרן", size=46, lead=50, weight="Black", align="right"),
        dict(box=(131, 150, 368, 236), it="VOLTE", he="פי", size=78, lead=84, weight="Black", align="right"),
        dict(box=(43, 146, 128, 290), it="4", he="4", size=135, lead=140, weight="Black", align="center"),
        dict(box=(131, 222, 368, 275), it="PIÙ", he="יותר", size=46, lead=50, weight="Black", align="right"),
        dict(box=(39, 275, 372, 349), it="LUMINOSO", he="בהירה", size=64, lead=70, weight="Black", align="center"),
        dict(box=(376, 275, 393, 306), it="*", he="*", size=31, weight="Black", align="center"),
        dict(box=(36, 382, 300, 412), it="Le livelle laser STANLEY® a raggio verde offrono una visibilità nettamente superiore rispetto al raggio rosso.",
             he="פלסי הלייזר של STANLEY® עם קרן ירוקה מעניקים נראות טובה בהרבה בהשוואה לקרן אדומה.",
             size=10.5, lead=13.5, weight="Regular", align="right"),
        dict(box=(36, 418, 300, 447), it="Nate per utilizzo professionale, sono estremamente visibili, veloci e semplici all’uso.",
             he="הם פותחו לשימוש מקצועי – בולטים לעין במיוחד, מהירים ופשוטים לשימוש.",
             size=10.5, lead=13.5, weight="Regular", align="right"),
        dict(box=(36, 541, 200, 551), it="*4 volte più visibile rispetto al raggio rosso", he="*נראות גבוהה פי 4 בהשוואה לקרן אדומה",
             size=6.5, weight="Regular", align="left", color="#ffffff"),
    ]),
    6: dict(w=411.024, blocks=[
        dict(box=(21, 9, 90, 17), it="www.STANLEY.it", he="www.STANLEY.it", size=6, weight="Bold", align="left"),
        dict(box=(42, 39, 370, 50), it="LIVELLA LASER STANLEY® CUBIX™ A RAGGIO ROSSO E VERDE", he="פלס לייזר STANLEY® CUBIX™ עם קרן אדומה וירוקה",
             size=8, weight="Bold", align="right"),
        dict(box=(162, 57, 356, 185), it="• Portata: 12 metri (raggio rosso) / 16 metri (raggio verde)\n• Precisione della linea: ± 6 mm a 10 metri\n• Autolivellante, traccia una croce con angoli a 90°\n• Il raggio verde garantisce grande visibilità e portata maggiorata\n• Utilizzata capovolta, consente di creare una linea sul soffitto\n• Campo di autolivellamento: ± 4°\n• Indice di protezione da pioggia e polvere IP50\n• Funzione blocco del pendolo - consente il trasporto in sicurezza\n• Attacco 1/4”\n• Indicata per uso in interni\n• Utilizza 2 batterie AA (incluse)\n• La confezione include: nuovo supporto multidirezionale QuickLink™, fodero, manuale.",
             he="• טווח: 12 מטר (קרן אדומה) / 16 מטר (קרן ירוקה)\n• דיוק הקו: ‎±6 מ\"מ ל-10 מטר\n• פילוס עצמי, מקרין צלב בזוויות של 90°\n• הקרן הירוקה מבטיחה נראות גבוהה וטווח מוגדל\n• במצב הפוך מאפשר להקרין קו על התקרה\n• טווח פילוס עצמי: ‎±4°\n• דרגת הגנה מפני גשם ואבק IP50\n• נעילת מטוטלת – לנשיאה בטוחה\n• תבריג חיבור \"1/4\n• מיועד לשימוש בתוך מבנים\n• פועל על 2 סוללות AA (כלולות)\n• באריזה: מעמד רב-כיווני חדש QuickLink™, נרתיק ומדריך.",
             size=6.7, lead=9.6, weight="Regular", align="right", color="#231f20"),
        # product table 1 (red)
        dict(box=(240, 202, 344, 210), it="Descrizione", he="תיאור", size=4.7, weight="Bold", align="center"),
        dict(box=(166, 212, 207, 220), it="STHT77498-1", he="STHT77498-1", size=4.7, weight="Bold", align="center"),
        dict(box=(212, 212, 346, 220), it="Livella laser STANLEY® Cubix™ a raggio rosso", he="פלס לייזר STANLEY® Cubix™ קרן אדומה", size=4.9, weight="Regular", align="center", color="#231f20"),
        dict(box=(206, 237, 257, 251), it="RAGGIO ROSSO", he=[("קרן ", "#1a1a1a", "Regular"), ("אדומה", "#ed1c24", "Black")], size=9.5, weight="Regular", align="left"),
        dict(box=(256, 231, 286, 247), it="12 m", he="12 m", size=11.5, nowrap=True, ltr=True, weight="Black", align="center"),
        dict(box=(259, 251, 284, 257), it="±0.6mm/m", he="±0.6mm/m", size=4.3, weight="Regular", align="center", color="#ffffff"),
        dict(box=(349, 250, 371, 255), it="Uso in interni", he="שימוש פנימי", size=2.9, weight="Bold", align="center"),
        # product table 2 (green)
        dict(box=(240, 268, 344, 276), it="Descrizione", he="תיאור", size=4.7, weight="Bold", align="center"),
        dict(box=(166, 278, 207, 286), it="STHT77499-1", he="STHT77499-1", size=4.7, weight="Bold", align="center"),
        dict(box=(212, 278, 346, 286), it="Livella laser STANLEY® Cubix™ a raggio verde", he="פלס לייזר STANLEY® Cubix™ קרן ירוקה", size=4.9, weight="Regular", align="center", color="#231f20"),
        dict(box=(206, 302, 257, 317), it="RAGGIO VERDE", he=[("קרן ", "#1a1a1a", "Regular"), ("ירוקה", "#0aa94d", "Black")], size=9.5, weight="Regular", align="left"),
        dict(box=(256, 297, 286, 313), it="16 m", he="16 m", size=11.5, nowrap=True, ltr=True, weight="Black", align="center"),
        dict(box=(259, 317, 284, 323), it="±0.6mm/m", he="±0.6mm/m", size=4.3, weight="Regular", align="center", color="#ffffff"),
        dict(box=(349, 316, 371, 321), it="Uso in interni", he="שימוש פנימי", size=2.9, weight="Bold", align="center"),
        # laser class labels (codes stay the same)
        dict(box=(54, 238, 86, 245), it="STHT77498-1", he="STHT77498-1", size=5, weight="Bold", align="left"),
        dict(box=(55, 268, 100, 278), nowrap=True, it="1.5mW @ 630-680nm / IEC 60825-1: 2014", he="1.5mW @ 630-680nm\nIEC 60825-1: 2014", size=3.8, lead=4.4, weight="Bold", align="left", ltr=True),
        dict(box=(54, 283, 86, 290), it="STHT77499-1", he="STHT77499-1", size=5, weight="Bold", align="left"),
        dict(box=(55, 313, 100, 323), nowrap=True, it="1.5mW @ 510-530nm / IEC 60825-1: 2014", he="1.5mW @ 510-530nm\nIEC 60825-1: 2014", size=3.8, lead=4.4, weight="Bold", align="left", ltr=True),
    ]),
}
