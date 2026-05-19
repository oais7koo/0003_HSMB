#!/usr/bin/env python3
"""ooscrap_search.py - 유튜브서머리/읽을거리 키워드 검색 (QMD BM25 → grep 폴백)"""

import os
import sys
import subprocess
import argparse

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
SCRAPING_DIR = os.path.join(PROJECT_ROOT, '04_scraping')
SEARCH_DIRS = [
    os.path.join(SCRAPING_DIR, '01_유튜브서머리'),
    os.path.join(SCRAPING_DIR, '04_읽을거리'),
]


def search_qmd(query, limit):
    """QMD BM25 검색 (04_scraping/ 경로 필터링)"""
    try:
        result = subprocess.run(
            ['qmd', 'search', query],
            capture_output=True, text=True, timeout=30, encoding='utf-8'
        )
        if result.returncode != 0:
            return None

        lines = result.stdout.strip().split('\n')
        hits = []
        current = None

        for line in lines:
            if line.startswith('qmd://oais/04-scraping/'):
                # QMD 경로 → 실제 경로 변환
                parts = line.split(' ')
                path_part = parts[0].replace('qmd://oais/', '').split(':')[0]
                score = ''
                for p in parts:
                    if p.startswith('Score:'):
                        score = parts[parts.index(p) + 1] if parts.index(p) + 1 < len(parts) else ''
                        break
                current = {'path': path_part, 'score': score, 'preview': ''}
                hits.append(current)
            elif current and line.startswith('Title:'):
                current['title'] = line.replace('Title:', '').strip()
            elif current and line.strip() and not line.startswith('@@') and not line.startswith('Score:'):
                if not current['preview']:
                    current['preview'] = line.strip()[:100]

        return hits[:limit] if hits else None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def search_grep(query, limit):
    """grep 폴백 검색 (QMD 미설치 시)"""
    hits = []
    for search_dir in SEARCH_DIRS:
        if not os.path.exists(search_dir):
            continue
        category = '유튜브서머리' if '유튜브서머리' in search_dir else '읽을거리'
        for fname in sorted(os.listdir(search_dir), reverse=True):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(search_dir, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                if query.lower() in content.lower():
                    # 제목 추출 (첫 번째 # 행)
                    title = fname[:-3]
                    for line in content.split('\n'):
                        if line.startswith('# '):
                            title = line[2:].strip()
                            break
                    # 매칭 라인 미리보기
                    preview = ''
                    for line in content.split('\n'):
                        if query.lower() in line.lower():
                            preview = line.strip()[:100]
                            break
                    hits.append({
                        'title': title,
                        'category': category,
                        'file': fname,
                        'preview': preview,
                    })
                    if len(hits) >= limit:
                        return hits
            except Exception:
                continue
    return hits


def main():
    parser = argparse.ArgumentParser(description='ccscrap search')
    parser.add_argument('query', help='검색 키워드')
    parser.add_argument('--limit', type=int, default=10, help='최대 결과 수 (기본: 10)')
    args = parser.parse_args()

    print(f'[ccscrap search] "{args.query}" (최대 {args.limit}건)')
    print(f'  대상: 04_scraping/01_유튜브서머리/, 04_scraping/04_읽을거리/')
    print()

    # QMD 우선, 실패 시 grep 폴백
    hits = search_qmd(args.query, args.limit)
    engine = 'QMD BM25'

    if hits is None:
        hits = search_grep(args.query, args.limit)
        engine = 'grep'

    if not hits:
        print(f'  결과 없음 (엔진: {engine})')
        return

    print(f'  {len(hits)}건 발견 (엔진: {engine})')
    print()

    for i, hit in enumerate(hits, 1):
        title = hit.get('title', hit.get('path', ''))
        category = hit.get('category', '')
        preview = hit.get('preview', '')
        score = hit.get('score', '')

        header = f'[{i}] {title}'
        if category:
            header += f'  [{category}]'
        if score:
            header += f'  ({score})'
        print(header)
        fname = hit.get('file', '')
        if fname:
            if hit.get('category') == '유튜브서머리':
                print(f'    04_scraping/01_유튜브서머리/{fname}')
            elif hit.get('category') == '읽을거리':
                print(f'    04_scraping/04_읽을거리/{fname}')
        if preview:
            print(f'    {preview}')
        print()


if __name__ == '__main__':
    main()
