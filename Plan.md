# Plan.md

## 진행 방식
이 저장소는 `.claude/skills/tdd-skill`의 PLAN → RED → GREEN → REVIEW 체크포인트 워크플로우를 따른다.
계획 승인 전에는 테스트/프로덕션 코드를 작성하지 않는다.

## 전체 로드맵 (참고용 — 슬라이스마다 이 파일을 갱신하고 재승인 받음)
1. **시료(Sample) 등록/조회 — JSON 영속성** ← 이번 슬라이스
2. 시료 조회/검색 컨트롤러+뷰, 메인 메뉴 스켈레톤 (MVC)
3. 주문(Order) 예약 — RESERVED 생성, 주문번호 채번
4. 주문 승인/거절 — 재고 확인, CONFIRMED/PRODUCING/REJECTED 전이
5. 생산 라인 — FIFO 큐, 실 생산량/총 생산 시간 계산
6. 모니터링 — 상태별 집계, 재고 상태 판정
7. 출고 처리 — CONFIRMED→RELEASED

---

## 이번 슬라이스: 시료 등록/조회 (JSON 영속성)

### 검증할 동작 (Behavior)
- 새 시료를 생성(create)하면 JSON 파일에 저장되고, 이후 조회(get_all)하면 나타난다.
- 이미 존재하는 시료 ID로 생성을 시도하면 거부된다.
- 존재하지 않는 시료 ID로 조회하면 `None`을 반환한다.

### 작성할 테스트
`tests/repository/test_sample_repository.py`

- `test_create_persists_sample_to_json_file`
  - `tmp_path`에 임시 JSON 파일 경로를 만들고, 그 경로로 `SampleRepository` 인스턴스를 생성
  - `create(Sample(...))` 호출
  - **같은 파일 경로로 새로운** `SampleRepository` 인스턴스를 만들어 `get_all()` 호출 → 방금 만든 시료가 그대로 나타나는지 검증 (mock 없이 실제 파일 I/O 검증)
- `test_create_rejects_duplicate_sample_id`
  - 동일한 `sample_id`로 두 번 `create()` 호출 시 두 번째 호출에서 `ValueError` 발생
- `test_get_by_id_returns_none_when_not_found`
  - 빈 저장소에서 존재하지 않는 ID로 `get_by_id()` 호출 시 `None` 반환

### 프로덕션 코드 계획 (DataPersistence PoC 재사용/이식)
- `models/sample.py`
  - `Sample` dataclass: `sample_id: str`, `name: str`, `average_production_minutes: float`, `yield_rate: float`, `stock_quantity: int`
  - `to_dict()` / `from_dict()` (직렬화)
- `repository/json_repository.py`
  - `load_json(path)` / `save_json(path, data)` — 파일 없으면 빈 리스트로 초기화하는 공통 유틸
- `repository/sample_repository.py`
  - `SampleRepository(file_path)`: 생성자에서 파일 경로를 주입받음 (테스트 시 `tmp_path` 사용 가능하도록)
  - `create(sample) -> Sample`: 중복 ID면 `ValueError`
  - `get_all() -> list[Sample]`
  - `get_by_id(sample_id) -> Sample | None`

### 이번 슬라이스 범위 밖
- `update`/`delete` (다음 슬라이스에서 필요 시 추가)
- 이름 검색(시료 검색) 기능
- Controller/View, 메인 메뉴 (슬라이스 2에서 진행)
- `data/samples.json` 실제 운영 데이터 파일 — 테스트는 `tmp_path`만 사용하고, 실제 애플리케이션용 데이터 파일 경로 배선은 슬라이스 2(메인 메뉴 스켈레톤)에서 함께 진행

**상태: GREEN 완료, REVIEW 승인 완료 (커밋 `929ba90`)**

---

## 슬라이스 2: 시료 조회/검색 컨트롤러 + 메인 메뉴 스켈레톤

### PoC 재사용 방침
- `ConsoleMVC`/`DataPersistence` PoC 저장소는 수정하지 않고, **참고용으로만** 열람한다.
- **View**(`SampleView`, `MainView`): 순수 입출력(print/input)만 담당하고 분기 로직이 없으므로, ConsoleMVC PoC 코드를 이 저장소의 모듈 경로(`models`/`repository`가 아니라 `views`/`controllers`를 최상위에 둠)에 맞게 그대로 이식한다. 별도 테스트 없이 진행 (tdd-skill의 "설정/플러밍" 예외에 해당).
- **Repository/Controller**(`SampleRepository.search_by_name`, `SampleRepository.generate_sample_id`, `SampleController`): 실제 로직(검증, 채번, 필터링)이 있으므로 PoC는 참고만 하고 이 저장소에서 TDD로 새로 작성한다.

### 검증할 동작 (Behavior)

1. `SampleRepository.generate_sample_id()`
   - 저장소가 비어 있으면 `S-001`을 반환한다.
   - 기존 시료가 `S-001`, `S-002`이면 `S-003`을 반환한다 (기존 최대 번호 다음).
2. `SampleRepository.search_by_name(keyword)`
   - 이름에 keyword가 포함된(대소문자 무시) 시료만 반환한다.
   - 일치하는 것이 없으면 빈 리스트를 반환한다.
3. `SampleController.register_sample()`
   - 유효한 입력이면 `generate_sample_id()`로 채번한 뒤 저장소에 생성하고, View에 성공 메시지를 표시한다.
   - 이름이 빈 문자열이면 저장하지 않고 View에 에러를 표시한다.
   - 숫자 항목(평균 생산시간/수율/재고)이 숫자로 변환 불가능하면 저장하지 않고 View에 에러를 표시한다.
   - 수율이 0~1 범위를 벗어나면 저장하지 않고 View에 에러를 표시한다.
4. `SampleController.browse_samples()`
   - 선택값이 "1"이면 전체 목록을 View에 표시한다.
   - 선택값이 "2"이면 검색 키워드를 입력받아 그 결과를 View에 표시한다.

### 작성할 테스트
- `tests/repository/test_sample_repository.py`에 `generate_sample_id`, `search_by_name` 테스트 추가 (실제 `SampleRepository` + `tmp_path` 사용, mock 없음)
- `tests/controllers/test_sample_controller.py` (신규)
  - View는 mock/실제 콘솔 대신 **테스트용 Fake 객체**(고정된 입력을 반환하고 호출된 출력 메서드를 기록하는 간단한 스텁 클래스)를 사용한다 (tdd-skill "모든 것을 mock해야 한다 → DI를 사용하라" 가이드에 따름).
  - Repository는 `tmp_path` 기반 실제 `SampleRepository` 사용 (mock 없음).

### 프로덕션 코드 계획
- `repository/sample_repository.py`에 `generate_sample_id()`, `search_by_name(keyword)` 메서드 추가
- `controllers/__init__.py`, `controllers/sample_controller.py`: ConsoleMVC의 `SampleController` 로직을 이 저장소의 `SampleRepository` API(`create`/`get_all`/`generate_sample_id`/`search_by_name`)에 맞게 새로 작성
- `views/__init__.py`, `views/sample_view.py`, `views/main_view.py`: ConsoleMVC PoC에서 그대로 이식 (import 경로만 조정, 테스트 없음)
- `controllers/main_controller.py`, `main.py`: ConsoleMVC 패턴을 참고해 메인 메뉴 라우팅 스켈레톤 작성 (시료 등록/조회, 종료만 우선 연결. 주문 메뉴는 슬라이스 3에서 연결)

### 이번 슬라이스 범위 밖
- 시료 수정/삭제
- 주문(Order) 메뉴 연결 (슬라이스 3)
- `data/samples.json` 실제 배선 (main.py에서 고정 경로로 연결하되, 세부 데이터 시딩은 다루지 않음)

**상태: GREEN 완료, REVIEW 승인 완료 (커밋 `2760aaf`)**

---

## 슬라이스 3: 주문(Order) 예약

### PoC 재사용 방침에 대한 주의
- `ConsoleMVC`의 `OrderController.reserve_order()`는 예약 시점에 재고를 확인해 즉시 `REJECTED`로 전환하고 재고를 차감하는데, 이는 **CLAUDE.md/PRD.md 최종 명세와 다르다** (주문 예약은 항상 `RESERVED`로 생성되고, 재고 확인·차감·REJECTED 전환은 슬라이스 4 "주문 승인/거절"의 책임). PoC 작성 시점과 최종 명세가 어긋난 부분이므로, 이번 슬라이스는 PoC 로직을 따르지 않고 CLAUDE.md 기준으로 새로 설계한다.
- `DataPersistence`의 `Order` 모델(속성 구성, JSON 직렬화)과 순번 기반 주문번호 생성 방식은 그대로 참고한다.

### 검증할 동작 (Behavior)

1. `OrderRepository.generate_order_id()`
   - `ORD-YYYYMMDD-HHMM-NN` 형식으로, 기존 주문번호와 겹치지 않게 순번을 붙여 생성한다 (DataPersistence와 동일 규칙).
2. `OrderController.reserve_order()`
   - 존재하는 시료 ID + 유효한 고객명 + 1 이상의 정수 수량이 입력되면, 상태 `RESERVED`인 주문을 생성하고 저장한다. 이 시점에는 재고를 확인하거나 차감하지 않는다.
   - 존재하지 않는 시료 ID면 저장하지 않고 View에 에러를 표시한다.
   - 고객명이 빈 문자열이면 저장하지 않고 View에 에러를 표시한다.
   - 수량이 숫자로 변환 불가능하거나 0 이하이면 저장하지 않고 View에 에러를 표시한다.

### 작성할 테스트
- `tests/repository/test_order_repository.py` (신규): `create`/`get_all`/`generate_order_id`에 대해 Sample과 동일한 방식으로 검증 (mock 없이 `tmp_path` 사용)
- `tests/controllers/test_order_controller.py` (신규): `FakeOrderView` + 실제 `SampleRepository`/`OrderRepository`(`tmp_path`) 사용, mock 없음

### 프로덕션 코드 계획
- `models/order.py`: `Order` dataclass(`order_id`, `sample_id`, `customer_name`, `quantity`, `status`) + `to_dict`/`from_dict` (DataPersistence 참고)
- `repository/order_repository.py`: `OrderRepository(file_path)` — `create`(중복 ID 시 `ValueError`), `get_all`, `generate_order_id()` (DataPersistence의 순번 suffix 로직 참고)
- `controllers/order_controller.py`: `OrderController(order_repository, sample_repository, order_view)` — `reserve_order()`를 CLAUDE.md 기준(항상 RESERVED, 재고 미확인)으로 새로 작성
- `views/order_view.py`: ConsoleMVC PoC에서 이식 (순수 입출력, 테스트 없음)
- `controllers/main_controller.py`, `main.py`, `views/main_view.py`: 주문 메뉴("3. 시료 주문(예약)") 연결, 종료 메뉴 번호를 "4"로 조정

### 이번 슬라이스 범위 밖
- 주문 승인/거절, 재고 확인·차감 (슬라이스 4)
- 생산 라인, 모니터링, 출고 처리 (슬라이스 5~7)
