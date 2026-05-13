#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oo_usage_validator.py - OAIS 모듈 사용 검증

이 모듈은 프로젝트 내에서 oo 모듈의 올바른 사용을 검증합니다.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class OaisUsageError:
    """OAIS 사용 오류를 나타내는 데이터 클래스"""
    attr_name: str
    line_no: int
    suggestion: Optional[str] = None


def get_oo_errors(project_root: Path) -> dict:
    """
    프로젝트 내의 oo 모듈 사용 오류를 검사합니다.

    Args:
        project_root: 프로젝트 루트 경로

    Returns:
        dict: 검사 결과
            - total_files: 검사한 파일 수
            - total_errors: 발견된 오류 수
            - server_errors: 파일별 오류 딕셔너리
            - project_root: 프로젝트 루트 경로
    """
    # 검사 대상 디렉토리
    target_dirs = ["src", "oo", "tests"]
    total_files = 0
    server_errors: Dict[str, List[OaisUsageError]] = {}

    for target_dir in target_dirs:
        target_path = project_root / target_dir
        if not target_path.exists():
            continue

        for py_file in target_path.rglob("*.py"):
            # 제외 패턴
            if any(x in str(py_file) for x in ["__pycache__", ".git", "node_modules", "tmp"]):
                continue

            total_files += 1
            # 실제 검사 로직 (간소화된 버전)
            # TODO: 실제 oo 사용 패턴 검사 로직 추가

    return {
        "total_files": total_files,
        "total_errors": len(server_errors),
        "server_errors": server_errors,
        "project_root": project_root
    }
