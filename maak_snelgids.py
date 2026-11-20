# DraveMaatje - snelgids (PDF)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
import os
HERE = os.path.dirname(os.path.abspath(__file__))
t = ParagraphStyle('t', fontName='Helvetica-Bold', fontSize=26, leading=32, textColor='#2c8f7c', spaceAfter=8)
h = ParagraphStyle('h', fontName='Helvetica-Bold', fontSize=18, leading=24, textColor='#4a3d66', spaceBefore=14, spaceAfter=6)
b = ParagraphStyle('b', fontName='Helvetica', fontSize=15, leading=21, spaceAfter=6)
s = ParagraphStyle('s', fontName='Helvetica', fontSize=12, leading=16, textColor='#555555')
L = []
ic = os.path.join(HERE, 'assets', 'icon_256.png')
if os.path.exists(ic):
    L.append(Image(ic, width=2.6 * cm, height=2.6 * cm, hAlign='LEFT'))
L += [Paragraph('DraveMaatje - snelgids', t),
      Paragraph('Versie 0.6. Je maatje voor de pc. Voor ouderen en iedereen die geen zin heeft in pc-gedoe. Het Maatje kijkt je pc na, helpt met instellingen en beschermt je tegen oplichters. In gewone taal, en het leest alles hardop voor.', b)]


def blok(kop, regels, plaatje=None):
    samen = [Paragraph(kop, h)] if kop else [Spacer(1, 10)]          # kop + plaatje + eerste regel blijven bij elkaar
    if plaatje and os.path.exists(os.path.join(HERE, 'gids', plaatje)):
        samen += [Image(os.path.join(HERE, 'gids', plaatje), width=16.5 * cm, height=16.5 * cm * 1125 / 1625), Spacer(1, 6)]
    rest = [Paragraph('&bull; ' + x, b) for x in regels]
    L.append(KeepTogether(samen + rest[:1]))
    L.extend(rest[1:])


blok('Starten', [
    'Dubbelklik op <b>DraveMaatje.exe</b>. Het Maatje zegt hallo en legt uit wat het doet.',
    'Zegt Windows <i>"Windows heeft uw pc beschermd"</i>? Klik op <b>Meer informatie</b> en dan op <b>Toch uitvoeren</b>. Dat hoeft maar een keer.'])
blok('1. Kijk mijn pc na (de grote groene knop)', [
    'Het Maatje kijkt naar je schijven, het werkgeheugen, je virusscanner, je firewall, Windows Update, de programma&#39;s die meestarten en de rommel.',
    'Achter elk punt staat een kleur: <b>Goed</b> (groen), <b>Let op</b> (geel) en <b>Aandacht</b> (rood). De belangrijkste staan bovenaan.',
    'Is er rommel? Dan verschijnt <b>Ruim de rommel op</b>. Het Maatje vraagt het eerst, met <b>JA</b> en <b>NEE</b>. Alles gaat naar de <b>prullenbak</b>, dus je kunt het altijd terughalen.',
    'Het Maatje komt nooit aan je documenten, foto&#39;s of persoonlijke mappen.'], 'gids_kijk.png')
blok('2. Help me met een instelling (blauw)', [
    'Microsoft verstopt veel instellingen diep. Typ in gewone woorden wat je wilt, bijvoorbeeld <b>muis groter</b>, <b>ik hoor niets</b> of <b>wifi doet het niet</b>, en druk op <b>Zoek</b>. Of druk op een van de <b>20 klusjes</b>.'], 'gids_hulp.png')
blok('', [
    'Het Maatje vertelt eerst hoe het nu is. Dan kun je kiezen.',
    '<b>Het Maatje doet het voor je</b> (pas na JA): geluid, muispijl, vergrootglas, voorleesstem, donker of licht scherm, dubbelklikken, printer, programma&#39;s die meestarten en updates.',
    '<b>Terugzetten zoals het was</b>: vind je het niks? Het Maatje zet het terug.',
    '<b>Laat me zien waar het staat</b>: het Maatje opent de goede Windows-pagina en vertelt stap voor stap wat je moet doen.',
    'Je beveiliging (virusscanner, firewall) verandert het Maatje nooit zelf.'], 'gids_klus.png')
blok('3. Pc-paspoort (paars) - voor de reparateur', [
    'Gaat je pc naar de reparateur? Druk eerst op <b>Maak een paspoort</b>. Het Maatje schrijft de serienummers van de onderdelen op.',
    'Krijg je de pc terug? Druk op <b>Vergelijk met nu</b>. Dan zie je zwart op wit of je je <b>eigen</b> pc terugkrijgt: <b>Zelfde</b> (groen), <b>Zelfde soort</b> (geel) of <b>ANDERS</b> (rood).',
    'Het belangrijkste bewijs is het <b>moederbord</b>: dat is het hart van de pc.',
    'Zet een kopie van het paspoort op een usb-stick of print het uit (knop <b>Open de map met paspoorten</b>).'], 'gids_pas.png')
blok('4. Bescherm mij (oranje) - tegen oplichters', [
    '<b>Kijkt er iemand mee?</b> Het Maatje zoekt programma&#39;s waarmee iemand op afstand in je pc kan. Draait er nu zo&#39;n programma? Dan kun je het met <b>Stop het meekijken NU</b> uitzetten (eerst JA).',
    '<b>Is dit bericht echt?</b> Plak een mail, sms of WhatsApp en druk op <b>Controleer</b>. Het Maatje zegt <b>groen</b> (niets verdachts), <b>geel</b> (let op) of <b>rood</b> (gevaarlijk), en laat bij elke reden zien wat het zag.',
    '<b>Is deze website echt?</b> Plak een websiteadres. Het Maatje herkent nep-namen, zoals <i>rabobank-veilig-inloggen.nl</i>.',
    '<b>Gouden regels</b>: tien regels tegen oplichters, voorgelezen.',
    'Het Maatje kan het nooit 100% zeker weten. Twijfel je? Bel de afzender zelf, via een nummer dat je zelf opzoekt.'], 'gids_bes.png')
blok('Zo stel je het in', [
    '<b>Lees nog eens voor</b> - het Maatje zegt het nog een keer. De toets <b>Esc</b> maakt het meteen stil.',
    '<b>Voorlezen: AAN / UIT</b> - liever alleen lezen? Zet het uit.',
    '<b>Tekst groter</b> en <b>Tekst kleiner</b> - het Maatje onthoudt het.',
    '<b>Info</b> (of F1) - wie we zijn, en een knop om ons te steunen.'])
blok('Veilig', ['Het Maatje verandert nooit iets zonder het te vragen. Jij drukt zelf op JA.',
                'Alles blijft op je eigen pc. Er gaat niets naar internet.',
                'Wat het Maatje doet, staat in <b>handen_logboek.txt</b>.'])
L.append(Spacer(1, 12))
L.append(Paragraph('Dravenlock (Roger &amp; Claudio) - gratis, steun via paypal.me/roger076 - service@dravenlock.nl', s))
SimpleDocTemplate(os.path.join(HERE, 'DraveMaatje_snelgids.pdf'), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                  topMargin=1.6 * cm, bottomMargin=1.6 * cm, title='DraveMaatje snelgids', author='Dravenlock').build(L)
print('snelgids klaar')
