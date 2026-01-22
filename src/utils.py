"""
유틸리티 함수 모듈
공통으로 사용하는 헬퍼 함수들
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import platform
import warnings
warnings.filterwarnings('ignore')



def set_korean_font():
    """
    시각화 한글 깨짐 방지를 위한 폰트 설정
    Windows: Malgun Gothic, Mac: AppleGothic
    """
    system_os = platform.system()
    
    if system_os == 'Windows':
        plt.rc('font', family='Malgun Gothic')
    elif system_os == 'Darwin': # Mac
        plt.rc('font', family='AppleGothic')
    
    # 마이너스 기호 깨짐 방지
    plt.rc('axes', unicode_minus=False)
    
    print(f"✅ 한글 폰트 설정 완료 ({system_os})")


def check_data_quality(df: pd.DataFrame, name: str = "DataFrame") -> Dict:
    """
    데이터 품질 체크
    
    Parameters:
    -----------
    df : pd.DataFrame
        체크할 데이터프레임
    name : str
        데이터프레임 이름
        
    Returns:
    --------
    Dict
        품질 체크 결과
    """
    
    quality_report = {
        'name': name,
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'duplicates': df.duplicated().sum(),
        'missing_values': {},
        'data_types': df.dtypes.to_dict()
    }
    
    # 결측치 확인
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            missing_pct = (missing_count / len(df)) * 100
            quality_report['missing_values'][col] = {
                'count': missing_count,
                'percentage': round(missing_pct, 2)
            }
    
    return quality_report


def print_quality_report(quality_report: Dict) -> None:
    """
    데이터 품질 리포트 출력
    
    Parameters:
    -----------
    quality_report : Dict
        check_data_quality()의 결과
    """
    
    print(f"\n{'='*60}")
    print(f"📊 데이터 품질 리포트: {quality_report['name']}")
    print(f"{'='*60}\n")
    
    print(f"✅ Total Rows: {quality_report['total_rows']:,d}")
    print(f"✅ Total Columns: {quality_report['total_columns']:,d}")
    print(f"✅ Duplicates: {quality_report['duplicates']:,d}")
    
    if quality_report['missing_values']:
        print(f"\n⚠️  Missing Values:")
        for col, info in quality_report['missing_values'].items():
            print(f"   {col:40s}: {info['count']:>7,d} ({info['percentage']:>5.2f}%)")
    else:
        print(f"\n✅ No Missing Values!")
    
    print()


def detect_outliers_iqr(df: pd.DataFrame, column: str, factor: float = 1.5) -> pd.Series:
    """
    IQR 방법으로 이상치 탐지
    
    Parameters:
    -----------
    df : pd.DataFrame
        데이터프레임
    column : str
        체크할 컬럼명
    factor : float
        IQR 배수 (기본 1.5)
        
    Returns:
    --------
    pd.Series
        이상치 여부 (True/False)
    """
    
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - (factor * IQR)
    upper_bound = Q3 + (factor * IQR)
    
    outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
    
    return outliers


def calculate_summary_stats(df: pd.DataFrame, column: str) -> Dict:
    """
    기술 통계량 계산
    
    Parameters:
    -----------
    df : pd.DataFrame
        데이터프레임
    column : str
        컬럼명
        
    Returns:
    --------
    Dict
        통계량 딕셔너리
    """
    
    stats = {
        'count': df[column].count(),
        'mean': df[column].mean(),
        'std': df[column].std(),
        'min': df[column].min(),
        '25%': df[column].quantile(0.25),
        'median': df[column].median(),
        '75%': df[column].quantile(0.75),
        'max': df[column].max(),
    }
    
    return stats


def convert_to_datetime(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    컬럼들을 datetime 타입으로 변환
    
    Parameters:
    -----------
    df : pd.DataFrame
        데이터프레임
    columns : List[str]
        변환할 컬럼 리스트
        
    Returns:
    --------
    pd.DataFrame
        변환된 데이터프레임
    """
    
    df = df.copy()
    
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            print(f"✅ {col} → datetime 변환 완료")
    
    return df


def calculate_time_diff(df: pd.DataFrame, 
                        start_col: str, 
                        end_col: str, 
                        unit: str = 'days',
                        new_col_name: str = None) -> pd.DataFrame:
    """
    두 날짜 컬럼 간 시간 차이 계산
    
    Parameters:
    -----------
    df : pd.DataFrame
        데이터프레임
    start_col : str
        시작 날짜 컬럼
    end_col : str
        종료 날짜 컬럼
    unit : str
        단위 ('days', 'hours', 'minutes')
    new_col_name : str
        새 컬럼명 (None이면 자동 생성)
        
    Returns:
    --------
    pd.DataFrame
        시간 차이 컬럼이 추가된 데이터프레임
    """
    
    df = df.copy()
    
    if new_col_name is None:
        new_col_name = f"{end_col.split('_')[0]}_to_{start_col.split('_')[0]}_{unit}"
    
    time_diff = df[end_col] - df[start_col]
    
    if unit == 'days':
        df[new_col_name] = time_diff.dt.days
    elif unit == 'hours':
        df[new_col_name] = time_diff.dt.total_seconds() / 3600
    elif unit == 'minutes':
        df[new_col_name] = time_diff.dt.total_seconds() / 60
    else:
        raise ValueError(f"지원하지 않는 단위: {unit}")
    
    return df


def categorize_numeric(series: pd.Series, 
                       bins: List[float], 
                       labels: List[str] = None) -> pd.Series:
    """
    연속형 변수를 범주형으로 변환
    
    Parameters:
    -----------
    series : pd.Series
        연속형 시리즈
    bins : List[float]
        구간 경계값
    labels : List[str]
        범주 레이블 (None이면 자동 생성)
        
    Returns:
    --------
    pd.Series
        범주형 시리즈
    """
    
    if labels is None:
        labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)]
    
    return pd.cut(series, bins=bins, labels=labels, include_lowest=True)


def get_top_n(df: pd.DataFrame, 
              column: str, 
              n: int = 10, 
              ascending: bool = False) -> pd.DataFrame:
    """
    컬럼 기준 상위 N개 행 추출
    
    Parameters:
    -----------
    df : pd.DataFrame
        데이터프레임
    column : str
        정렬 기준 컬럼
    n : int
        추출할 개수
    ascending : bool
        오름차순 여부
        
    Returns:
    --------
    pd.DataFrame
        상위 N개 행
    """
    
    return df.nlargest(n, column) if not ascending else df.nsmallest(n, column)


def safe_divide(numerator: pd.Series, denominator: pd.Series, fill_value: float = 0) -> pd.Series:
    """
    0으로 나누기 안전하게 처리
    
    Parameters:
    -----------
    numerator : pd.Series
        분자
    denominator : pd.Series
        분모
    fill_value : float
        0 나누기 시 채울 값
        
    Returns:
    --------
    pd.Series
        나눗셈 결과
    """
    
    result = numerator / denominator
    result = result.replace([np.inf, -np.inf], fill_value)
    result = result.fillna(fill_value)
    
    return result


def percentage(part: float, total: float, decimals: int = 2) -> float:
    """
    퍼센트 계산
    
    Parameters:
    -----------
    part : float
        부분
    total : float
        전체
    decimals : int
        소수점 자리수
        
    Returns:
    --------
    float
        퍼센트 값
    """
    
    if total == 0:
        return 0.0
    
    return round((part / total) * 100, decimals)


if __name__ == "__main__":
    # 테스트 예제
    print("유틸리티 함수 테스트...\n")
    
    # 샘플 데이터 생성
    sample_df = pd.DataFrame({
        'value': [1, 2, 3, 100, 5, 6, 7, 8, 9, 10],
        'category': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'A', 'B', 'C']
    })
    
    # 데이터 품질 체크
    quality = check_data_quality(sample_df, "Sample Data")
    print_quality_report(quality)
    
    # 이상치 탐지
    outliers = detect_outliers_iqr(sample_df, 'value')
    print(f"이상치 개수: {outliers.sum()}")
    print(f"이상치 인덱스: {sample_df[outliers].index.tolist()}")
