# HSUP tananyag letöltő

A [HSUP](https://hsup.nkfih.gov.hu) program jelen féléves tananyagát tölti le egy `output.md` Markdown fájlba, amiből már bármilyen formátumba átalakítható pl. [pandoc](https://pandoc.org) segítségével

Például így átalakítható EPUB formátumba: 
```
pandoc output.md -o output.epub -s
```

## Telepítés

1. Töltsd le a repo-t:
```
git clone https://github.com/Andruida/hsup-scraper.git
```

2. Telepítsd a [Python3](https://www.python.org/downloads/)-at, ha még nincs telepítve, majd telepítsd a `requests` könyvtárat
```
pip install requests
```

3. Készíts egy másolatot `config_sample.json` fájlról `config.json` néven, és írd be a HSUP-s fiókod adatait

4. Futtasd le a `scraper.py` fájlt