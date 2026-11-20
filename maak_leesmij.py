# DraveMaatje - "Lees mij eerst" (PDF, grote letters, simpele woorden). Voor ouderen.
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
import os
HERE = os.path.dirname(os.path.abspath(__file__))
t = ParagraphStyle('t', fontName='Helvetica-Bold', fontSize=34, leading=42, textColor='#2c8f7c', spaceAfter=12)
h = ParagraphStyle('h', fontName='Helvetica-Bold', fontSize=24, leading=30, textColor='#4a3d66', spaceBefore=18, spaceAfter=8)
b = ParagraphStyle('b', fontName='Helvetica', fontSize=20, leading=28, spaceAfter=10)
L = []
ic = os.path.join(HERE, 'assets', 'icon_256.png')
if os.path.exists(ic):
    L.append(Image(ic, width=3.2 * cm, height=3.2 * cm, hAlign='LEFT'))
L += [Paragraph('Lees mij eerst', t),
      Paragraph('Hallo! Dit is <b>DraveMaatje</b>. Het Maatje helpt u met uw computer. In gewone taal. Het leest alles hardop voor.', b)]


def blok(kop, regels):
    L.append(Paragraph(kop, h))
    for x in regels:
        L.append(Paragraph(x, b))


blok('1. Het Maatje starten', [
    'Dubbelklik op <b>DraveMaatje.exe</b>.',
    'Tip: vraag iemand om een <b>snelkoppeling</b> op uw bureaublad te zetten. Dan vindt u het Maatje altijd terug.'])
blok('2. Ziet u een blauw venster van Windows?', [
    'Soms zegt Windows: <i>"Windows heeft uw pc beschermd"</i>. Dat is normaal bij nieuwe gratis programma&#39;s.',
    'Klik dan op <b>Meer informatie</b>. Klik daarna op <b>Toch uitvoeren</b>. Dit hoeft maar &eacute;&eacute;n keer.'])
blok('3. Wat kan het Maatje?', [
    '<b>Kijk mijn pc na</b> (de grote groene knop): het Maatje vertelt hoe het met uw pc gaat.',
    '<b>Help me met een instelling</b> (blauw): bijvoorbeeld een grotere muispijl of het geluid harder.',
    '<b>Pc-paspoort</b> (paars): voor als uw pc naar de reparateur gaat.',
    '<b>Bescherm mij</b> (oranje): is dit bericht echt? Is deze website echt? Kijkt er iemand mee?'])
blok('4. Het Maatje is veilig', [
    'Het Maatje verandert <b>nooit</b> iets zonder het eerst te vragen. U drukt zelf op <b>JA</b> of <b>NEE</b>.',
    'Spijt? Druk op <b>Terugzetten zoals het was</b>.',
    'Opruimen gaat naar de <b>prullenbak</b>. U kunt het altijd terughalen.',
    'Het Maatje komt niet aan uw foto&#39;s, documenten of wachtwoorden. Alles blijft op uw eigen pc. Er gaat niets naar internet.'])
blok('5. Handige knoppen onderaan', [
    '<b>Lees nog eens voor</b>: het Maatje zegt het nog een keer.',
    '<b>Voorlezen AAN/UIT</b>: stem aan of uit. De toets <b>Esc</b> maakt het Maatje meteen stil.',
    '<b>Tekst groter</b> en <b>Tekst kleiner</b>: zo leest u het makkelijk.'])
blok('6. Gouden regel', [
    'Belt iemand op over een virus, of vraagt iemand uw pincode? <b>Ophangen.</b> Een bank of Microsoft doet dat nooit.'])
blok('Vragen?', [
    'In de map staat ook de <b>snelgids</b> met plaatjes, en een <b>uitlegfilmpje</b>.',
    'Mail ons: <b>service@dravenlock.nl</b>',
    'Het Maatje is gratis. Wilt u ons steunen? <b>paypal.me/roger076</b>. Dank u wel!',
    '<i>Dravenlock - Roger en Claudio</i>'])
SimpleDocTemplate(os.path.join(HERE, 'Lees_mij_eerst.pdf'), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                  topMargin=1.8 * cm, bottomMargin=1.8 * cm, title='DraveMaatje - Lees mij eerst').build(L)
print('KLAAR')
