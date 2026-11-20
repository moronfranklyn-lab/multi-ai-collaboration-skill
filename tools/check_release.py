#!/usr/bin/env python3
"""Check this public Skill package; report locations, never matched values."""

import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

REQUIRED = {
    'SKILL.md', 'README.md', 'agents/openai.yaml',
    'references/protocol.md', 'references/records.md',
    'references/evaluation.md', 'templates/collaboration-contract.md',
    'templates/handoff.md', 'templates/change-event.json',
    'tools/check_release.py', '.github/workflows/validate.yml', '.gitignore',
}
ALLOWED_SUFFIXES = {'.md', '.json', '.py', '.yaml', '.yml'}
DISCLOSURES = {
    'machine path': r'/(?:Users|Volumes|home)/[^\s/`]+',
    'tenant resource URL': r'https?://[A-Za-z0-9-]+\.(?:feishu\.cn|larksuite\.com)/',
    'provider resource ID': r'\b(?:tbl|rec|fld|vew)[A-Za-z0-9]{10,}\b',
    'GitHub credential': r'\bgh[pousr]_[A-Za-z0-9]{20,}\b',
    'API credential': r'\bsk-[A-Za-z0-9_-]{20,}\b',
    'private key': r'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----',
    'email address': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
}


def check(root):
    root = root.resolve()
    errors = []
    for required in sorted(REQUIRED):
        if not (root / required).is_file():
            errors.append(f'{required}: missing required file')
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if '.git' in rel.parts or '__pycache__' in rel.parts:
            continue
        if path.is_symlink():
            errors.append(f'{rel}: symlink is not allowed')
            continue
        if any(part in {'private', 'local-config'} for part in rel.parts):
            errors.append(f'{rel}: private configuration is not allowed')
            continue
        if not path.is_file():
            continue
        if path.name != '.gitignore' and path.suffix not in ALLOWED_SUFFIXES:
            errors.append(f'{rel}: unexpected file type')
        try:
            content = path.read_text(encoding='utf-8')
        except (UnicodeError, OSError):
            errors.append(f'{rel}: cannot read as UTF-8 text')
            continue
        for label, pattern in DISCLOSURES.items():
            if re.search(pattern, content):
                errors.append(f'{rel}: possible {label}')
        if path.suffix == '.json':
            try:
                json.loads(content)
            except ValueError:
                errors.append(f'{rel}: invalid JSON')
        if path.suffix == '.md':
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', content):
                target = link.strip().strip('<>')
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                resolved = (path.parent / unquote(parsed.path)).resolve()
                if not resolved.is_relative_to(root):
                    errors.append(f'{rel}: link escapes package')
                elif not resolved.exists():
                    errors.append(f'{rel}: missing relative link target')
        if path.name == 'SKILL.md':
            if not re.match(r'\A---\n[\s\S]+?\n---\n', content):
                errors.append(f'{rel}: missing YAML frontmatter')
            if not re.search(r'^name: multi-ai-collaboration$', content, re.M):
                errors.append(f'{rel}: incorrect Skill name')
            if '[TODO:' in content:
                errors.append(f'{rel}: unfinished scaffold')
    return errors


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    errors = check(root)
    if errors:
        for error in errors:
            print(error)
        return 1
    print('Release checks passed. Manual privacy and content review still required.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
