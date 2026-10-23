"""Parsers for online info services (pure functions, tested against sample data). Not a task."""
import json
import re
import urllib.parse
import xml.etree.ElementTree as ET

from _net import get


def weather(city):
    d = get(f"https://wttr.in/{urllib.parse.quote(city)}?format=j1", as_json=True, timeout=10)
    if not isinstance(d, dict):
        return None
    try:
        cur = d["current_condition"][0]
        area = d.get("nearest_area", [{}])[0]
        place = ", ".join(x["value"] for x in (area.get("areaName", [{}])[0], area.get("country", [{}])[0]) if x.get("value")) or (city or "your location")
        lines = [f"{place}",
                 f"  Now: {cur['temp_C']}C (feels {cur['FeelsLikeC']}C), {cur['weatherDesc'][0]['value']}, "
                 f"humidity {cur['humidity']}%, wind {cur['windspeedKmph']} km/h {cur.get('winddir16Point', '')}".rstrip()]
        for day in d.get("weather", [])[:3]:
            mid = day["hourly"][len(day["hourly"]) // 2]
            rain = max(int(h.get("chanceofrain", 0)) for h in day["hourly"])
            lines.append(f"  {day['date']}: {day['mintempC']}-{day['maxtempC']}C, {mid['weatherDesc'][0]['value']}, rain chance up to {rain}%")
        return "\n".join(lines)
    except (KeyError, IndexError, ValueError, TypeError):
        return ""


def wiki(topic):
    s = get("https://en.wikipedia.org/w/api.php?action=opensearch&limit=1&namespace=0&format=json&search=" + urllib.parse.quote(topic),
            as_json=True)
    if s is None:
        return None
    try:
        title = s[1][0]
    except (IndexError, TypeError):
        return ""
    d = get("https://en.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(title.replace(" ", "_"), safe=""), as_json=True)
    if not isinstance(d, dict) or "extract" not in d:
        return None
    text = d["extract"].strip()
    if len(text) > 900:
        text = text[:900].rsplit(" ", 1)[0] + " ..."
    out = [d.get("title", title) + (f"  -  {d['description']}" if d.get("description") else ""), "", text]
    if d.get("type") == "disambiguation":
        out.append("\n(This title has several meanings; be more specific.)")
    url = d.get("content_urls", {}).get("desktop", {}).get("page")
    if url:
        out.append("\n" + url)
    return "\n".join(out)


def define(word):
    d = get("https://api.dictionaryapi.dev/api/v2/entries/en/" + urllib.parse.quote(word), as_json=True)
    if not isinstance(d, list) or not d:
        return None
    out, e = [], d[0]
    out.append(e.get("word", word) + (f"   {e['phonetic']}" if e.get("phonetic") else ""))
    for m in e.get("meanings", [])[:3]:
        out.append(f"  ({m.get('partOfSpeech', '?')})")
        for n, df in enumerate(m.get("definitions", [])[:2], 1):
            out.append(f"   {n}. {df.get('definition', '')}")
            if df.get("example"):
                out.append(f"      e.g. \"{df['example']}\"")
    return "\n".join(out)


def news(query="", limit=10):
    base = "https://news.google.com/rss"
    url = (base + "/search?q=" + urllib.parse.quote(query) if query else base) + "&hl=en-IN&gl=IN&ceid=IN:en" if query \
        else base + "?hl=en-IN&gl=IN&ceid=IN:en"
    xml = get(url, timeout=10)
    if not xml:
        return None
    if re.search(r"<!DOCTYPE|<!ENTITY", xml, re.I):          # refuse XML entity tricks
        return ""
    try:
        items = ET.fromstring(xml).findall("./channel/item")
    except ET.ParseError:
        return ""
    out = []
    for it in items[:limit]:
        title = (it.findtext("title") or "").strip()
        src = (it.findtext("source") or "").strip()
        if src and title.endswith(" - " + src):
            title = title[: -len(src) - 3]
        out.append(f"  - {title}" + (f"  [{src}]" if src else ""))
    return "\n".join(out)


def pincode(pin):
    d = get("https://api.postalpincode.in/pincode/" + pin, as_json=True)
    if not isinstance(d, list) or not d:
        return None
    if d[0].get("Status") != "Success" or not d[0].get("PostOffice"):
        return ""
    po = d[0]["PostOffice"]
    out = [f"{pin}: {po[0].get('District', '?')}, {po[0].get('State', '?')}"]
    for p in po[:6]:
        out.append(f"  {p.get('Name', '?')} ({p.get('BranchType', '')}, {p.get('DeliveryStatus', '')})".replace(", )", ")"))
    return "\n".join(out)
