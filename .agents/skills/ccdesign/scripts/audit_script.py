import os, re, sys, argparse

BASE = r'C:\Users\oaiskoo\doom\1_oais\07_designsystem\04_components'
BASE_THEME = r'C:\Users\oaiskoo\doom\1_oais\07_designsystem\05_components_theme'

PLATFORMS = {
    'web':          os.path.join(BASE, '01_web'),
    'flutter':      os.path.join(BASE, '02_flutter'),
    'senior_world': os.path.join(BASE_THEME, '14_senior_world'),
}


def audit_platform(base, platform_name):
    issues = []

    # 두 플랫폼 모두 서브폴더 구조 (atoms/molecules/...) 사용
    html_files = []
    for dirpath, _, filenames in os.walk(base):
        for f in filenames:
            if f.endswith('.html') and f != '00_index.html':
                html_files.append((f, os.path.join(dirpath, f)))
    html_files.sort()
    index_path = os.path.join(base, '00_index.html')

    for fname, path in html_files:
        with open(path, encoding='utf-8') as f:
            content = f.read()

        body_content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        actual_boxes = len(re.findall(r'<div class="elem-box', body_content))

        # Check 1: section-title 넘버링 범위 표기
        titles = re.findall(r'class="section-title"[^>]*>([^<]+)', body_content)
        for t in titles:
            t = t.strip()
            has_range = bool(re.search(r'\([A-Z]\d{3}-\d{3}\s*~\s*\d{3}\)', t))
            if not has_range and actual_boxes > 1:
                issues.append(f'[{platform_name}] {fname}: section-title "{t}" missing 3-digit sub-numbering range')

        # Check 2: elem-box 구조 무결성
        starts = [m.start() for m in re.finditer(r'<div class="elem-box', body_content)]
        for i, start in enumerate(starts):
            chunk = body_content[start:start+2000]
            has_id      = 'class="elem-id"' in chunk
            has_preview = 'class="elem-preview"' in chunk
            has_code    = 'class="elem-code"' in chunk
            if not (has_id and has_preview and has_code):
                missing = [x for x, ok in [('elem-id', has_id), ('elem-preview', has_preview), ('elem-code', has_code)] if not ok]
                issues.append(f'[{platform_name}] {fname}: elem-box #{i+1} missing: {missing}')

    # Check 3: 00_index.html ↔ 실제 파일 불일치
    if os.path.exists(index_path):
        with open(index_path, encoding='utf-8') as f:
            idx = f.read()

        sidebar_links = re.findall(r'class="oo-nav-item" href="([^"]+\.html)"', idx)
        content_cards = re.findall(r'class="cat-card" href="([^"]+\.html)"', idx)

        sidebar_set = set(sidebar_links)
        content_set = set(content_cards)

        in_sidebar_not_content = sidebar_set - content_set
        in_content_not_sidebar = content_set - sidebar_set

        if in_sidebar_not_content:
            issues.append(f'[{platform_name}] 00_index.html: sidebar links not in content cards: {sorted(in_sidebar_not_content)}')
        if in_content_not_sidebar:
            issues.append(f'[{platform_name}] 00_index.html: content cards not in sidebar: {sorted(in_content_not_sidebar)}')

        actual_files = set(f for f in os.listdir(base) if f.endswith('.html') and f != '00_index.html')
        in_sidebar_not_disk = {
            link for link in sidebar_set
            if not os.path.exists(os.path.normpath(os.path.join(base, link)))
        }
        in_disk_not_sidebar = actual_files - sidebar_set

        if in_sidebar_not_disk:
            issues.append(f'[{platform_name}] 00_index.html: sidebar references non-existent files: {sorted(in_sidebar_not_disk)}')
        if in_disk_not_sidebar:
            issues.append(f'[{platform_name}] 00_index.html: files on disk not listed in sidebar: {sorted(in_disk_not_sidebar)}')
    else:
        issues.append(f'[{platform_name}] 00_index.html not found')

    return issues


def main():
    parser = argparse.ArgumentParser(description='ccdesign check — 컴포넌트 정합성 감사')
    parser.add_argument('--platform', choices=['web', 'flutter', 'senior_world', 'all'], default='web',
                        help='감사 대상 플랫폼 (기본: web)')
    args = parser.parse_args()

    targets = list(PLATFORMS.items()) if args.platform == 'all' else [(args.platform, PLATFORMS[args.platform])]

    all_issues = []
    for platform_name, path in targets:
        all_issues.extend(audit_platform(path, platform_name))

    if all_issues:
        for issue in all_issues:
            print(issue)
        print(f'\n총 {len(all_issues)}개 이슈 발견')
    else:
        print('NO ISSUES FOUND')


if __name__ == '__main__':
    main()
