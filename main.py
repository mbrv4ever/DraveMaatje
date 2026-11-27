# -*- coding: utf-8 -*-
# DraveMaatje 0.6 - je maatje voor de pc. Voor ouderen en iedereen die geen zin heeft in pc-gedoe.
# Een grote knop: "Kijk mijn pc na". Het Maatje vertelt (en leest voor) hoe het met je pc gaat,
# in gewone taal. Opruimen ALLEEN als jij op JA drukt (naar de prullenbak, terug te halen).
# Gebruikt de gedeelde handen (DraveHanden), net als Drave Visual Buddy.
# 0.2: "Help me met een instelling": zoeken in gewone taal, de Windows-pagina openen met uitleg,
#      of (na JA) het voor je doen, met Terugzetten. Eerste klusje: muispijl groter.
# 0.6: de schermen Help en Bescherm komen uit de gedeelde handen (handen_qt): een keer verbeteren = overal beter.
#      Nieuwe, eerlijkere controle van berichten (bescherm 0.3: "Ik zag: ...").
# 0.5: alle instellingen: 9 klusjes die het Maatje zelf kan (na JA, met Terugzetten) en 11 met uitleg.
# 0.4: Bescherm mij: meekijk-alarm, is dit bericht echt?, is deze website echt?, gouden regels.
# 0.3: Pc-paspoort: voor de reparateur de serienummers vastleggen, daarna vergelijken (bewijs: krijg je je EIGEN pc terug?).
# Dravenlock (Roger & Claudio), 20-11-2026. Donationware: paypal.me/roger076
import os, sys, time, threading, locale, traceback, webbrowser, json

HERE = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)
VERSIE = "0.7"
try:
    NL = (locale.getlocale()[0] or "nl").lower().startswith(("nl", "dutch"))
except Exception:
    NL = True

TX = {
    "titel": ("DraveMaatje", "DraveMaatje"),
    "hoi": ("Hoi! Ik ben je Maatje. Ik help je met je pc.", "Hi! I'm your Maatje. I help you with your pc."),
    "uitleg": ("Druk op de grote groene knop. Dan kijk ik je pc na en vertel ik hoe het gaat. Ik verander niets zonder het te vragen.",
               "Press the big green button. I'll check your pc and tell you how it's doing. I never change anything without asking."),
    "kijk": ("Kijk mijn pc na", "Check my pc"),
    "bezig": ("Ik kijk je pc na. Een momentje...", "I'm checking your pc. One moment..."),
    "ruim": ("Ruim de rommel op", "Clean up the junk"),
    "nog": ("Lees nog eens voor", "Read it again"),
    "stem_aan": ("Voorlezen: AAN", "Read aloud: ON"), "stem_uit": ("Voorlezen: UIT", "Read aloud: OFF"),
    "groter": ("Tekst groter", "Bigger text"), "kleiner": ("Tekst kleiner", "Smaller text"),
    "info": ("Info", "Info"),
    "ja": ("JA", "YES"), "nee": ("NEE", "NO"),
    "vraag": ("Zal ik %s aan rommel opruimen? Het gaat naar de prullenbak, dus je kunt het altijd terughalen.",
              "Shall I clean up %s of junk? It goes to the recycle bin, so you can always get it back."),
    "niets": ("Er is bijna geen rommel. Opruimen is niet nodig.", "There is hardly any junk. No need to clean up."),
    "nee_ok": ("Goed, ik doe niets.", "Okay, I won't do anything."),
    "ruimt": ("Ik ruim op. Een momentje...", "Cleaning up. One moment..."),
    "eerst": ("Druk eerst op Kijk mijn pc na.", "First press Check my pc."),
    "fout": ("Dat lukte niet: %s", "That didn't work: %s"),
    "status": ({"goed": "✔  Goed", "let_op": "!  Let op", "slecht": "✖  Aandacht", "onbekend": "?  Weet ik niet"},
               {"goed": "✔  Good", "let_op": "!  Note", "slecht": "✖  Attention", "onbekend": "?  Unknown"}),
    "info_tekst": ("DraveMaatje %s - testversie.\nDravenlock (Roger & Claudio).\n\nIk kijk je pc na en leg het uit in gewone taal.\n"
                   "Ik ruim alleen op als jij op JA drukt, en dan gaat het naar de prullenbak.\n"
                   "Ik kom nooit aan je documenten, foto's of persoonlijke mappen.\nAlles blijft op je eigen pc.\n\n"
                   "Steun ons: paypal.me/roger076\nVragen: service@dravenlock.nl",
                   "DraveMaatje %s - test version.\nDravenlock (Roger & Claudio).\n\nI check your pc and explain it in plain words.\n"
                   "I only clean up when you press YES, and then it goes to the recycle bin.\n"
                   "I never touch your documents, photos or personal folders.\nEverything stays on your pc.\n\n"
                   "Support us: paypal.me/roger076\nQuestions: service@dravenlock.nl"),
    "help": ("Help me met een instelling", "Help me with a setting"),
    "help_kop": ("Waar kan ik je mee helpen?", "What can I help you with?"),
    "help_uitleg": ("Typ wat je wilt, of kies hieronder een klusje.", "Type what you want, or pick a job below."),
    "zoek_hint": ("Bijvoorbeeld: muis groter", "For example: bigger mouse"),
    "zoek": ("Zoek", "Search"), "terug_thuis": ("◀  Terug", "◀  Back"),
    "niet_gevonden": ("Dat ken ik nog niet. Kies hieronder een klusje, of probeer het met andere woorden.",
                      "I don't know that yet. Pick a job below, or try other words."),
    "laat_zien": ("Laat me zien waar het staat", "Show me where it is"),
    "terugzetten": ("Terugzetten zoals het was", "Undo, back as it was"),
    "terug_vraag": ("Zal ik het terugzetten zoals het was, voordat ik iets veranderde?", "Shall I put it back as it was before I changed anything?"),
    "alle": ("◀  Alle klusjes", "◀  All jobs"),
    "zelf_doen": ("Dit doe je zelf. Druk op Laat me zien waar het staat: dan open ik de goede pagina en vertel ik wat je moet doen.",
                  "You do this yourself. Press Show me where it is: I open the right page and tell you what to do."),
    "even_kijken": ("Even kijken...", "Let me look..."),
    "pas": ("Pc-paspoort (voor de reparateur)", "Pc passport (for the repair shop)"),
    "pas_kop": ("Pc-paspoort", "Pc passport"),
    "pas_uitleg": ("Gaat je pc naar de reparateur? Maak dan eerst een paspoort. Ik schrijf de serienummers van de onderdelen op. "
                   "Krijg je hem terug? Druk dan op Vergelijk met nu. Zo zie je zwart op wit of je je eigen pc terugkrijgt.",
                   "Is your pc going to the repair shop? Make a passport first. I write down the serial numbers of the parts. "
                   "Got it back? Press Compare with now. Then you see in black and white if you got your own pc back."),
    "pas_maak": ("Maak een paspoort", "Make a passport"), "pas_verg": ("Vergelijk met nu", "Compare with now"),
    "pas_map": ("Open de map met paspoorten", "Open the passport folder"),
    "pas_geen": ("Je hebt nog geen paspoort. Druk op Maak een paspoort.", "You don't have a passport yet. Press Make a passport."),
    "pas_laatste": ("Laatste paspoort: %s. Je hebt er %d.", "Latest passport: %s. You have %d."),
    "pas_bezig": ("Ik lees de onderdelen van je pc. Een momentje...", "Reading your pc's parts. One moment..."),
    "pas_st": ({"zelfde": "✔  Zelfde", "onzeker": "~  Zelfde soort", "anders": "✖  ANDERS"},
               {"zelfde": "✔  Same", "onzeker": "~  Same type", "anders": "✖  DIFFERENT"}),
    "bes": ("Bescherm mij", "Protect me"),
    "bes_kop": ("Bescherm mij tegen oplichters", "Protect me against scammers"),
    "bes_uitleg": ("Kies wat je wilt laten controleren. Alles blijft op je eigen pc.", "Choose what you want checked. Everything stays on your pc."),
    "bes_mee": ("Kijkt er iemand mee?", "Is someone watching?"), "bes_ber": ("Is dit bericht echt?", "Is this message real?"),
    "bes_link": ("Is deze website echt?", "Is this website real?"), "bes_regels": ("Gouden regels", "Golden rules"),
    "bes_ber_uitleg": ("Plak hieronder de mail, sms of WhatsApp (rechtermuisknop, Plakken) en druk op Controleer.",
                       "Paste the mail, text or WhatsApp below (right-click, Paste) and press Check."),
    "bes_link_uitleg": ("Plak hieronder het websiteadres (rechtermuisknop, Plakken) en druk op Controleer.",
                        "Paste the web address below (right-click, Paste) and press Check."),
    "bes_check": ("Controleer", "Check"), "bes_stop": ("Stop het meekijken NU", "Stop the watching NOW"),
    "bes_stop_vraag": ("Zal ik het meekijk-programma nu uitzetten? Dan kan degene aan de andere kant niet meer in je pc.",
                       "Shall I turn off the remote program now? Then the person on the other end can't get into your pc anymore."),
    "bes_bezig": ("Ik kijk even. Een momentje...", "Checking. One moment..."),
    "bes_regels_kop": ("De gouden regels tegen oplichters:", "The golden rules against scammers:"),
    "van": ("Is mijn pc nog van mij?", "Is my pc still mine?"),
    "van_bezig": ("Ik kijk of Windows stiekem iets heeft aangezet. Een momentje...",
                  "I'm checking whether Windows quietly switched something on. One moment..."),
    "van_weer": ("Let op! Windows heeft iets weer aangezet: %s. Hieronder staat hoe je het uitzet.",
                 "Careful! Windows switched something back on: %s. Below is how to switch it off."),
    "van_eerst": ("Ik heb gekeken en onthouden hoe het nu staat. Volgende keer zie ik of Windows iets verandert.",
                  "I checked and remembered how things are now. Next time I'll see if Windows changes something."),
    "van_rust": ("Sinds de vorige keer heeft Windows niets teruggezet.", "Since last time Windows didn't switch anything back."),
    "van_aan": ("Er staan nog %d dingen aan die met Microsoft praten of reclame tonen.",
                "%d things are still on that talk to Microsoft or show ads."),
    "van_alles": ("Alles staat netjes uit. Je pc is van jou!", "Everything is switched off. Your pc is yours!"),
    "van_goed": ("Deze %d dingen staan netjes uit", "These %d things are switched off"),
    "doneer": ("Doneren via PayPal", "Donate via PayPal"), "sluit": ("Sluiten", "Close"),
}


def T(k):
    return TX[k][0 if NL else 1]


INST_JSON = os.path.join(HERE, "maatje_instellingen.json")


def lees_inst():
    try:
        with open(INST_JSON, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def schrijf_inst(d):
    try:
        with open(INST_JSON, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
    except Exception:
        pass


def main():
    sys.path.insert(0, HERE)
    import handen
    import klusjes                                              # 0.2
    import paspoort                                             # 0.3
    import bescherm                                             # 0.4
    import wachter                                              # 0.7: is mijn pc nog van mij?
    from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer
    from PyQt6.QtGui import QFont, QIcon, QShortcut, QKeySequence
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                                 QFrame, QScrollArea, QDialog, QStackedWidget, QLineEdit, QGridLayout, QPlainTextEdit,
                                 QSizePolicy)
    from handen_qt import BeschermScherm, KlusjesScherm          # 0.6: gedeelde schermen

    app = QApplication(sys.argv)
    inst = lees_inst()
    taal = "nl" if NL else "en"
    st = {"uitslag": None, "bezig": False, "vraag": False, "zinnen": [], "stem_aan": inst.get("voorlezen", True),
          "maat": int(inst.get("tekstmaat", 18))}

    # ---------- stem (Leon). Lukt dat niet, dan werkt het Maatje gewoon zonder stem.
    stem = None
    try:
        from stem import Stem
        stem = Stem(stem="Leon", taal=taal)
        stem.snelheid = float(inst.get("tempo", 0.85))
        stem.warm_op()
    except Exception:
        stem = None
    if os.environ.get("MAATJE_STIL") and stem:                      # alleen voor de proef: geen geluid
        stem.zeg = lambda *a, **k: None

    def spreek(zinnen):
        st["zinnen"] = list(zinnen)
        if stem and st["stem_aan"]:
            stem.stil()
            for z in zinnen:
                stem.zeg(z)

    class Sein(QObject):
        uitslag = pyqtSignal(object)
    sein = Sein()

    # ---------- venster
    w = QMainWindow()
    w.setWindowTitle(T("titel"))
    try:
        w.setWindowIcon(QIcon(os.path.join(HERE, "assets", "icon_256.png")))
    except Exception:
        pass
    w.resize(1200, 900)
    w.setStyleSheet("""
        QMainWindow, QWidget { background:#16131f; color:#f0f0f5; }
        QPushButton { background:#221c34; border:3px solid #b59cff; border-radius:14px; padding:8px 16px; color:white; }
        QPushButton:hover { background:#4a3d66; }
        QPushButton[soort="kijk"] { background:#287846; border-color:#78e696; }
        QPushButton[soort="ruim"] { background:#20504a; border-color:#5ee0c8; }
        QPushButton[soort="ja"] { background:#287846; border-color:#78e696; }
        QPushButton[soort="nee"] { background:#822832; border-color:#ff7878; }
        QPushButton[soort="help"] { background:#284670; border-color:#6edcff; }
        QPushButton[soort="klus"] { background:#2a2440; border-color:#6edcff; }
        QPushButton[soort="pas"] { background:#5a3a70; border-color:#d29cff; }
        QPushButton[soort="van"] { background:#1f5a5a; border-color:#5ee0c8; }
QPushButton[soort="bes"] { background:#7a3a20; border-color:#ffa070; }
        QPlainTextEdit { background:#0f0d17; border:3px solid #ffa070; border-radius:14px; padding:8px; color:white; }
        QLineEdit { background:#0f0d17; border:3px solid #6edcff; border-radius:14px; padding:6px 14px; color:white; }
        QPushButton:disabled { background:#1b1728; border-color:#3a3350; color:#6a6680; }
        QFrame#vraag { background:#2a2440; border:4px solid #ffdc5a; border-radius:16px; }
        QFrame#rij { background:#1b1728; border:2px solid #2e2645; border-radius:14px; }
        QScrollArea { border:none; }
        QLabel { background:transparent; }
    """)

    def F(extra=0, vet=True):
        return QFont("Segoe UI", max(10, st["maat"] + extra), QFont.Weight.Bold if vet else QFont.Weight.Normal)

    def knop(tekst, soort=None, h=64):
        b = QPushButton(tekst); b.setMinimumHeight(h); b.setCursor(Qt.CursorShape.PointingHandCursor)
        if soort:
            b.setProperty("soort", soort)
        return b

    logo = QLabel()
    try:
        from PyQt6.QtGui import QPixmap
        logo.setPixmap(QPixmap(os.path.join(HERE, "assets", "icon_256.png")).scaled(
            96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    except Exception:
        pass
    hoi = QLabel(T("hoi")); hoi.setWordWrap(True); hoi.setStyleSheet("color:#5ee0c8;")
    uitleg = QLabel(T("uitleg")); uitleg.setWordWrap(True); uitleg.setStyleSheet("color:#d0d0e0;")
    b_kijk = knop(T("kijk"), "kijk", 110)
    b_help = knop(T("help"), "help", 80)                        # 0.2
    b_pas = knop(T("pas"), "pas", 80)                           # 0.3
    b_bes = knop(T("bes"), "bes", 80)                           # 0.4
    b_van = knop("🛡  " + T("van"), "van", 80)                    # 0.7
    sv = QLabel(""); sv.setWordWrap(True)
    vraag = QFrame(); vraag.setObjectName("vraag")
    vraag_lbl = QLabel(""); vraag_lbl.setWordWrap(True)
    b_ja, b_nee = knop(T("ja"), "ja", 100), knop(T("nee"), "nee", 100)
    vq = QVBoxLayout(vraag); vq.setContentsMargins(20, 16, 20, 16); vq.addWidget(vraag_lbl)
    vh = QHBoxLayout(); vh.setSpacing(28); vh.addWidget(b_ja); vh.addWidget(b_nee); vq.addLayout(vh)
    vraag.hide()
    lijst_w = QWidget(); lijst = QVBoxLayout(lijst_w); lijst.setSpacing(10); lijst.setContentsMargins(0, 0, 8, 0)
    scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(lijst_w)
    b_ruim = knop(T("ruim"), "ruim", 80)
    b_nog, b_stem = knop(T("nog")), knop("")
    b_kleiner, b_groter, b_info = knop(T("kleiner")), knop(T("groter")), knop(T("info"))

    kop = QHBoxLayout(); kop.setSpacing(18); kop.addWidget(logo)
    kt = QVBoxLayout(); kt.addWidget(hoi); kt.addWidget(uitleg); kop.addLayout(kt, 1)
    onder = QHBoxLayout(); onder.setSpacing(12)
    for x in (b_nog, b_stem, b_kleiner, b_groter, b_info):
        onder.addWidget(x)
    L = QVBoxLayout(); L.setContentsMargins(26, 20, 26, 20); L.setSpacing(14)
    rij2 = QHBoxLayout(); rij2.setSpacing(14); rij2.addWidget(b_help); rij2.addWidget(b_pas); rij2.addWidget(b_bes)
    L.addLayout(kop); L.addWidget(b_kijk); L.addLayout(rij2); L.addWidget(b_van); L.addWidget(sv); L.addWidget(vraag); L.addWidget(scroll, 1)
    L.addWidget(b_ruim); L.addLayout(onder)
    thuis = QWidget(); thuis.setLayout(L)

    # ---------- 0.2 / 0.6: scherm "Help me met een instelling" (gedeeld, uit handen_qt)
    help_scherm = KlusjesScherm(spreek, nl=NL, maat=st["maat"], terug=lambda: help_dicht())

    # ---------- 0.3: scherm Pc-paspoort
    p_kop = QLabel(T("pas_kop")); p_kop.setStyleSheet("color:#d29cff;")
    p_uitleg = QLabel(T("pas_uitleg")); p_uitleg.setWordWrap(True); p_uitleg.setStyleSheet("color:#d0d0e0;")
    b_p_terug = knop(T("terug_thuis"), None, 64)
    b_p_maak, b_p_verg, b_p_map = knop(T("pas_maak"), "kijk", 80), knop(T("pas_verg"), "help", 80), knop(T("pas_map"), None, 64)
    p_stand = QLabel(""); p_stand.setWordWrap(True)
    p_sv = QLabel(""); p_sv.setWordWrap(True)
    p_lijst_w = QWidget(); p_lijst = QVBoxLayout(p_lijst_w); p_lijst.setSpacing(10); p_lijst.setContentsMargins(0, 0, 8, 0)
    p_scroll = QScrollArea(); p_scroll.setWidgetResizable(True); p_scroll.setWidget(p_lijst_w)
    PL = QVBoxLayout(); PL.setContentsMargins(26, 20, 26, 20); PL.setSpacing(14)
    pk_ = QHBoxLayout(); pk_.addWidget(p_kop, 1); pk_.addWidget(b_p_terug); PL.addLayout(pk_)
    PL.addWidget(p_uitleg)
    pr_ = QHBoxLayout(); pr_.setSpacing(14); pr_.addWidget(b_p_maak); pr_.addWidget(b_p_verg); PL.addLayout(pr_)
    PL.addWidget(p_stand); PL.addWidget(p_sv); PL.addWidget(p_scroll, 1); PL.addWidget(b_p_map)
    pas_scherm = QWidget(); pas_scherm.setLayout(PL)

    # ---------- 0.4 / 0.6: scherm Bescherm mij (gedeeld, uit handen_qt)
    bes_scherm = BeschermScherm(spreek, nl=NL, maat=st["maat"], terug=lambda: help_dicht())

    schermen = QStackedWidget(); schermen.addWidget(thuis); schermen.addWidget(help_scherm); schermen.addWidget(pas_scherm)
    schermen.addWidget(bes_scherm)
    w.setCentralWidget(schermen)
    b_ruim.hide()

    KLEUR = {"goed": "#78e696", "let_op": "#ffdc5a", "slecht": "#ff7878", "onbekend": "#9696aa"}

    def zet_letters():
        hoi.setFont(F(8)); uitleg.setFont(F(0, False)); b_kijk.setFont(F(12)); b_help.setFont(F(6)); b_pas.setFont(F(6)); sv.setFont(F(4))
        p_kop.setFont(F(8)); p_uitleg.setFont(F(0, False)); b_p_terug.setFont(F(0)); p_stand.setFont(F(2)); p_sv.setFont(F(4))
        for x in (b_p_maak, b_p_verg):
            x.setFont(F(4))
        b_p_map.setFont(F(0))
        b_bes.setFont(F(6)); b_van.setFont(F(6))
        help_scherm.zet_maat(st["maat"]); bes_scherm.zet_maat(st["maat"])          # 0.6
        vraag_lbl.setFont(F(4)); b_ja.setFont(F(10)); b_nee.setFont(F(10)); b_ruim.setFont(F(4))
        for x in (b_nog, b_stem, b_kleiner, b_groter, b_info):
            x.setFont(F(-2))
        if st["uitslag"] and "lijst" in st["uitslag"]:
            toon(st["uitslag"], voorlezen=False)

    def zet_stem_knop():
        b_stem.setText(T("stem_aan") if st["stem_aan"] else T("stem_uit"))

    def knoppen():
        vrij = not st["bezig"] and not st["vraag"]
        for b in (b_kijk, b_ruim, b_nog, b_van):
            b.setEnabled(vrij)

    def leeg_lijst():
        while lijst.count():
            it = lijst.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

    def rommel_bytes():
        for b in (st["uitslag"] or {}).get("lijst", []):
            if b["soort"] == "rommel":
                return b["extra"].get("bytes", 0)
        return 0

    # ---------- nakijken
    def kijk():
        if st["bezig"]:
            return
        st["bezig"] = True; vraag.hide(); st["vraag"] = False; knoppen()
        sv.setText(T("bezig")); sv.setStyleSheet("color:#ffdc5a;"); leeg_lijst(); b_ruim.hide()
        spreek([T("bezig")])

        def werk():
            try:
                s, l = handen.pc_nakijken(taal)
                sein.uitslag.emit({"sv": s, "lijst": l})
            except Exception as ex:
                sein.uitslag.emit({"sv": T("fout") % ex, "lijst": []})
        threading.Thread(target=werk, daemon=True).start()

    def toon(r, voorlezen=True):
        sv.setText(r["sv"]); sv.setStyleSheet("color:#f0f0f5;"); leeg_lijst()
        volgorde = {"slecht": 0, "let_op": 1, "onbekend": 2, "goed": 3}
        zinnen = [r["sv"]]
        for b in sorted(r["lijst"], key=lambda b: volgorde.get(b["status"], 9)):
            rij = QFrame(); rij.setObjectName("rij")
            hl = QHBoxLayout(rij); hl.setContentsMargins(16, 12, 16, 12); hl.setSpacing(18)
            stat = QLabel(TX["status"][0 if NL else 1].get(b["status"], "?")); stat.setFont(F(2))
            stat.setMinimumWidth(st["maat"] * 12); stat.setStyleSheet("color:%s;" % KLEUR.get(b["status"], "#fff"))
            tekst = "<b>%s</b><br>%s" % (b["titel"], b["uitleg"])
            if b.get("advies"):
                tekst += "<br><span style='color:#ffdc5a'>%s</span>" % b["advies"]
            tl = QLabel(tekst); tl.setWordWrap(True); tl.setFont(F(0, False))
            hl.addWidget(stat); hl.addWidget(tl, 1)
            lijst.addWidget(rij)
            zinnen.append(b["uitleg"] + ((" " + b["advies"]) if b.get("advies") else ""))
        lijst.addStretch(1)
        b_ruim.setVisible(rommel_bytes() >= 1024 * 1024)
        if voorlezen:
            spreek(zinnen)
        else:
            st["zinnen"] = zinnen

    def klaar(r):
        st["bezig"] = False; knoppen()
        if "uitleg" in r:                                           # uitslag van het opruimen
            sv.setText(r["uitleg"]); spreek([r["uitleg"]])
            QTimer.singleShot(2500, kijk)                           # daarna opnieuw kijken
            return
        st["uitslag"] = r
        toon(r)
    sein.uitslag.connect(klaar)

    # ---------- 0.7: is mijn pc nog van mij? (Wachter, alleen kijken)
    def mijn():
        if st["bezig"]:
            return
        st["bezig"] = True; vraag.hide(); st["vraag"] = False; knoppen()
        sv.setText(T("van_bezig")); sv.setStyleSheet("color:#ffdc5a;"); leeg_lijst(); b_ruim.hide()
        spreek([T("van_bezig")])

        def werk():
            try:
                kaart = os.path.join(HERE, "cache")
                priv, veranderd, eerste, _ = wachter.privacy_veranderd(kaart, taal)
                opstart = wachter.kijk_opstart_nieuw(kaart, taal)
                aan = [b for b in priv if b["status"] != "goed"]
                goed = [b for b in priv if b["status"] == "goed"]
                if veranderd:
                    zin = T("van_weer") % ", ".join(b["titel"] for b in veranderd)
                elif eerste:
                    zin = T("van_eerst")
                else:
                    zin = T("van_rust")
                n_aan = sum(1 for b in aan if b["status"] in ("let_op", "slecht"))
                zin += " " + (T("van_aan") % n_aan if n_aan else T("van_alles"))
                lijst_ = aan + opstart
                if goed:
                    lijst_.append(wachter.bevinding("privacy", "goed", T("van_goed") % len(goed),
                                                    ", ".join(b["titel"] for b in goed) + "."))
                sein.uitslag.emit({"sv": zin, "lijst": lijst_})
            except Exception as ex:
                sein.uitslag.emit({"sv": T("fout") % ex, "lijst": []})
        threading.Thread(target=werk, daemon=True).start()

    # ---------- opruimen: eerst vragen
    def vraag_ruim():
        if not st["uitslag"]:
            spreek([T("eerst")]); sv.setText(T("eerst")); return
        n = rommel_bytes()
        if n < 1024 * 1024:
            spreek([T("niets")]); sv.setText(T("niets")); return
        zin = T("vraag") % handen.mooi_getal(n)
        vraag_lbl.setText(zin); vraag.show(); st["vraag"] = True; knoppen()
        spreek([zin])

    def antwoord(ja):
        if not st["vraag"]:
            return
        vraag.hide(); st["vraag"] = False
        if not ja:
            knoppen(); spreek([T("nee_ok")]); sv.setText(T("nee_ok")); return
        st["bezig"] = True; knoppen(); sv.setText(T("ruimt")); spreek([T("ruimt")])

        def werk():                                                 # de gebruiker drukte zelf op JA
            try:
                r = handen.ruim_op(bevestigd=True, taal=taal)
            except Exception as ex:
                r = {"gedaan": False, "uitleg": T("fout") % ex}
            sein.uitslag.emit(r)
        threading.Thread(target=werk, daemon=True).start()

    # ---------- 0.2 / 0.6: help met een instelling
    def help_open():
        if stem:
            stem.stil()
        schermen.setCurrentIndex(1); help_scherm.open()

    def help_dicht():
        if stem:
            stem.stil()
        schermen.setCurrentIndex(0)

    b_help.clicked.connect(help_open)

    # ---------- 0.3: Pc-paspoort
    class PasSein(QObject):
        klaar = pyqtSignal(object)
    pas_sein = PasSein()
    ps = {"bezig": False}
    PKLEUR = {"zelfde": "#78e696", "onzeker": "#ffdc5a", "anders": "#ff7878"}

    def p_leeg():
        while p_lijst.count():
            it = p_lijst.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

    def p_stand_zet():
        lijst = paspoort.paspoorten()
        p_stand.setText(T("pas_laatste") % (lijst[0][1], len(lijst)) if lijst else T("pas_geen"))
        b_p_verg.setEnabled(bool(lijst) and not ps["bezig"])
        b_p_maak.setEnabled(not ps["bezig"])
        return lijst

    def pas_open():
        if stem:
            stem.stil()
        schermen.setCurrentIndex(2); p_leeg(); p_sv.setText("")
        lijst = p_stand_zet()
        spreek([T("pas_kop") + ".", T("pas_uitleg"), p_stand.text()])

    def pas_werk(soort):
        if ps["bezig"]:
            return
        ps["bezig"] = True; p_stand_zet(); p_leeg()
        p_sv.setText(T("pas_bezig")); p_sv.setStyleSheet("color:#ffdc5a;"); spreek([T("pas_bezig")])

        def werk():
            try:
                if soort == "maak":
                    r = paspoort.maak_paspoort("", taal)
                else:
                    oud = paspoort.laad(paspoort.paspoorten()[0][0])
                    zin, regels = paspoort.vergelijk(oud, None, taal)
                    r = {"vergelijk": True, "uitleg": zin, "regels": regels, "van": oud.get("gemaakt", "?")}
            except Exception as ex:
                r = {"uitleg": T("fout") % ex}
            pas_sein.klaar.emit(r)
        threading.Thread(target=werk, daemon=True).start()

    def pas_klaar(r):
        ps["bezig"] = False; p_stand_zet()
        p_sv.setText(r["uitleg"])
        kleur = "#f0f0f5"
        if r.get("vergelijk"):
            st_ = [g["status"] for g in r["regels"]]
            kleur = "#ff7878" if "anders" in st_ else "#78e696"
        p_sv.setStyleSheet("color:%s;" % kleur)
        zinnen = [r["uitleg"]]
        for g in r.get("regels", []):
            rij = QFrame(); rij.setObjectName("rij")
            hl = QHBoxLayout(rij); hl.setContentsMargins(16, 12, 16, 12); hl.setSpacing(18)
            a = QLabel(TX["pas_st"][0 if NL else 1].get(g["status"], "?")); a.setFont(F(2))
            a.setMinimumWidth(st["maat"] * 13); a.setStyleSheet("color:%s;" % PKLEUR.get(g["status"], "#fff"))
            b = QLabel("<b>%s</b><br>%s" % (g["onderdeel"], g["uitleg"])); b.setWordWrap(True); b.setFont(F(0, False))
            hl.addWidget(a); hl.addWidget(b, 1); p_lijst.addWidget(rij)
            if g["status"] == "anders":
                zinnen.append(g["onderdeel"] + ": " + g["uitleg"])
        p_lijst.addStretch(1)
        spreek(zinnen)

    pas_sein.klaar.connect(pas_klaar)
    b_pas.clicked.connect(pas_open); b_p_terug.clicked.connect(help_dicht)
    b_p_maak.clicked.connect(lambda: pas_werk("maak")); b_p_verg.clicked.connect(lambda: pas_werk("vergelijk"))
    b_p_map.clicked.connect(lambda: os.startfile(paspoort.map_paspoorten()) if os.name == "nt" else None)

    # ---------- 0.4 / 0.6: Bescherm mij
    def bes_open():
        if stem:
            stem.stil()
        schermen.setCurrentIndex(3); bes_scherm.open()

    b_bes.clicked.connect(bes_open)

    # ---------- kleine knoppen
    def wissel_stem():
        st["stem_aan"] = not st["stem_aan"]; inst["voorlezen"] = st["stem_aan"]; schrijf_inst(inst); zet_stem_knop()
        if not st["stem_aan"] and stem:
            stem.stil()

    def maat(d):
        st["maat"] = max(14, min(30, st["maat"] + d)); inst["tekstmaat"] = st["maat"]; schrijf_inst(inst); zet_letters()

    def info():
        d = QDialog(w); d.setWindowTitle(T("titel")); d.setStyleSheet(w.styleSheet())
        v = QVBoxLayout(d); v.setContentsMargins(26, 22, 26, 22); v.setSpacing(16)
        l = QLabel(T("info_tekst") % VERSIE); l.setFont(F(-2, False)); v.addWidget(l)
        k1, k2 = knop(T("doneer")), knop(T("sluit"))
        k1.setFont(F(-2)); k2.setFont(F(-2))
        k1.clicked.connect(lambda: webbrowser.open("https://paypal.me/roger076")); k2.clicked.connect(d.accept)
        h = QHBoxLayout(); h.addWidget(k1); h.addWidget(k2); v.addLayout(h)
        d.exec()

    b_kijk.clicked.connect(kijk); b_ruim.clicked.connect(vraag_ruim); b_van.clicked.connect(mijn)
    b_ja.clicked.connect(lambda: antwoord(True)); b_nee.clicked.connect(lambda: antwoord(False))
    b_nog.clicked.connect(lambda: spreek(st["zinnen"]) if st["zinnen"] else spreek([T("uitleg")]))
    b_stem.clicked.connect(wissel_stem); b_groter.clicked.connect(lambda: maat(2)); b_kleiner.clicked.connect(lambda: maat(-2))
    b_info.clicked.connect(info)
    QShortcut(QKeySequence("Esc"), w, activated=lambda: stem.stil() if stem else None)
    QShortcut(QKeySequence("F1"), w, activated=info)

    zet_stem_knop(); zet_letters(); knoppen()
    w.showMaximized()                                               # groot: fijn voor ouderen en slechtzienden
    QTimer.singleShot(800, lambda: spreek([T("hoi"), T("uitleg")]))

    # alleen voor de proef
    if os.environ.get("MAATJE_KIJK"):
        QTimer.singleShot(int(float(os.environ["MAATJE_KIJK"]) * 1000), kijk)
    if os.environ.get("MAATJE_VRAAG"):                              # alleen de vraag tonen, NOOIT ja drukken
        QTimer.singleShot(int(float(os.environ["MAATJE_VRAAG"]) * 1000), vraag_ruim)
    if os.environ.get("MAATJE_HELP"):                               # 0.2: "sec|zoektekst" (alleen zoeken, NOOIT ja)
        _t4, _z4 = os.environ["MAATJE_HELP"].split("|", 1)
        QTimer.singleShot(int(float(_t4) * 1000), lambda: (help_open(), help_scherm.zoekvak.setText(_z4), help_scherm.zoeken()))
    if os.environ.get("MAATJE_KVRAAG"):                             # 0.5: alleen de vraag van de eerste knop tonen, NOOIT ja
        QTimer.singleShot(int(float(os.environ["MAATJE_KVRAAG"]) * 1000), help_scherm.eerste_vraag)
    if os.environ.get("MAATJE_KLUS"):                               # 0.5: "sec|klus-id" (alleen tonen)
        _t7, _s7 = os.environ["MAATJE_KLUS"].split("|", 1)
        QTimer.singleShot(int(float(_t7) * 1000), lambda: (help_open(), help_scherm.kies(klusjes.zoek_klus(_s7))))
    if os.environ.get("MAATJE_HULP"):                               # 0.5: alleen het hulpscherm met alle klusjes
        QTimer.singleShot(int(float(os.environ["MAATJE_HULP"]) * 1000), help_open)
    if os.environ.get("MAATJE_PAS"):                                # 0.3: "sec|maak" of "sec|vergelijk"
        _t5, _s5 = os.environ["MAATJE_PAS"].split("|", 1)
        QTimer.singleShot(int(float(_t5) * 1000), lambda: (pas_open(), pas_werk(_s5)))
    if os.environ.get("MAATJE_BES"):                                # 0.4: "sec|mee" / "sec|regels" / "sec|bericht:tekst" / "sec|link:adres"
        _t6, _s6 = os.environ["MAATJE_BES"].split("|", 1)

        def _bes_proef():
            bes_open()
            if _s6 == "mee":
                bes_scherm.meekijk()
            elif _s6 == "regels":
                bes_scherm.regels()
            elif _s6.startswith("bericht:"):
                bes_scherm.bericht(); bes_scherm.invoer.setPlainText(_s6[8:].replace("\\n", "\n")); bes_scherm.check()
            elif _s6.startswith("link:"):
                bes_scherm.link(); bes_scherm.adres.setText(_s6[5:]); bes_scherm.check()
        QTimer.singleShot(int(float(_t6) * 1000), _bes_proef)
    if os.environ.get("MAATJE_SHOT"):
        def foto():
            w.grab().save(os.path.join(CACHE, "shot.png")); app.quit()
        QTimer.singleShot(int(float(os.environ["MAATJE_SHOT"]) * 1000), foto)
    app.exec()
    if stem:
        stem.stil()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        with open(os.path.join(CACHE, "error.log"), "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + traceback.format_exc() + "\n")
    finally:
        os._exit(0)
