"""새 위키 항목 파일을 템플릿에서 생성한다.

사용법:
    python tools/new_entry.py <카테고리> "<제목>" [--slug <slug>]

카테고리: bm-catalog | genres | prototypes

예시:
    python tools/new_entry.py bm-catalog "쿠폰형 할인" --slug coupon-discount
    -> docs/bm-catalog/coupon-discount.md 생성 (템플릿 복사 + 제목만 채움)

이 스크립트는 파일만 만든다. bm-catalog/index.md, genres/index.md,
prototypes/index.md 표에 새 행을 추가하는 건 별도로 해야 한다.
"""

import argparse
import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
CATEGORIES = {"bm-catalog", "genres", "prototypes"}


def slugify(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9가-힣]+", "-", s)
    return s.strip("-")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("category", choices=sorted(CATEGORIES))
    parser.add_argument("title")
    parser.add_argument("--slug", default=None, help="파일명으로 쓸 slug (기본: 제목에서 자동 생성)")
    args = parser.parse_args()

    category_dir = DOCS / args.category
    template_path = category_dir / "_template.md"
    if not template_path.exists():
        print(f"오류: 템플릿을 찾을 수 없습니다 ({template_path})", file=sys.stderr)
        return 1

    slug = args.slug or slugify(args.title)
    if not slug:
        print("오류: slug를 만들 수 없습니다. --slug로 직접 지정하세요.", file=sys.stderr)
        return 1

    target_path = category_dir / f"{slug}.md"
    if target_path.exists():
        print(f"오류: 이미 존재하는 파일입니다 ({target_path})", file=sys.stderr)
        return 1

    content = template_path.read_text(encoding="utf-8")
    content = content.replace("{BM 이름}", args.title)
    content = content.replace("{장르 이름}", args.title)
    content = content.replace("{프로토타입 이름}", args.title)

    target_path.write_text(content, encoding="utf-8")
    print(f"생성됨: {target_path.relative_to(DOCS.parent)}")
    print(f"다음 할 일: docs/{args.category}/index.md 표에 이 항목을 한 줄 추가하세요.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
