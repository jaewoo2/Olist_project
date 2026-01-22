#!/usr/bin/env python3
"""
Olist 프로젝트 폴더 구조 자동 생성 스크립트
실행: python setup_project.py
"""

import os
from pathlib import Path


def create_project_structure():
    """프로젝트 폴더 구조 생성"""
    
    # 루트 폴더
    root = Path("../project2")
    
    # 폴더 구조 정의
    folders = [
        # 데이터 폴더
        "data/raw",
        "data/processed",
        
        # 노트북 폴더
        "notebooks",
        
        # 소스 코드 폴더
        "src",
        
        # 이미지 폴더
        "images/eda",
        "images/hypothesis",
        "images/strategy",
        "images/final",
        
        # 보고서 폴더
        "reports",
        
        # 발표 자료 폴더
        "presentation",
        
        # 테스트 폴더 (선택)
        "tests",
    ]
    
    # 폴더 생성
    print("🚀 Olist 프로젝트 폴더 구조 생성 중...\n")
    
    for folder in folders:
        folder_path = root / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {folder_path}")
    
    # __init__.py 파일 생성 (src 폴더)
    init_file = root / "src" / "__init__.py"
    init_file.touch()
    print(f"\n✅ Created: {init_file}")
    
    # .gitkeep 파일 생성 (빈 폴더 추적용)
    gitkeep_folders = [
        "data/raw",
        "data/processed",
        "images/eda",
        "images/hypothesis",
        "images/strategy",
        "images/final",
    ]
    
    for folder in gitkeep_folders:
        gitkeep = root / folder / ".gitkeep"
        gitkeep.touch()
    
    print(f"\n✅ Created .gitkeep files in empty folders")
    
    print("\n" + "="*60)
    print("✨ 프로젝트 폴더 구조 생성 완료!")
    print("="*60)
    print(f"\n📁 프로젝트 루트: {root}")
    print("\n다음 단계:")
    print("1. Kaggle에서 Olist 데이터 다운로드")
    print("2. CSV 파일들을 /project2/data/raw/ 폴더에 저장")
    print("3. requirements.txt 설치: pip install -r requirements.txt")
    print("4. notebooks/01_data_loading_eda.ipynb 실행")


if __name__ == "__main__":
    create_project_structure()
