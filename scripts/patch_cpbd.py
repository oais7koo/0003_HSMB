# -*- coding: utf-8 -*-
"""cpbd 패키지 호환 패치 스크립트.

cpbd PyPI 패키지(1.0.7)는 scipy.ndimage.imread를 사용하나
scipy 1.8+에서 해당 함수가 제거됨 → ImportError 발생.

이 스크립트는 cpbd/compute.py의 imread import를 cv2 기반 fallback으로 교체한다.
uv sync 후 반드시 재실행할 것.

실행:
    uv run python scripts/patch_cpbd.py
"""

import importlib.util
import pathlib
import sys


def find_cpbd_compute() -> pathlib.Path:
    spec = importlib.util.find_spec("cpbd")
    if spec is None or spec.origin is None:
        raise RuntimeError("cpbd 패키지가 설치되어 있지 않습니다. `uv add cpbd` 먼저 실행하세요.")
    return pathlib.Path(spec.origin).parent / "compute.py"


PATCH_OLD = "from scipy.ndimage import imread"
PATCH_NEW = """\
try:
    from scipy.ndimage import imread
except ImportError:
    import numpy as _np
    import cv2 as _cv2
    def imread(path, flatten=False):
        buf = _np.fromfile(path, dtype=_np.uint8)
        flag = _cv2.IMREAD_GRAYSCALE if flatten else _cv2.IMREAD_COLOR
        return _cv2.imdecode(buf, flag)"""


def patch():
    target = find_cpbd_compute()
    content = target.read_text(encoding="utf-8")

    if PATCH_NEW in content:
        print(f"[OK] 이미 패치 적용됨: {target}")
        return

    if PATCH_OLD not in content:
        print(f"[WARN] 패치 대상 라인 없음 (이미 다른 방식으로 수정됐거나 버전 변경): {target}")
        return

    patched = content.replace(PATCH_OLD, PATCH_NEW, 1)
    target.write_text(patched, encoding="utf-8")
    print(f"[DONE] 패치 완료: {target}")


def verify():
    try:
        import cpbd
        import numpy as np
        import cv2
        dummy = np.zeros((100, 100), dtype=np.uint8)
        score = cpbd.compute(dummy)
        print(f"[VERIFY] cpbd.compute(dummy) = {score:.4f}  ✅")
    except Exception as e:
        print(f"[VERIFY] 실패: {e}")


if __name__ == "__main__":
    patch()
    verify()
