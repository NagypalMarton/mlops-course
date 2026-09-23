# Data Dictionary: Hotel Booking Demand

This document details all 32 columns present in the raw `hotel_bookings.csv` file, including data types, valid ranges, semantic descriptions, and observed data quality considerations.

| # | Column Name | Data Type | Units / Range | Null / Sentinel Values | Description & Modeling Considerations |
|---|---|---|---|---|---|
| 1 | `hotel` | Categorical | `Resort Hotel`, `City Hotel` | None | Operational property type. Primary pivot for spatial/domain drift in HW5. |
| 2 | `is_canceled` | Binary | 0, 1 | None | **Target Variable.** 0 = Checked-Out (arrived), 1 = Canceled or No-Show. |
| 3 | `lead_time` | Integer | 0 – 737 days | None | Number of days elapsed between booking date and arrival date. Heavy right-skew. |
| 4 | `arrival_date_year` | Integer | 2015, 2016, 2017 | None | Calendar year of scheduled arrival. Useful for temporal train/test splits. |
| 5 | `arrival_date_month` | Categorical | January – December | None | Calendar month of arrival. Encodes seasonality. |
| 6 | `arrival_date_week_number` | Integer | 1 – 53 | None | ISO week number of arrival. |
| 7 | `arrival_date_day_of_month` | Integer | 1 – 31 | None | Day of month of arrival. |
| 8 | `stays_in_weekend_nights` | Integer | 0 – 19 nights | None | Count of weekend nights (Saturday/Sunday) booked. |
| 9 | `stays_in_week_nights` | Integer | 0 – 50 nights | None | Count of weekday nights (Monday–Friday) booked. |
| 10 | `adults` | Integer | 0 – 55 | None | Number of declared adults. *Quirk: 180 rows show 0 adults, 0 children, 0 babies.* |
| 11 | `children` | Float / Int | 0 – 10 | 4 rows NaN | Number of declared children. Missing values should be imputed to 0. |
| 12 | `babies` | Integer | 0 – 10 | None | Number of declared infants. |
| 13 | `meal` | Categorical | `BB`, `HB`, `FB`, `SC`, `Undefined` | Sentinel `Undefined` | Board type booked. `SC` (self-catering) and `Undefined` denote no meal plan. |
| 14 | `country` | Categorical | ISO 3166-1 alpha-3 | 488 rows `NULL` / NaN | Nationality of primary guest. High cardinality (177 codes; top: PRT, GBR, FRA, ESP). |
| 15 | `market_segment` | Categorical | 8 categories | Sentinel `Undefined` | Market segment designation (`Direct`, `Online TA`, `Offline TA/TO`, `Corporate`, etc.). |
| 16 | `distribution_channel` | Categorical | 5 categories | Sentinel `Undefined` | Booking distribution channel (`Direct`, `TA/TO`, `Corporate`, `GDS`, `Undefined`). |
| 17 | `is_repeated_guest` | Binary | 0, 1 | None | 1 indicates previous booking on record for this customer. |
| 18 | `previous_cancellations` | Integer | 0 – 26 | None | Historical booking cancellations associated with this guest profile. |
| 19 | `previous_bookings_not_canceled` | Integer | 0 – 72 | None | Historical completed bookings not canceled prior to this reservation. |
| 20 | `reserved_room_type` | Categorical | Codes `A` – `L` | None | Room code requested at booking time. |
| 21 | `assigned_room_type` | Categorical | Codes `A` – `P` | None | Room code assigned at check-in. Mismatches with requested room indicate operational changes. |
| 22 | `booking_changes` | Integer | 0 – 21 | None | Total amendments made between booking creation and check-in/cancellation. |
| 23 | `deposit_type` | Categorical | `No Deposit`, `Non Refund`, `Refundable` | None | Payment guarantee terms. |
| 24 | `agent` | Categorical / ID | 1 – 535 | 16,340 rows NaN (13.7%) | ID of travel agency that made the booking. NaN indicates direct individual booking. |
| 25 | `company` | Categorical / ID | 6 – 543 | 112,593 rows NaN (94.3%) | Corporate ID responsible for booking/payment. NaN denotes non-corporate reservation. |
| 26 | `days_in_waiting_list` | Integer | 0 – 391 days | None | Days the reservation remained in waiting list before customer confirmation. |
| 27 | `customer_type` | Categorical | 4 categories | None | Booking type: `Transient`, `Transient-Party`, `Contract`, `Group`. |
| 28 | `adr` | Float | -6.38 – 5400.0 EUR | None | Average Daily Rate (total room revenue divided by total nights). *Contains negative values and an outlier of 5400 EUR.* |
| 29 | `required_car_parking_spaces` | Integer | 0 – 8 | None | Number of parking spots requested. Strong negative correlation with cancellation. |
| 30 | `total_of_special_requests` | Integer | 0 – 5 | None | Count of additional requests made by guest (e.g., high floor, twin beds). |
| 31 | `reservation_status` | Categorical | `Check-Out`, `Canceled`, `No-Show` | None | **DATA LEAKAGE.** Post-event state. Must be strictly excluded from model feature inputs. |
| 32 | `reservation_status_date` | Date / String | YYYY-MM-DD | None | **DATA LEAKAGE.** Date when last status modification occurred. Must be excluded from feature inputs. |

---

### Data Cleaning and Preprocessing Recommendations

1. **Feature Exclusion (Leakage Prevention):**
   * Drop `reservation_status` and `reservation_status_date` prior to dataset splitting and preprocessing.
2. **Invalid Rows Filtering:**
   * Filter out rows where `adults + children + babies == 0` (180 total records).
   * Filter or clip negative `adr` values (`adr < 0`) and the extreme isolated outlier (`adr == 5400`).
3. **Missing Value Imputation:**
   * `children`: Replace 4 missing values with `0`.
   * `country`: Impute missing values with sentinel `'Unknown'` or mode.
   * `agent` and `company`: Do not treat missingness as invalid data; impute NaNs as `0` to represent direct/individual non-corporate bookings.
4. **Encoding Strategies:**
   * Group low-frequency `country` categories below a 1% threshold into an `'Other'` bucket to prevent high dimensionality.
   * Apply One-Hot Encoding to low-cardinality nominal features (`hotel`, `meal`, `market_segment`, `distribution_channel`, `deposit_type`, `customer_type`).