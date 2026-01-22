# Olist 데이터 전처리 및 특성 공학 상세 보고서

본 보고서는 Olist 데이터셋의 8개 테이블에 대해 수행된 데이터 정제(Data Cleaning), 이상치 처리(Outlier Handling) 및 특성 공학(Feature Engineering) 작업을 **테이블별로 상세하게** 기록합니다.

---

## 1. Products (상품) 테이블

상품 정보를 표준화하고 분석 가능한 형태로 정제했습니다. 등록되었으나 판매 이력이 없는 상품은 존재하지 않음을 확인했습니다.

### **결측치 처리 (Missing Values)**
*   **카테고리명 (`product_category_name`)**: 610개 결측 발생. 삭제하지 않고 `'unknown'`으로 대체하여 분석 범주에 포함시켰습니다.
*   **텍스트 속성 (`name_lenght`, `description_lenght`, `photos_qty`)**: 610개 결측 발생. 정보 부재를 의미하므로 `0`으로 대체했습니다.
*   **수치형 속성 (`weight_g`, `length_cm`, `height_cm`, `width_cm`)**: 2개 결측 발생. 데이터 분포를 고려하여 해당 컬럼의 **중앙값(Median)**으로 대체했습니다.

### **이상치 및 로직 검증**
*   **미판매 상품 확인**: 전체 32,951개 상품 ID 모두 판매 이력이 있음을 확인했습니다. (No "unsold" products found).

---

## 2. Orders (주문) 테이블

배송 성과 분석의 핵심이 되는 테이블로, 가장 강도 높은 전처리와 특성 공학이 수행되었습니다.

### **데이터 필터링 (Data Filtering)**
*   **주문 상태 (`order_status`)**: 배송 프로세스가 완료된 주문만을 분석하기 위해 `'delivered'` 상태인 데이터만 남기고 나머지는 제외했습니다.
*   **필수 날짜 결측 제거**: 배송 기간 산출에 필수적인 3개 컬럼(`order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`)에 결측값이 있는 행을 제거했습니다.

### **이상치 처리 (Outlier Handling)**
*   **논리적 오류 데이터 제거**: 날짜 계산 결과 음수(-) 값이 나오는 데이터(예: 배송 완료일이 주문일보다 앞서는 경우)를 **총 1,373건** 식별하여 제거했습니다.
    *   대상 컬럼: `total_delivery_time`, `seller_prep_time`, `pure_shipping_time`

### **특성 공학 (Feature Engineering) - 파생변수 생성 상세**

| 구분 | 변수명 | 설명 및 계산 로직 |
| :--- | :--- | :--- |
| **기간 (Time Delta)** | `total_delivery_time` | 주문 접수부터 고객 수령까지 총 기간 (Days) |
| | `seller_prep_time` | 결제 승인부터 물류사 인계까지 걸린 시간 (Days) |
| | `pure_shipping_time` | 물류사 인계부터 고객 수령까지 걸린 시간 (Days) |
| | `delivery_accuracy` | (예상 배송일 - 실제 수령일). 양수면 조기 도착, 음수면 지연. |
| | `estimated_wait_time` | (예상 배송일 - 주문일). 고객에게 안내된 예상 대기 기간. |
| **상태 (Status)** | `is_delayed` | `1` (지연): 실제 수령일 > 예상 배송일<br>`0` (정시): 그 외 |
| **시점 (Date Parts)** | `purchase_hour` | 주문 시각 (0~23) |
| | `purchase_dayofweek` | 주문 요일 (Monday, Tuesday...) |
| | `purchase_month` | 주문 월 (1~12) |
| | `is_weekend` | `True` (주말), `False` (평일) |
| **등급 (Category)** | `delivery_speed_type` | 총 배송 기간(`total_delivery_time`)을 기준으로 4단계 등급화.<br>**[구간 기준 (Bins)]**<br>- **Very Fast**: 0일 ~ 6일 이하<br>- **Normal**: 6일 초과 ~ 15일 이하<br>- **Slow**: 15일 초과 ~ 30일 이하<br>- **Very Slow**: 30일 초과 |

---

## 3. Geolocation (위치 정보) 테이블

### **결측치 및 이상치 처리**
*   **결측치**: 없음 (None).
*   **좌표 이상치 식별**: 브라질 영토 범위를 벗어나는 좌표(Out of bounds) **42건**을 식별했습니다.
    *   설정 경계: Lat(-33.75 ~ 5.27), Lng(-73.98 ~ -34.79)
    *   **조치**: 삭제하지 않고 유지함. (추후 지도 시각화나 정밀 거리 계산 분석 시에만 필터링하도록 주석 처리)

---

## 4. Order Payments (결제) 테이블

### **결측치 및 이상치 처리**
*   **결측치**: 없음 (None).
*   **이상치 탐색 (Boxplot)**:
    *   `payment_sequential`: 분할 결제 또는 바우처 다중 사용으로 인해 최대 **29번**까지 시퀀스가 발생하는 이상치 확인. 실제 데이터로 판단하여 삭제하지 않음.
    *   `payment_value`: 고액 결제 건 다수 존재하나 실제 거래로 간주하여 삭제하지 않음.

---

## 5. Order Items (주문 상품) 테이블

### **데이터 검증**
*   **결측치**: 없음 (None).
*   **금액 무결성 검증**: 상품 가격(`price`) + 배송비(`freight_value`)의 합계가 실제 결제 금액(`payment_value`)과 일치하는지 검증했습니다.
    *   결과: **99.74%**의 주문이 정확히 일치함. 미세한 차이는 바우처 사용 등으로 인한 것으로 보이며 데이터 수정 없이 유지하였습니다.

---

## 6. Sellers (판매자) 테이블

### **전처리 현황**
*   **결측치**: 없음 (None).
*   **조치**: 별도 전처리 없이 원본 데이터를 복사하여 `clean_sellers`로 정의함.

---

## 7. Customers (고객) 테이블

### **전처리 현황**
*   **결측치**: 없음 (None).
*   **조치**: 별도 전처리 없이 원본 데이터를 복사하여 `clean_customers`로 정의함.

---

## 8. Order Reviews (리뷰) 테이블

### **전처리 현황**
*   **결측치**: 리뷰 코멘트(`comment_message`)와 제목(`comment_title`)에 다수의 결측치가 존재하나, 이는 고객이 텍스트 리뷰를 남기지 않은 정상적인 케이스이므로 별도 채우기나 삭제 **없음 (None)**.
*   **조치**: 원본 데이터를 유지하여 `clean_order_reviews`로 정의함.

---

## **종합 결론 및 향후 계획**

1.  **데이터 품질**: 핵심인 `Orders` 테이블의 논리적 오류를 제거하고, `Products` 테이블의 누락 정보를 보완하여 분석 준비를 마쳤습니다. 나머지 테이블들은 데이터 품질이 양호하여 원본을 유지했습니다.
2.  **향후 작업**: 위에서 정제된 테이블들을 `order_items`를 기준으로 병합하여 **Unified Master Table**을 생성할 예정입니다.
