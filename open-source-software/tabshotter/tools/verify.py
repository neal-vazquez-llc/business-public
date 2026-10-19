#!/usr/bin/env python3
"""Verify the exact sanitized source bytes embedded by TabShotterUwU (stdlib only)."""
import hashlib
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

class CaptureParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = {}
        self.active = None
    def handle_starttag(self, tag, attrs):
        identifier = dict(attrs).get('id')
        if tag == 'pre' and identifier in ('capture-metadata', 'snapshot-source'):
            if identifier in self.parts:
                raise ValueError('Duplicate capture field')
            self.parts[identifier] = []
            self.active = identifier
    def handle_endtag(self, tag):
        if tag == 'pre':
            self.active = None
    def handle_data(self, data):
        if self.active:
            self.parts[self.active].append(data)

def verify(path):
    parser = CaptureParser()
    parser.feed(Path(path).read_text(encoding='utf-8'))
    metadata = json.loads(''.join(parser.parts['capture-metadata']))
    source = ''.join(parser.parts['snapshot-source'])
    actual = hashlib.sha256(source.encode('utf-8')).hexdigest()
    return actual == metadata['snapshot_sha256'], actual

if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise ValueError('Usage: python3 tools/verify.py CAPTURE.html')
        valid, digest = verify(sys.argv[1])
        print(('MATCH' if valid else 'MISMATCH') + ': ' + digest)
        print('Checks source integrity only; not origin, timestamp, metadata or authenticity.')
        sys.exit(0 if valid else 1)
    except (ValueError, KeyError, OSError) as error:
        print('Invalid capture: ' + str(error), file=sys.stderr)
        sys.exit(2)
