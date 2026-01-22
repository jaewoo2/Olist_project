import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(os.getcwd())

from src.data_loader import load_all_tables
from src.utils import set_korean_font

def generate_quality_report():
    # 1. 환경 설정 및 데이터 로드
    set_korean_font()
    tables = load_all_tables(verbose=False)
    
    report_dir = Path("reports")
    img_dir = Path("images/eda")
    report_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)
    
    report_content = "# Olist 데이터셋 품질 및 기술통계 분석 보고서\n\n"
    report_content += "본 보고서는 Olist 데이터셋의 결측치 현황, 주요 수치형 변수의 기술통계, 그리고 이상치 분석 결과를 포함합니다.\n\n"
    
    # 2. 테이블별 분석
    for table_name, df in tables.items():
        if df is None: continue
        
        report_content += f"## 📊 {table_name.upper()} 테이블\n\n"
        
        # 2.1 결측치 분석
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        
        report_content += "### 🔍 1. 결측치 현황\n"
        if len(missing) == 0:
            report_content += "- ✅ 결측치 없음\n\n"
        else:
            report_content += "| 컬럼명 | 결측치 수 | 비율 (%) |\n"
            report_content += "| :--- | :---: | :---: |\n"
            for col, count in missing.items():
                pct = (count / len(df)) * 100
                report_content += f"| {col} | {count:,} | {pct:.2f}% |\n"
            report_content += "\n"
            
        # 2.2 기술통계량 분석
        num_df = df.select_dtypes(include=['number'])
        if not num_df.empty:
            report_content += "### 🔢 2. 수치형 컬럼 기술통계\n\n"
            desc = num_df.describe().transpose()
            
            # 마크다운 테이블 직접 생성
            report_content += "| 컬럼 | count | mean | std | min | 25% | 50% | 75% | max |\n"
            report_content += "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
            for col, stats in desc.iterrows():
                report_content += f"| {col} | {stats['count']:.0f} | {stats['mean']:.2f} | {stats['std']:.2f} | {stats['min']:.2f} | {stats['25%']:.2f} | {stats['50%']:.2f} | {stats['75%']:.2f} | {stats['max']:.2f} |\n"
            report_content += "\n"
        
        # 2.3 이상치 분석 (Boxplot)
        num_cols = num_df.columns.tolist()
        # ID 성격의 컬럼 제외 (zip_code 등)
        plot_cols = [c for c in num_cols if 'zip' not in c.lower() and c != 'payment_sequential']
        
        if plot_cols:
            report_content += "### 📈 3. 이상치 분석 (Boxplot)\n"
            
            # 그래프 생성
            fig, axes = plt.subplots(1, len(plot_cols), figsize=(max(4 * len(plot_cols), 10), 6))
            if len(plot_cols) == 1: axes = [axes]
            
            for i, col in enumerate(plot_cols):
                sns.boxplot(y=df[col].dropna(), ax=axes[i], palette='Set2')
                axes[i].set_title(f"{col}")
                axes[i].set_ylabel("Value")
            
            plt.tight_layout()
            img_path = img_dir / f"{table_name}_boxplot.png"
            plt.savefig(img_path)
            plt.close()
            
            report_content += f"![{table_name} Boxplot](../images/eda/{table_name}_boxplot.png)\n\n"
            
        report_content += "---\n\n"
        
    # 3. 파일 저장
    report_file = report_dir / "01_data_quality_report.md"
    with open(report_file, "w", encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 보고서 생성 완료: {report_file}")

if __name__ == "__main__":
    generate_quality_report()
