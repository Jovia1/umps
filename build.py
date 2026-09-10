"""Validate local links and prepare the static site for hosting."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import shutil

ROOT = Path(__file__).resolve().parent.parent
PAGES = ['index.html', 'about.html', 'services.html', 'resources.html', 'contact.html']

class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.ids, self.links, self.h1s = set(), [], 0
        self.feed(source)
    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f"Duplicate id: {attrs['id']}"
            self.ids.add(attrs['id'])
        if tag == 'h1': self.h1s += 1
        for key in ('href', 'src'):
            if key in attrs: self.links.append(attrs[key])

pages = {name: Page((ROOT / name).read_text(encoding='utf-8-sig')) for name in PAGES}
for name, page in pages.items():
    assert page.h1s == 1, f'{name}: expected one main heading'
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc: continue
        target = unquote(url.path) or name
        assert (ROOT / target).is_file(), f'{name}: missing {target}'
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, f'{name}: missing anchor {link}'

output = ROOT / 'dist'
output.mkdir(exist_ok=True)
(output / 'assets').mkdir(exist_ok=True)
for name in PAGES:
    shutil.copy2(ROOT / name, output / name)
for name in ('site.css', 'site.js', 'sacco-office.png'):
    shutil.copy2(ROOT / 'assets' / name, output / 'assets' / name)
print('Validated all 5 pages, local assets, and navigation anchors. Static site prepared in dist/.')
