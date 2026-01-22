"""
Olist 데이터 로드 모듈
8개 테이블을 읽고 기본 정보를 확인하는 함수들
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


# 데이터 경로 설정 (수정됨!)
# __file__ = /project2/src/data_loader.py
# .parent = /project2/src
# .parent.parent = /project2
# .parent.parent / "data" / "raw" = /project2/data/raw
DATA_PATH = Path(__file__).parent.parent / "data" / "processed_v2"


def load_all_tables(data_path: Path = DATA_PATH, verbose: bool = True) -> Dict[str, pd.DataFrame]:
    """
    Olist의 모든 테이블을 한번에 로드
    
    Parameters:
    -----------
    data_path : Path
        CSV 파일이 있는 경로
    verbose : bool
        로딩 정보 출력 여부
        
    Returns:
    --------
    Dict[str, pd.DataFrame]
        테이블명을 key로 하는 딕셔너리
    """
    
    tables = {}
    
    # 테이블 파일명 정의
    table_files = {
        'customers': 'olist_customers_dataset.csv',
        'geolocation': 'olist_geolocation_dataset.csv',
        'order_items': 'olist_order_items_dataset.csv',
        'order_payments': 'olist_order_payments_dataset.csv',
        'order_reviews': 'olist_order_reviews_dataset.csv',
        'orders': 'olist_orders_dataset.csv',
        'products': 'olist_products_dataset.csv',
        'sellers': 'olist_sellers_dataset.csv',
        'category_translation': 'product_category_name_translation.csv'
    }
    
    if verbose:
        print("🚀 Olist 데이터 로딩 중...\n")
    
    for table_name, file_name in table_files.items():
        file_path = data_path / file_name
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            tables[table_name] = df
            
            if verbose:
                print(f"✅ {table_name:20s}: {df.shape[0]:>7,d} rows × {df.shape[1]:>2d} columns")
                
        except FileNotFoundError:
            if verbose:
                print(f"❌ {table_name:20s}: 파일을 찾을 수 없습니다 ({file_name})")
            tables[table_name] = None
    
    if verbose:
        print("\n" + "="*60)
        total_rows = sum(df.shape[0] for df in tables.values() if df is not None)
        print(f"📊 전체 데이터: {total_rows:,d} rows")
        print("="*60 + "\n")
    
    return tables


def load_orders() -> pd.DataFrame:
    """주문 데이터 로드"""
    return pd.read_csv(DATA_PATH / 'olist_orders_dataset.csv', encoding='utf-8')


def load_order_items() -> pd.DataFrame:
    """주문 상품 데이터 로드"""
    return pd.read_csv(DATA_PATH / 'olist_order_items_dataset.csv', encoding='utf-8')


def load_order_payments() -> pd.DataFrame:
    """주문 결제 데이터 로드"""
    return pd.read_csv(DATA_PATH / 'olist_order_payments_dataset.csv', encoding='utf-8')


def load_order_reviews() -> pd.DataFrame:
    """주문 리뷰 데이터 로드"""
    return pd.read_csv(DATA_PATH / 'olist_order_reviews_dataset.csv', encoding='utf-8')


def load_customers() -> pd.DataFrame:
    """고객 데이터 로드"""
    return pd.read_csv(DATA_PATH / 'olist_customers_dataset.csv', encoding='utf-8')


def load_sellers() -> pd.DataFrame:
    """판매자 데이터 로드"""
    return pd.read_csv(DATA_PATH / 'olist_sellers_dataset.csv', encoding='utf-8')


def load_products() -> pd.DataFrame:
    """상품 데이터 로드"""
    return pd.read_csv(DATA_PATH / 'olist_products_dataset.csv', encoding='utf-8')


def load_geolocation() -> pd.DataFrame:
    """지리 좌표 데이터 로드"""
    return pd.read_csv(DATA_PATH / 'olist_geolocation_dataset.csv', encoding='utf-8')


def load_category_translation() -> pd.DataFrame:
    """카테고리 번역 데이터 로드"""
    return pd.read_csv(DATA_PATH / 'product_category_name_translation.csv', encoding='utf-8')


def get_table_info(df: pd.DataFrame, table_name: str = "DataFrame") -> None:
    """
    데이터프레임의 기본 정보 출력
    
    Parameters:
    -----------
    df : pd.DataFrame
        확인할 데이터프레임
    table_name : str
        테이블 이름
    """
    
    print(f"\n{'='*60}")
    print(f"📊 {table_name}")
    print(f"{'='*60}")
    
    print(f"\n✅ Shape: {df.shape[0]:,d} rows × {df.shape[1]:,d} columns")
    
    print(f"\n📋 Columns:")
    for i, col in enumerate(df.columns, 1):
        print(f"   {i:2d}. {col} ({df[col].dtype})")
    
    print(f"\n🔍 Missing Values:")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("   ✅ 결측치 없음!")
    else:
        missing_pct = (missing / len(df) * 100).round(2)
        for col in missing[missing > 0].index:
            print(f"   {col:40s}: {missing[col]:>7,d} ({missing_pct[col]:>5.2f}%)")
    
    print(f"\n📈 Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print()


def check_relationships(tables: Dict[str, pd.DataFrame]) -> None:
    """
    테이블 간 관계 검증 (Foreign Key 체크)
    
    Parameters:
    -----------
    tables : Dict[str, pd.DataFrame]
        로드된 테이블 딕셔너리
    """
    
    print("\n" + "="*60)
    print("🔗 테이블 관계 검증")
    print("="*60 + "\n")
    
    checks = [
        {
            'name': 'orders → customers',
            'parent': 'orders',
            'child': 'customers',
            'key': 'customer_id'
        },
        {
            'name': 'order_items → orders',
            'parent': 'order_items',
            'child': 'orders',
            'key': 'order_id'
        },
        {
            'name': 'order_items → products',
            'parent': 'order_items',
            'child': 'products',
            'key': 'product_id'
        },
        {
            'name': 'order_items → sellers',
            'parent': 'order_items',
            'child': 'sellers',
            'key': 'seller_id'
        },
        {
            'name': 'order_payments → orders',
            'parent': 'order_payments',
            'child': 'orders',
            'key': 'order_id'
        },
        {
            'name': 'order_reviews → orders',
            'parent': 'order_reviews',
            'child': 'orders',
            'key': 'order_id'
        },
    ]
    
    for check in checks:
        parent_df = tables[check['parent']]
        child_df = tables[check['child']]
        key = check['key']
        
        # Foreign Key 검증
        parent_keys = set(parent_df[key].dropna())
        child_keys = set(child_df[key].dropna())
        
        # 부모에는 있는데 자식에는 없는 키
        orphans = parent_keys - child_keys
        
        if len(orphans) == 0:
            print(f"✅ {check['name']:30s}: 일치 ({len(parent_keys):,d} keys)")
        else:
            orphan_pct = len(orphans) / len(parent_keys) * 100
            print(f"⚠️  {check['name']:30s}: {len(orphans):,d} orphans ({orphan_pct:.2f}%)")
    
    print()


if __name__ == "__main__":
    # 테스트 실행
    print("데이터 로더 테스트...\n")
    
    tables = load_all_tables()
    
    # 주요 테이블 정보 출력
    if tables['orders'] is not None:
        get_table_info(tables['orders'], "Orders")
    
    if tables['order_items'] is not None:
        get_table_info(tables['order_items'], "Order Items")
    
    # 관계 검증
    if all(tables[t] is not None for t in ['orders', 'customers', 'order_items']):
        check_relationships(tables)