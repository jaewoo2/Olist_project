# Olist 데이터 전처리 및 특성 공학 상세 보고서 (v3)

본 보고서는 Olist 데이터셋의 8개 테이블에 대해 수행된 데이터 정제(Data Cleaning), 이상치 처리(Outlier Handling) 및 특성 공학(Feature Engineering) 작업을 **테이블별로 상세하게** 기록합니다.

**버전:** 3.0 (마스터 테이블 생성 완료)  
**최종 수정일:** 2025-01-19

---

## 📊 전처리 요약

| 테이블 | 주요 처리 | 제거/변환 건수 | 영향도 |
|--------|-----------|----------------|--------|
| Products | 결측치 대체 | 610건 (카테고리), 2건 (수치형) | 낮음 |
| Orders | 상태 필터링 + 이상치 제거 | 2,963건 (non-delivered) + 1,373건 (음수) | 4.4% |
| Geolocation | 좌표 이상치 식별 (유지) | 42건 | 0.004% |
| Payments | 이상치 유지 | 0건 | - |
| Order Items | 변경 없음 | 0건 | - |
| Sellers | 변경 없음 | 0건 | - |
| Customers | 변경 없음 | 0건 | - |
| Order Reviews | **중복 제거 완료** | 551건 (중복 행 제거 -> 1주문 = 1리뷰 ) | 0.6% |

---

## 1. Products (상품) 테이블

상품 정보를 표준화하고 분석 가능한 형태로 정제했습니다.

### **결측치 처리 (Missing Values)**

| 컬럼 | 결측 건수 | 처리 방법 | 근거 |
|------|-----------|-----------|------|
| `product_category_name` | 610건 | `'unknown'` 대체 | 삭제 시 데이터 손실, 분석 범주에 포함 |
| `name_lenght`, `description_lenght`, `photos_qty` | 610건 | `0` 대체 | 정보 부재 = 해당 속성 없음 |
| `weight_g`, `length_cm`, `height_cm`, `width_cm` | 2건 | **중앙값(Median)** 대체 | 아래 설명 참조 |

**수치형 속성에 중앙값을 사용한 이유:**
```
문제: 상품 무게/크기에 극단값 존재 (예: 매우 무거운 상품)
     → 평균(Mean) 사용 시 극단값에 영향받아 왜곡

해결: 중앙값(Median) 사용
     → 극단값에 robust함
     → 데이터 분포의 중심을 더 잘 반영
```

### **데이터 검증**
*   **미판매 상품 확인**: 전체 32,951개 상품 ID 모두 판매 이력이 있음을 확인. (미판매 상품 없음)

---

## 2. Orders (주문) 테이블

배송 성과 분석의 핵심이 되는 테이블로, 가장 강도 높은 전처리와 특성 공학이 수행되었습니다.

### **데이터 필터링 (Data Filtering)**

#### 주문 상태 분포 (원본)

| 상태 | 건수 | 비율 |
|------|------|------|
| **delivered** | 96,478 | **97.0%** |
| shipped | 1,107 | 1.1% |
| canceled | 625 | 0.6% |
| unavailable | 609 | 0.6% |
| invoiced | 314 | 0.3% |
| processing | 301 | 0.3% |
| created | 5 | 0.0% |
| approved | 2 | 0.0% |
| **합계** | **99,441** | **100%** |

#### 필터링 결정

```
결정: 'delivered' 상태만 분석 대상으로 필터링

근거:
1. delivered가 전체의 97.0%로 대다수 차지
2. 배송 완료된 주문만 "배송 성과" 분석 가능
3. 미완료 주문(shipped, processing 등)은 배송 시간 계산 불가
4. 취소/불가(canceled, unavailable)는 별도 분석 필요 시 진행

제외 건수: 2,963건 (3.0%)
→ 분석 영향도 낮음
```

#### 필수 날짜 결측 제거

배송 기간 산출에 필수적인 3개 컬럼에 결측값이 있는 행 제거:
- `order_approved_at`
- `order_delivered_carrier_date`
- `order_delivered_customer_date`

### **이상치 처리 (Outlier Handling)**

#### 논리적 오류 데이터 제거

| 대상 컬럼 | 이상치 정의 | 제거 건수 | 잔여 건수 | 비율 |
|-----------|-------------|-----------|-----------|------|
| `total_delivery_time` | 음수 값 | - | - | - |
| `seller_prep_time` | 음수 값 | - | - | - |
| `pure_shipping_time` | 음수 값 | - | - | - |
| **합계 (중복 제거)** | - | **1,373건** | **95,082건** | **1.4%** |

```
근거:
- 총 배송 시간, 판매자 준비 시간, 순수 운송 시간은 음수 값이 존재할 수 없음
- 음수 = 날짜 데이터 입력 오류 (예: 배송 완료일이 주문일보다 앞섬)
- 1,373건 / 96,455건 = 1.4%로 영향도 낮음
- 해당 건 제거 후 분석 진행
```

### **특성 공학 (Feature Engineering)**

#### 파생변수 생성 상세

| 구분 | 변수명 | 설명 및 계산 로직 |
|------|--------|-------------------|
| **기간** | `total_delivery_time` | 주문 접수 → 고객 수령 (Days) |
| | `seller_prep_time` | 결제 승인 → 물류사 인계 (Days) |
| | `pure_shipping_time` | 물류사 인계 → 고객 수령 (Days) |
| | `delivery_accuracy` | 예상 배송일 - 실제 수령일 (양수=조기, 음수=지연) |
| | `estimated_wait_time` | 예상 배송일 - 주문일 (고객 안내 대기 기간) |
| **상태** | `is_delayed` | 1: 실제 수령일 > 예상 배송일 (지연)<br>0: 그 외 (정시/조기) |
| **시점** | `purchase_hour` | 주문 시각 (0~23) |
| | `purchase_dayofweek` | 주문 요일 (Monday~Sunday) |
| | `purchase_month` | 주문 월 (1~12) |
| | `is_weekend` | True: 주말, False: 평일 |
| **등급** | `delivery_speed_type` | 배송 속도 4단계 분류 (아래 상세) |

#### delivery_speed_type 구간 설정 근거

**total_delivery_time 기술통계:**
```
count    95,082건
mean     12.09일
std       9.55일
min       0일
25%       6일    ← Very Fast 경계
50%      10일
75%      15일    ← Normal/Slow 경계
max     209일
```

**구간 설정:**

| 등급 | 구간 | 근거 | 해석 |
|------|------|------|------|
| **Very Fast** | 0 ~ 6일 | 하위 25% (1사분위수) | 상위 25% 빠른 배송 |
| **Normal** | 6 ~ 15일 | 25% ~ 75% (IQR) | 중간 50% |
| **Slow** | 15 ~ 30일 | 75% 초과 | 평균보다 느림 |
| **Very Slow** | 30일 초과 | 극단값 | 심각한 지연 |

```python
# 실제 적용 코드
bins = [-1, 6, 15, 30, orders['total_delivery_time'].max()]
labels = ['Very Fast', 'Normal', 'Slow', 'Very Slow']
```

---

## 3. Geolocation (위치 정보) 테이블

### **데이터 현황**

| 항목 | 값 |
|------|-----|
| 전체 건수 | 1,000,163건 |
| 결측치 | 0건 |

### **좌표 이상치 식별**

**브라질 영토 경계:**
```
위도 (Latitude): -33.75 ~ 5.27
경도 (Longitude): -73.98 ~ -34.79
```

**이상치 현황:**

| 구분 | 건수 | 비율 |
|------|------|------|
| 정상 좌표 | 1,000,121건 | 99.996% |
| **경계 이탈** | **42건** | **0.004%** |

```
결정: 삭제하지 않고 유지

근거:
1. 42건 / 1,000,163건 = 0.004%로 극히 미미
2. 현재 분석에서 정밀 좌표 계산 불필요
3. 추후 지도 시각화나 거리 계산 시 해당 건만 필터링

※ 필터링 필요 시:
   df = df[(df['geolocation_lat'].between(-33.75, 5.27)) & 
           (df['geolocation_lng'].between(-73.98, -34.79))]
```

---

## 4. Order Payments (결제) 테이블

### **데이터 현황**
- **결측치**: 없음

### **이상치 탐색 및 판단**

#### payment_sequential (분할 결제 횟수)

| 항목 | 값 |
|------|-----|
| 최대값 | 29회 |
| 의심 사항 | 1건 주문에 29회 분할 결제? |

**검증 과정:**
```
1. 29회 분할 결제된 주문 ID 확인
2. 해당 주문의 payment_type 분석
3. 결과: 29회 모두 'voucher' (바우처/쿠폰)

4. Top 10 분할 결제 주문 시각화 (hue=payment_type)
5. 결과: voucher가 90% 이상 차지
```

**결론:**
```
결정: 이상치로 판단하지 않고 유지

근거:
- 다중 바우처/쿠폰 사용으로 인한 정상적인 분할 결제
- 브라질 이커머스에서 프로모션 쿠폰 다중 적용 흔함
- 실제 비즈니스 로직 반영한 데이터
```

#### payment_value (결제 금액)

- 고액 결제 건 다수 존재
- 실제 거래로 간주하여 유지 (이상치 처리 없음)

---

## 5. Order Items (주문 상품) 테이블

### **데이터 현황**
- **결측치**: 없음

### **금액 무결성 검증**

| 검증 내용 | 결과 |
|-----------|------|
| price + freight_value = payment_value | **99.74% 일치** |

```
불일치 원인 (0.26%):
- 최종 결론
이것은 단순히 할인이 적용된 것이 아니라, **"브라질 커머스 특유의 신용카드 할부 수수료(Interest)"**가 결제 금액에 포함되었기 때문에 발생하는 현상입니다.

가정(Assumption): 바우처 할인 때문에 결제액이 적을 것이다. (X)
사실(Fact): 할부 횟수가 많은 신용카드 결제에서 할부 이자가 붙어 결제 금액이 실제 상품가보다 커진 것이다. (O)

결정: 데이터 수정 없이 유지
```

---

## 6. Sellers (판매자) 테이블

### **데이터 현황**
- **결측치**: 없음
- **조치**: 별도 전처리 없이 원본 유지

---

## 7. Customers (고객) 테이블

### **데이터 현황**
- **결측치**: 없음
- **조치**: 별도 전처리 없이 원본 유지

---

## 8. Order Reviews (리뷰) 테이블

### **데이터 현황**

| 컬럼 | 결측 상태 | 조치 |
|------|-----------|------|
| `review_score` | 없음 | 유지 |
| `review_comment_title` | 다수 결측 | 유지 (텍스트 미작성 = 정상) |
| `review_comment_message` | 다수 결측 | 유지 (텍스트 미작성 = 정상) |

### **✅ 중복 리뷰 처리 (완료)**

#### 현상 및 원인

```
현상: 동일 order_id에 리뷰가 2개 이상 존재하는 케이스 발견
원인: 시스템 오류로 판단 (정상적으로 1주문 = 1리뷰)
```

**중복 현황 (처리 전):**

| 주문당 리뷰 수 | order_id 수 | 비고 |
|----------------|-------------|------|
| 1개 | 98,126개 | 정상 |
| 2개 | 543개 | 중복 |
| 3개 | 4개 | 중복 |
| **합계** | **98,673개** | - |

#### 처리 방법

```
방법: order_id 기준 중복 제거, 최신 리뷰(review_creation_date 기준)만 유지
```

```python
# 1. 날짜 기준 내림차순 정렬 (최신이 위로)
order_reviews_sorted = order_reviews.sort_values(by='review_creation_date', ascending=False)

# 2. order_id 기준 중복 제거, 첫 번째(가장 최신)만 유지
order_reviews_cleaned = order_reviews_sorted.drop_duplicates(subset='order_id', keep='first')
```

#### 처리 결과

| 구분 | 건수 |
|------|------|
| 처리 전 (order_reviews) | 99,224건 |
| 처리 후 (order_reviews_cleaned) | 98,673건 |
| **제거된 중복 행** | **551건** |

```
제거 건수 검산:
- 2개 리뷰 주문: 543개 × 1개 제거 = 543건
- 3개 리뷰 주문: 4개 × 2개 제거 = 8건
- 합계: 543 + 8 = 551건 ✅
```

**중복 현황 (처리 후):**

| 주문당 리뷰 수 | order_id 수 |
|----------------|-------------|
| 1개 | 98,673개 |

→ 모든 주문이 1개의 리뷰만 보유 ✅

#### 리뷰-주문 매칭 현황 (master_orders 생성 시)

| 구분 | 건수 | 설명 |
|------|------|------|
| 주문 O + 리뷰 O | 94,443건 | 정상 연결 |
| 주문 O + 리뷰 X | 639건 | 리뷰 미작성 (정상) |
| 주문 X + 리뷰 O | 4,230건 | non-delivered 주문의 리뷰 (master에서 제외) |

```
리뷰 응답률: 94,443 / 95,082 = 99.3%
→ 매우 높은 리뷰 응답률
```

---

## 9. 마스터 테이블 생성 ✅ NEW

### **생성 목적**

```
문제:
- 분석 시마다 여러 테이블 조인 필요
- 팀원마다 조인 로직 다르면 결과 불일치
- 1:N 관계 조인 시 데이터 뻥튀기 위험

해결:
- 검증된 마스터 테이블 1번 생성
- 전 팀원이 동일한 데이터로 분석
- 분석 단위별 집계 완료 상태로 제공
```

### **테이블 관계 주의사항**

```
1:N 관계 조인 시 데이터 뻥튀기 발생!

예시: 주문 A에 상품 3개
- 단순 조인 시 주문 A가 3행으로 늘어남
- AVG(review_score) 계산 시 리뷰가 3번 카운트됨 (왜곡!)

해결: 먼저 집계 → 그 다음 조인
```

---

### **9-1. master_orders**

**용도:** 주문/배송/리뷰/고객 경험 분석  
**단위:** 1행 = 1주문 (중복 없음)  
**건수:** 95,082건

#### 생성 로직

```
1. order_items → 주문 단위 집계 (item_count, total_price 등)
2. order_payments → 주문 단위 집계 (payment_total, main_payment_type 등)
3. clean_orders + 집계 테이블들 + reviews_unique + customers 조인
```

#### 컬럼 구성

| 출처 | 컬럼 |
|------|------|
| orders (원본) | order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date |
| orders (파생) | total_delivery_time, seller_prep_time, pure_shipping_time, delivery_accuracy, estimated_wait_time, is_delayed, purchase_hour, purchase_dayofweek, purchase_month, is_weekend, delivery_speed_type |
| order_items_agg | item_count, seller_count, total_price, total_freight |
| payments_agg | payment_count, payment_total, max_installments, main_payment_type |
| reviews_unique | review_score, review_comment_message |
| customers | customer_unique_id, customer_city, customer_state |

#### 검증 결과

| 검증 항목 | 결과 |
|-----------|------|
| 행 수 일치 (clean_orders = master_orders) | ✅ 95,082 = 95,082 |
| order_id 중복 | ✅ 0건 |
| 금액 합계 일치 | ✅ 일치 |
| 리뷰 연결 | ✅ 94,443건 (639건 미작성) |

---

### **9-2. master_sellers**

**용도:** 판매자 성과 분석  
**단위:** 1행 = 1판매자 (중복 없음)  
**건수:** 3,095건

#### 생성 로직

```
1. order_items → (order_id, seller_id) 단위 중간 집계
2. 중간 집계 + orders + reviews_unique 조인
3. seller_id 단위 최종 집계
4. sellers 정보 조인
```

#### 컬럼 구성

| 구분 | 컬럼 |
|------|------|
| 식별 | seller_id, seller_city, seller_state |
| 주문/매출 | total_orders, total_items, total_revenue, total_freight, total_gmv |
| 리뷰 | avg_review_score, review_count, five_star_count, one_star_count, five_star_rate, one_star_rate |
| 배송 | avg_delivery_days, delay_count, delay_rate |
| 기간 | first_order_date, last_order_date |

#### 파생변수 상세

| 변수명 | 계산식 | 의미 | 분석 용도 |
|--------|--------|------|-----------|
| `total_gmv` | total_revenue + total_freight | 판매자의 총 거래액. 고객이 실제 지불한 금액(상품가격 + 배송비)의 합계 | 판매자 매출 순위, 파레토 분석 (상위 20%가 전체 매출의 몇 % 차지하는지) |
| `five_star_rate` | five_star_count / review_count × 100 | 해당 판매자 주문 중 5점 리뷰를 받은 비율 (%). 높을수록 만족 고객 多 | 우수 판매자 식별, 판매자 품질 평가 |
| `one_star_rate` | one_star_count / review_count × 100 | 해당 판매자 주문 중 1점 리뷰를 받은 비율 (%). 높을수록 불만족 고객 多 | 문제 판매자 식별, 리스크 관리 대상 선정 |
| `delay_rate` | delay_count / total_orders × 100 | 해당 판매자 주문 중 배송 지연이 발생한 비율 (%). 고객이 예상 배송일보다 늦게 받은 비율 | 배송 품질 평가, 지연-리뷰 관계 분석 |

**참고사항:**

| 항목 | 설명 |
|------|------|
| GMV | Gross Merchandise Value. 플랫폼에서 거래된 총 금액을 의미 |
| delay_rate 해석 | 판매자 책임 + 물류사 책임 + 외부 요인이 혼합된 최종 결과. 순수 판매자 책임만 측정한 것은 아님 |
| 비율 단위 | 모든 rate 변수는 % 단위 (0~100) |

#### 검증 결과

| 검증 항목 | 결과 |
|-----------|------|
| seller_id 중복 | ✅ 0건 |
| GMV 합계 일치 | ✅ 일치 |

---

## 📋 최종 데이터 현황

### 처리 전후 비교

| 테이블 | 원본 건수 | 처리 후 건수 | 변화 |
|--------|-----------|--------------|------|
| Products | 32,951 | 32,951 | - |
| Orders | 99,441 | **95,082** | -4,359 (-4.4%) |
| Order Items | 112,650 | 112,650 | - |
| Order Payments | 103,886 | 103,886 | - |
| Order Reviews | 99,224 | **98,673** (중복 제거) | -551 (-0.6%) |
| Customers | 99,441 | 99,441 | - |
| Sellers | 3,095 | 3,095 | - |
| Geolocation | 1,000,163 | 1,000,163 | - |

### Orders 필터링 상세

```
원본:                  99,441건
  ↓ non-delivered 제외  -2,963건 (3.0%)
  ↓ 날짜 결측 제거      -23건 (0.0%)
  ↓ 음수 값 제거        -1,373건 (1.4%)
최종:                  95,082건
```

### 마스터 테이블 현황

| 테이블 | 건수 | 단위 | 용도 |
|--------|------|------|------|
| master_orders | 95,082건 | 1행 = 1주문 | 주문/배송/리뷰/고객 분석 |
| master_sellers | 3,095건 | 1행 = 1판매자 | 판매자 성과 분석 |

---

## 📁 최종 산출물

```
📁 데이터
│
├── 📂 raw/ (원본)
│   └── (Kaggle 원본 9개 테이블)
│
├── 📂 cleaned/ (정제 완료)
│   ├── clean_orders.csv (파생변수 포함, 95,082건)
│   ├── clean_order_items.csv
│   ├── clean_order_payments.csv
│   ├── clean_order_reviews.csv
│   ├── clean_order_reviews_unique.csv (중복 제거, 98,673건)
│   ├── clean_customers.csv
│   ├── clean_sellers.csv
│   ├── clean_products.csv
│   └── clean_geolocation.csv
│
└── 📂 master/ (분석용)
    ├── master_orders.csv (95,082건)
    └── master_sellers.csv (3,095건)
```

---

## 🔜 다음 단계

1. **EDA (탐색적 데이터 분석)**
   - master_orders: 리뷰 분포, 배송 vs 리뷰, 지역 패턴, 시간 패턴
   - master_sellers: 파레토 분석, 리뷰-매출 관계, 판매자 세그먼트

2. **문제 규정**
   - EDA 발견 + 도메인 지식 결합
   - 비즈니스 임팩트 판단

3. **가설 검증**
   - 통계적 검정 수행 (Mann-Whitney U, Kruskal-Wallis 등)
   - p-value + 효과 크기 확인

---

**문서 버전:** 3.0  
**작성일:** 2025-01-19  
**변경 이력:**
- v1.0: 초기 작성
- v2.0: 전처리 판단 근거 보완, 수치/비율 추가
- v3.0: 리뷰 중복 제거 완료, 마스터 테이블 생성 추가
