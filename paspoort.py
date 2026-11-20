# -*- coding: utf-8 -*-
"""DraveHanden - Pc-paspoort 0.1: bewijs dat je je EIGEN pc terugkrijgt van de reparateur.

Voor de reparatie: maak een paspoort. Het Maatje schrijft de serienummers op van moederbord, BIOS,
processor, geheugen, schijven, videokaart en netwerkkaarten, met datum en een vingerafdruk (SHA-256).
Na de reparatie: vergelijk. Dan zie je zwart op wit wat hetzelfde is en wat anders.

Alleen LEZEN (Windows WMI). Er verandert niets aan de pc. De paspoorten staan in de map
'paspoorten' naast de app (portable) - bewaar een kopie op een usb-stick of print hem.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time

VERSIE = "0.1.1"
NO_WIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)

# serienummers die fabrikanten invullen als ze "niets" bedoelen: daar kun je niets mee bewijzen
NEP_NUMMERS = {"", "none", "null", "default string", "to be filled by o.e.m.", "to be filled by oem", "system serial number",
               "0", "00000000", "0000000000000000", "not applicable", "n/a", "oem", "not specified", "123456789",
               "03000200-0400-0500-0006-000700080009", "ffffffff-ffff-ffff-ffff-ffffffffffff",
               "00000000-0000-0000-0000-000000000000", "base board serial number", "chassis serial number"}


def _hier():
    return os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))


def _t(nl, en, taal):
    return nl if taal == "nl" else en


def map_paspoorten():
    p = os.path.join(_hier(), "paspoorten")
    os.makedirs(p, exist_ok=True)
    return p


def _schoon(x):
    return str(x or "").strip()


def echt_nummer(x):
    s = _schoon(x)
    if not s or s.lower().strip(".") in NEP_NUMMERS or "o.e.m" in s.lower() or "default" in s.lower():
        return False
    tekens = [c for c in s.lower() if c.isalnum()]
    if len(set(tekens)) <= 1:
        return False
    return tekens.count("0") < 0.7 * len(tekens)                       # "0000_0000_0100_0000" is geen echt nummer


_PS = r"""
$o = [ordered]@{}
$cs = Get-CimInstance Win32_ComputerSystem
$o.computer = @{ merk = $cs.Manufacturer; model = $cs.Model; geheugen_totaal = $cs.TotalPhysicalMemory }
$p = Get-CimInstance Win32_ComputerSystemProduct
$o.product = @{ uuid = $p.UUID; nummer = $p.IdentifyingNumber; naam = $p.Name }
$b = Get-CimInstance Win32_BaseBoard
$o.moederbord = @{ merk = $b.Manufacturer; model = $b.Product; serie = $b.SerialNumber }
$bi = Get-CimInstance Win32_BIOS
$o.bios = @{ merk = $bi.Manufacturer; versie = $bi.SMBIOSBIOSVersion; serie = $bi.SerialNumber }
$o.processor = @(Get-CimInstance Win32_Processor | ForEach-Object { @{ naam = $_.Name.Trim(); id = $_.ProcessorId; kernen = $_.NumberOfCores } })
$o.geheugen = @(Get-CimInstance Win32_PhysicalMemory | ForEach-Object { @{ plek = $_.DeviceLocator; merk = $_.Manufacturer; onderdeel = $_.PartNumber; serie = $_.SerialNumber; grootte = $_.Capacity } })
$o.schijven = @(Get-CimInstance Win32_DiskDrive | Where-Object { $_.MediaType -notlike '*xternal*' -and $_.MediaType -notlike '*emovable*' -and $_.InterfaceType -ne 'USB' } | ForEach-Object { @{ model = $_.Model; serie = $_.SerialNumber; grootte = $_.Size; soort = $_.InterfaceType } })
$o.videokaart = @(Get-CimInstance Win32_VideoController | ForEach-Object { @{ naam = $_.Name; pnp = $_.PNPDeviceID } })
$o.netwerk = @(Get-CimInstance Win32_NetworkAdapter -Filter "PhysicalAdapter=True" | Where-Object { $_.MACAddress -and $_.PNPDeviceID -like 'PCI\*' } | ForEach-Object { @{ naam = $_.Name; mac = $_.MACAddress } })
$os = Get-CimInstance Win32_OperatingSystem
$o.windows = @{ naam = $os.Caption; versie = $os.Version; geinstalleerd = $os.InstallDate.ToString('yyyy-MM-dd') }
$o | ConvertTo-Json -Depth 4 -Compress
"""


def lees_pc():
    """Leest de onderdelen (alleen lezen). Geeft een dict, of {'fout': ...}."""
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", _PS],
                           capture_output=True, text=True, timeout=90, creationflags=NO_WIN)
        d = json.loads(r.stdout or "{}")
        for k in ("processor", "geheugen", "schijven", "videokaart", "netwerk"):    # altijd een lijst
            v = d.get(k)
            d[k] = v if isinstance(v, list) else ([v] if v else [])
        return d
    except Exception as ex:
        return {"fout": str(ex)}


def vingerafdruk(onderdelen):
    return hashlib.sha256(json.dumps(onderdelen, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def mooi_gb(n):
    try:
        return ("%.0f GB" % (int(n) / 1024 ** 3)).replace(".", ",")
    except Exception:
        return "?"


def _of_onbekend(x, taal="nl"):
    s = _schoon(x)
    return s if (s and "o.e.m" not in s.lower() and "default" not in s.lower() and s.lower() != "unknown") else _t("onbekend", "unknown", taal)


def leesbaar(p, taal="nl"):
    """Het paspoort als gewone tekst (om te printen of op een usb-stick te zetten)."""
    o = p["onderdelen"]
    r = []
    r.append(_t("PC-PASPOORT - gemaakt door DraveMaatje (Dravenlock)", "PC PASSPORT - made by DraveMaatje (Dravenlock)", taal))
    r.append("=" * 60)
    r.append(_t("Gemaakt op:      %s", "Made on:         %s", taal) % p["gemaakt"])
    if p.get("naam"):
        r.append(_t("Naam / reden:    %s", "Name / reason:   %s", taal) % p["naam"])
    c = o.get("computer", {}); pr = o.get("product", {})
    r.append(_t("Computer:        %s %s", "Computer:        %s %s", taal) % (_of_onbekend(c.get("merk"), taal), _of_onbekend(c.get("model"), taal)))
    r.append(_t("Computer-id:     %s", "Computer id:     %s", taal) % _schoon(pr.get("uuid")))
    if echt_nummer(pr.get("nummer")):
        r.append(_t("Serienummer:     %s", "Serial number:   %s", taal) % _schoon(pr.get("nummer")))
    mb = o.get("moederbord", {})
    r.append("")
    r.append(_t("MOEDERBORD:      %s %s", "MOTHERBOARD:     %s %s", taal) % (_schoon(mb.get("merk")), _schoon(mb.get("model"))))
    r.append(_t("  serienummer:   %s", "  serial:        %s", taal) % (_schoon(mb.get("serie")) if echt_nummer(mb.get("serie")) else _t("geen echt nummer", "no real number", taal)))
    bi = o.get("bios", {})
    r.append(_t("BIOS:            %s, versie %s, serienummer %s", "BIOS:            %s, version %s, serial %s", taal)
             % (_schoon(bi.get("merk")), _schoon(bi.get("versie")), _schoon(bi.get("serie")) if echt_nummer(bi.get("serie")) else _t("geen echt nummer", "no real number", taal)))
    for x in o.get("processor", []):
        r.append(_t("PROCESSOR:       %s (%s kernen), id %s", "PROCESSOR:       %s (%s cores), id %s", taal)
                 % (_schoon(x.get("naam")), x.get("kernen"), _schoon(x.get("id"))))
    r.append("")
    r.append(_t("GEHEUGEN (%d latjes):", "MEMORY (%d sticks):", taal) % len(o.get("geheugen", [])))
    for x in o.get("geheugen", []):
        r.append("  %-10s %-8s %s %s  serie %s" % (_schoon(x.get("plek")), mooi_gb(x.get("grootte")), _of_onbekend(x.get("merk"), taal),
                                                   _schoon(x.get("onderdeel")),
                                                   _schoon(x.get("serie")) if echt_nummer(x.get("serie")) else _t("geen echt nummer", "no real number", taal)))
    r.append(_t("SCHIJVEN:", "DRIVES:", taal))
    for x in o.get("schijven", []):
        r.append("  %s (%s)  serie %s" % (_schoon(x.get("model")), mooi_gb(x.get("grootte")),
                                          _schoon(x.get("serie")).rstrip(".") if echt_nummer(x.get("serie")) else _t("geen echt nummer", "no real number", taal)))
    r.append(_t("VIDEOKAART:", "GRAPHICS CARD:", taal))
    for x in o.get("videokaart", []):
        r.append("  %s" % _schoon(x.get("naam")))
    r.append(_t("NETWERK:", "NETWORK:", taal))
    for x in o.get("netwerk", []):
        r.append("  %s  %s" % (_schoon(x.get("mac")), _schoon(x.get("naam"))))
    w = o.get("windows", {})
    r.append("")
    r.append(_t("WINDOWS:         %s (%s), geinstalleerd op %s", "WINDOWS:         %s (%s), installed on %s", taal)
             % (_schoon(w.get("naam")), _schoon(w.get("versie")), _schoon(w.get("geinstalleerd"))))
    r.append("")
    r.append(_t("Vingerafdruk (SHA-256): %s", "Fingerprint (SHA-256): %s", taal) % p["vingerafdruk"])
    r.append(_t("Bewaar een kopie op een usb-stick, of print dit uit.", "Keep a copy on a usb stick, or print this.", taal))
    return "\n".join(r)


def maak_paspoort(naam="", taal="nl"):
    """Leest de pc en bewaart een paspoort (json + leesbare txt). Verandert niets aan de pc."""
    o = lees_pc()
    if "fout" in o:
        return {"gedaan": False, "uitleg": _t("Het paspoort maken lukte niet: %s", "Making the passport failed: %s", taal) % o["fout"]}
    p = {"versie": VERSIE, "gemaakt": time.strftime("%Y-%m-%d %H:%M"), "naam": naam.strip(),
         "onderdelen": o, "vingerafdruk": vingerafdruk(o)}
    stempel = time.strftime("%Y-%m-%d_%H%M")
    m = map_paspoorten()
    with open(os.path.join(m, "paspoort_%s.json" % stempel), "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
    with open(os.path.join(m, "paspoort_%s.txt" % stempel), "w", encoding="utf-8") as f:
        f.write(leesbaar(p, taal))
    p["bestand"] = os.path.join(m, "paspoort_%s.txt" % stempel)
    return {"gedaan": True, "paspoort": p,
            "uitleg": _t("Klaar! Ik heb het paspoort van je pc gemaakt, op %s. Bewaar een kopie op een usb-stick of print het uit."
                         % p["gemaakt"], "Done! I made your pc's passport on %s. Keep a copy on a usb stick or print it." % p["gemaakt"], taal)}


def paspoorten():
    """Alle bewaarde paspoorten, nieuwste eerst: [(pad, gemaakt, naam)]."""
    uit = []
    m = map_paspoorten()
    for f in os.listdir(m):
        if f.startswith("paspoort_") and f.endswith(".json"):
            try:
                with open(os.path.join(m, f), encoding="utf-8") as h:
                    p = json.load(h)
                uit.append((os.path.join(m, f), p.get("gemaakt", "?"), p.get("naam", "")))
            except Exception:
                pass
    return sorted(uit, key=lambda x: x[1], reverse=True)


def laad(pad):
    with open(pad, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- vergelijken
def _lijst_vergelijk(oud, nieuw, sleutel, naam_fn):
    """Vergelijk een lijst onderdelen op serienummer (of naam als er geen echt nummer is)."""
    def id_van(x):
        s = _schoon(x.get(sleutel))
        return ("serie", s) if echt_nummer(s) else ("naam", naam_fn(x))
    a = [id_van(x) for x in oud]
    b = [id_van(x) for x in nieuw]
    weg = [x for x in a if x not in b]
    erbij = [x for x in b if x not in a]
    zeker = all(k == "serie" for k, _ in a + b)
    return weg, erbij, zeker


def vergelijk(oud, nieuw=None, taal="nl"):
    """Vergelijk een paspoort met de pc van NU (of met een ander paspoort).
    Geeft (samenvatting, [regels]) - elke regel: {'onderdeel', 'status': 'zelfde'/'anders'/'onzeker', 'uitleg'}."""
    if nieuw is None:
        n = lees_pc()
        if "fout" in n:
            return _t("Ik kon de pc nu niet lezen.", "I could not read the pc now.", taal), []
    else:
        n = nieuw["onderdelen"]
    o = oud["onderdelen"]
    regels = []

    def regel(onderdeel, status, uitleg):
        regels.append({"onderdeel": onderdeel, "status": status, "uitleg": uitleg})

    # moederbord: het hart van de pc
    mo, mn = o.get("moederbord", {}), n.get("moederbord", {})
    so, sn = _schoon(mo.get("serie")), _schoon(mn.get("serie"))
    md = "%s %s" % (_schoon(mn.get("merk")), _schoon(mn.get("model")))
    if echt_nummer(so) and echt_nummer(sn):
        if so == sn:
            regel(_t("Moederbord", "Motherboard", taal), "zelfde", _t("Hetzelfde moederbord (%s), zelfde serienummer." % md,
                                                                      "Same motherboard (%s), same serial." % md, taal))
        else:
            regel(_t("Moederbord", "Motherboard", taal), "anders",
                  _t("ANDER moederbord! Eerst serienummer %s, nu %s." % (so, sn), "DIFFERENT motherboard! Was serial %s, now %s." % (so, sn), taal))
    else:
        zelfde_model = (_schoon(mo.get("merk")), _schoon(mo.get("model"))) == (_schoon(mn.get("merk")), _schoon(mn.get("model")))
        regel(_t("Moederbord", "Motherboard", taal), "onzeker" if zelfde_model else "anders",
              _t("Zelfde soort moederbord (%s), maar de fabrikant gaf geen echt serienummer." % md if zelfde_model
                 else "ANDER soort moederbord! Eerst %s %s, nu %s." % (_schoon(mo.get("merk")), _schoon(mo.get("model")), md),
                 "Same motherboard type, but no real serial." if zelfde_model else "DIFFERENT motherboard type!", taal))

    # computer-id (UUID) - zit in het moederbord/BIOS
    uo, un = _schoon(o.get("product", {}).get("uuid")), _schoon(n.get("product", {}).get("uuid"))
    if echt_nummer(uo) and echt_nummer(un):
        regel(_t("Computer-id", "Computer id", taal), "zelfde" if uo == un else "anders",
              _t("Zelfde computer-id." if uo == un else "ANDERE computer-id! Eerst %s, nu %s." % (uo, un),
                 "Same computer id." if uo == un else "DIFFERENT computer id!", taal))

    # processor
    po = [_schoon(x.get("naam")) + "|" + _schoon(x.get("id")) for x in o.get("processor", [])]
    pn = [_schoon(x.get("naam")) + "|" + _schoon(x.get("id")) for x in n.get("processor", [])]
    pnaam = ", ".join(_schoon(x.get("naam")) for x in n.get("processor", [])) or "?"
    if po == pn:
        regel("Processor", "onzeker",
              _t("Zelfde soort processor (%s). Let op: een processor heeft geen eigen serienummer dat Windows kan zien." % pnaam,
                 "Same processor type (%s). Note: Windows can't see a unique processor serial." % pnaam, taal))
    else:
        oudnaam = ", ".join(_schoon(x.get("naam")) for x in o.get("processor", [])) or "?"
        regel("Processor", "anders", _t("ANDERE processor! Eerst %s, nu %s." % (oudnaam, pnaam), "DIFFERENT processor!", taal))

    # geheugen, schijven, videokaart, netwerk
    for sleutel_lijst, titel, serie, naam_fn in (
            ("geheugen", _t("Geheugen", "Memory", taal), "serie",
             lambda x: "%s %s %s" % (_schoon(x.get("merk")), _schoon(x.get("onderdeel")), mooi_gb(x.get("grootte")))),
            ("schijven", _t("Schijven", "Drives", taal), "serie",
             lambda x: "%s %s" % (_schoon(x.get("model")), mooi_gb(x.get("grootte")))),
            ("videokaart", _t("Videokaart", "Graphics card", taal), "pnp", lambda x: _schoon(x.get("naam"))),
            ("netwerk", _t("Netwerkkaart", "Network card", taal), "mac", lambda x: _schoon(x.get("naam")))):
        weg, erbij, zeker = _lijst_vergelijk(o.get(sleutel_lijst, []), n.get(sleutel_lijst, []), serie, naam_fn)
        if not weg and not erbij:
            regel(titel, "zelfde" if zeker else "onzeker",
                  _t("Hetzelfde%s." % ("" if zeker else " (zonder echt serienummer)"), "Same%s." % ("" if zeker else " (no real serial)"), taal))
        else:
            delen = []
            if weg:
                delen.append(_t("weg: %s", "gone: %s", taal) % ", ".join(v for _k, v in weg))
            if erbij:
                delen.append(_t("nieuw: %s", "new: %s", taal) % ", ".join(v for _k, v in erbij))
            regel(titel, "anders", _t("ANDERS! ", "DIFFERENT! ", taal) + "; ".join(delen))

    # windows
    wo, wn = o.get("windows", {}), n.get("windows", {})
    if _schoon(wo.get("geinstalleerd")) != _schoon(wn.get("geinstalleerd")):
        regel("Windows", "anders", _t("Windows is opnieuw geinstalleerd (eerst %s, nu %s). Dat kan bij een reparatie horen, vraag ernaar."
                                      % (wo.get("geinstalleerd"), wn.get("geinstalleerd")),
                                      "Windows was reinstalled. That can be part of a repair; ask about it.", taal))
    else:
        regel("Windows", "zelfde", _t("Dezelfde Windows-installatie.", "Same Windows installation.", taal))

    anders = [r for r in regels if r["status"] == "anders"]
    hart = [r for r in anders if r["onderdeel"] in (_t("Moederbord", "Motherboard", taal), _t("Computer-id", "Computer id", taal))]
    if hart:
        sv = _t("LET OP: dit lijkt een ANDERE pc te zijn. Het moederbord of de computer-id is anders. Bewaar dit en vraag de reparateur om uitleg.",
                "CAREFUL: this looks like a DIFFERENT pc. Ask the repair shop for an explanation.", taal)
    elif anders:
        sv = _t("Dit is dezelfde pc, maar er zijn %d onderdelen anders. Was dat afgesproken? Vraag anders om uitleg." % len(anders),
                "This is the same pc, but %d parts are different. Was that agreed? Otherwise ask." % len(anders), taal)
    else:
        sv = _t("Goed nieuws: dit is dezelfde pc. Alle onderdelen die ik kan zien, zijn hetzelfde.",
                "Good news: this is the same pc. All parts I can see are the same.", taal)
    return sv, regels


if __name__ == "__main__":                                               # proef: alleen lezen, niets bewaren
    o = lees_pc()
    if "fout" in o:
        print("fout:", o["fout"])
    else:
        p = {"gemaakt": time.strftime("%Y-%m-%d %H:%M"), "naam": "proef", "onderdelen": o, "vingerafdruk": vingerafdruk(o)}
        print(leesbaar(p))
        print()
        sv, rg = vergelijk(p, p)
        print(sv)
        for r in rg:
            print(" ", r["status"], "-", r["onderdeel"], ":", r["uitleg"])
