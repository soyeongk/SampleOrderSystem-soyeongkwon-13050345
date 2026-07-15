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

**상태: GREEN 완료, REVIEW 승인 완료 (커밋 `062e2e9`)**

---

## 슬라이스 4: 주문 승인/거절

### 설계 결정
- 승인 시점에 재고를 확정적으로 반영한다: **재고 충분** → 주문 수량만큼 재고를 즉시 차감하고 `CONFIRMED`. **재고 부족** → 기존 재고를 전부 이 주문에 배정(재고 0으로 차감)하고, 부족분(`주문수량 - 기존재고`)을 생산 큐에 등록한 뒤 `PRODUCING`.
- 생산 큐는 별도 JSON 저장소(`ProductionQueueRepository`)로 관리하며, **append 순서 = FIFO 순서**로 취급한다 (슬라이스 5에서 실제 소비/생산 처리).
- 이번 슬라이스는 "승인/거절 판단과 큐 등록"까지만 다룬다. 실 생산량 계산(`ceil(부족분/수율)`), 총 생산 시간, PRODUCING→CONFIRMED 자동 전환은 슬라이스 5.
- ConsoleMVC PoC에는 이 기능이 없어 참고할 기존 코드가 없다. View는 새로 작성하되, 순수 입출력이라 테스트는 생략한다.

### 검증할 동작 (Behavior)

1. `SampleRepository.decrease_stock(sample_id, amount)`: 재고를 amount만큼 줄이고 영속화한다.
2. `OrderRepository.update_status(order_id, new_status)`: 주문 상태를 갱신하고 영속화한다.
3. `ProductionQueueRepository.enqueue(entry)` / `get_all()`: 등록한 순서대로(FIFO) 조회된다.
4. `ApprovalController.list_pending_orders()`: `RESERVED` 상태 주문만 반환한다 (다른 상태는 제외).
5. `ApprovalController.approve(order_id)`
   - 재고가 주문 수량 이상이면: 주문 상태 `CONFIRMED`, 재고는 주문 수량만큼 차감.
   - 재고가 주문 수량 미만이면: 주문 상태 `PRODUCING`, 재고는 0으로 차감, 생산 큐에 `{order_id, sample_id, shortfall_quantity}` 등록 (`shortfall_quantity = 주문수량 - 기존재고`).
6. `ApprovalController.reject(order_id)`: 주문 상태 `REJECTED`로 전환, 재고는 변경하지 않는다.

### 작성할 테스트
- `tests/repository/test_sample_repository.py`: `decrease_stock` 테스트 추가
- `tests/repository/test_order_repository.py`: `update_status` 테스트 추가
- `tests/repository/test_production_queue_repository.py` (신규): enqueue 순서 보존 검증
- `tests/controllers/test_approval_controller.py` (신규): `FakeApprovalView` + 실제 Repository(`tmp_path`) 사용, mock 없음

### 프로덕션 코드 계획
- `repository/sample_repository.py`: `decrease_stock(sample_id, amount)` 추가
- `repository/order_repository.py`: `update_status(order_id, new_status)` 추가
- `models/production_queue_entry.py`, `repository/production_queue_repository.py` (신규): `enqueue`/`get_all`, JSON 영속성 (기존 패턴 재사용)
- `controllers/approval_controller.py` (신규): `list_pending_orders`/`approve`/`reject`
- `views/approval_view.py` (신규, 테스트 없음): 승인 대기 목록 표시, 승인/거절 선택 입력
- `controllers/main_controller.py`, `main.py`, `views/main_view.py`: "주문 승인/거절" 메뉴 연결

### 이번 슬라이스 범위 밖
- 생산 큐 실제 소비(FIFO 처리), 실 생산량/총 생산 시간 계산, PRODUCING→CONFIRMED 자동 전환 (슬라이스 5)
- 모니터링, 출고 처리 (슬라이스 6~7)

**상태: GREEN 완료, REVIEW 승인 완료 (커밋 `de76544`)**

---

## 슬라이스 4 설계 재검토 (사용자 피드백 반영)

**문제 시나리오**: 재고 100, 주문1(수량 130) 승인 → 기존 설계는 재고를 즉시 0으로 확정하고 부족분(30)만 생산 큐에 등록. 이 상태에서 주문2(수량 10)가 들어오면, 실제 재고(100)가 아직 충분히 있었음에도 이미 0으로 확정되어 버려 불필요하게 별도 생산이 걸린다.

**수정된 설계**: 승인 시점에 **재고가 부족해도 재고를 건드리지 않는다.** 그냥 주문을 `PRODUCING`으로 표시하고 큐에 "이 주문에 필요한 전체 수량"만 기록해둔다. 재고 차감/생산 필요량 계산은 **그 주문이 큐의 맨 앞(FIFO head)이 되어 실제로 생산이 시작되는 시점**에, 그 시점의 실제 재고를 기준으로 계산한다. 이렇게 하면:
- 주문2(10개)는 주문1의 생산 여부와 무관하게, 승인 시점의 실제 재고(100)로 즉시 판단된다 → 재고 충분하면 그 자리에서 바로 `CONFIRMED` (큐에 들어가지도 않음).
- 주문1의 생산이 끝나 재고가 늘어난 뒤에도, 다음 큐 항목이 있다면 그 시점의 재고로 다시 판단 → 이미 충분하면 추가 생산 없이 바로 `CONFIRMED` (연쇄 처리).

**`ApprovalController.approve()` 변경 사항** (기존 리뷰 완료 동작 수정, git 히스토리는 그대로 두고 새 커밋으로 반영):
- 재고 충분 시: 기존과 동일 (즉시 차감 + `CONFIRMED`)
- 재고 부족 시: **재고를 건드리지 않고**, 생산 큐에 `{order_id, sample_id, quantity}` (부족분이 아니라 **주문 전체 수량**)만 등록 + 주문 상태 `PRODUCING`

**받아들이는 트레이드오프**: 생산 큐에 들어간 주문을 위해 "예약"해두는 재고는 없다. 즉, 이론적으로 여러 승인이 동시에 같은 재고를 놓고 경쟁할 수 있지만(과도하게 약속된 상태), 이 프로젝트 규모의 콘솔 애플리케이션에서는 순차 처리이므로 실질적 문제가 되지 않는다.

---

## 슬라이스 5: 생산 라인

### 설계 결정 (시간 처리)
콘솔 앱이라 실제 백그라운드 스레드로 시간을 흘려보낼 수 없으므로, **"진행 상태를 확인하는 시점(현재 시각)"을 기준으로 경과 시간을 계산**하는 방식을 쓴다. 테스트 가능하도록 모든 시간 관련 메서드는 `now`를 인자로 주입받는다 (기존 `generate_order_id(base_time)`와 동일한 패턴).

- 큐의 맨 앞(FIFO head) 항목이 "현재 생산 중" 대상이다.
- head 항목이 아직 시작 전이면(`started_at is None`): 그 시점의 실제 재고와 비교한다.
  - 재고가 이미 head의 필요 수량(`quantity`) 이상이면: 생산 없이 바로 재고 차감 + 주문 `CONFIRMED` + 큐에서 제거 → 다음 항목에 대해 같은 판단을 반복한다 (연쇄 처리).
  - 재고가 부족하면: **그 시점 재고**로 부족분(`shortfall_quantity = quantity - 그 시점 재고`)을 계산하고, 실 생산량/총 생산 시간을 계산해 `started_at=now`와 함께 큐 항목에 저장한 뒤 멈춘다 (이 항목이 생산 중 상태가 됨).
- 이미 시작된 head 항목은 경과 시간(`now - started_at`, 분)과 총 생산 시간을 비교한다.
  - 미달이면 상태 유지 (주문은 계속 `PRODUCING`).
  - 충족되면: 재고를 실 생산량만큼 증가시킨 뒤, 그 재고에서 head의 필요 수량(`quantity`)만큼 차감해 주문을 소진 처리, 주문 `CONFIRMED`, 큐에서 제거. 이후 다음 큐 항목에 대해 위 판단을 이어서 반복한다 (남은 잉여 재고로 바로 `CONFIRMED` 되거나, 부족하면 그 차이만큼만 새로 생산 시작 — 사용자가 요청한 시나리오가 여기서 해결됨).
- **실 생산량** = `ceil(그 시점의 shortfall_quantity / 시료.수율)`, **총 생산 시간(분)** = `시료.평균생산시간 * 실생산량`.
- 부분 생산량만으로는 완료되지 않는다는 요구사항은 "경과 시간 전부가 지나야 완료"라는 규칙으로 만족한다.

### 검증할 동작 (Behavior)

1. `ProductionQueueEntry`: `order_id`, `sample_id`, `quantity`(주문 전체 수량) + `started_at`, `shortfall_quantity`, `actual_quantity`, `total_production_minutes`(모두 기본값 `None`, 생산 시작 시 채워짐), JSON 직렬화 포함.
2. `SampleRepository.increase_stock(sample_id, amount)`: 재고를 amount만큼 늘리고 영속화한다.
3. `ProductionQueueRepository`: `update_entry(order_id, **changes)`(필드 갱신), `remove(order_id)`(제거) 추가.
4. `ProductionLineController.advance(now)`
   - 큐가 비어 있으면 아무 것도 하지 않는다.
   - head가 미시작 상태이고 **현재 재고가 이미 충분**하면: 생산 없이 즉시 재고 차감 + `CONFIRMED` + 큐 제거 + 다음 항목도 계속 시도(연쇄).
   - head가 미시작 상태이고 재고가 부족하면: 그 시점 재고로 부족분/실생산량/총생산시간을 계산해 저장, 이후 멈춘다.
   - head가 시작됨 + 경과 시간 미달: 아무 것도 하지 않는다 (계속 `PRODUCING`).
   - head가 시작됨 + 경과 시간 충족: 재고를 실생산량만큼 증가 → `quantity`만큼 차감 → `CONFIRMED` → 큐 제거 → 다음 항목에 대해 반복.
5. `ProductionLineController.get_current_status(now)`: `advance(now)` 호출 후, 현재 생산 중(head, 시작된 상태) 항목 정보를 반환. 큐가 비어 있으면 `None`.
6. `ProductionLineController.get_waiting_queue()`: head를 제외한 나머지를 FIFO 순서로 반환.

### 작성할 테스트
- `tests/controllers/test_approval_controller.py`: 재고 부족 케이스 기존 테스트를 새 동작(재고 불변, 큐에 `quantity` 전체 저장)으로 수정
- `tests/repository/test_sample_repository.py`: `increase_stock` 테스트 추가
- `tests/repository/test_production_queue_repository.py`: `update_entry`, `remove` 테스트 추가
- `tests/controllers/test_production_line_controller.py` (신규): 실제 Repository(`tmp_path`) + 고정 `now` 값 사용, mock 없음
  - 재고 부족 → 생산 시작(부족분/실생산량/총생산시간 계산, 재고 불변) 확인
  - 경과 시간 미달 → 상태 유지
  - 경과 시간 충족 → 완료 처리(재고 증가 후 quantity만큼 차감, CONFIRMED, 큐 제거)
  - **사용자 시나리오**: 주문1 생산 완료 후 남은 잉여 재고로 다음 큐 항목(주문2)이 추가 생산 없이 바로 `CONFIRMED` 되는지
  - 큐가 비었을 때 `get_current_status`가 `None`을 반환하는지

### 프로덕션 코드 계획
- `models/production_queue_entry.py`: 필드를 `order_id/sample_id/quantity/started_at/shortfall_quantity/actual_quantity/total_production_minutes`로 구성
- `repository/sample_repository.py`: `increase_stock(sample_id, amount)` 추가
- `repository/production_queue_repository.py`: `update_entry(order_id, **changes)`, `remove(order_id)` 추가
- `controllers/approval_controller.py`: 재고 부족 분기를 위 설계대로 수정 (재고 불변, `quantity` 전체를 큐에 저장)
- `controllers/production_line_controller.py` (신규): `advance`, `get_current_status`, `get_waiting_queue`
- `views/production_view.py` (신규, 테스트 없음): 생산 현황(현재 생산 중 정보) + 대기 목록 출력
- `controllers/main_controller.py`, `main.py`, `views/main_view.py`: "생산 라인 조회" 메뉴 연결 (조회 시 `datetime.now()`를 주입)

### 이번 슬라이스 범위 밖
- 모니터링, 출고 처리 (슬라이스 6~7)

**상태: GREEN 완료, REVIEW 승인 완료 (커밋 `3064cc6`)**

---

## 슬라이스 6: 모니터링

### 설계 결정
`DataMonitor` PoC의 판정 로직(대기수요 = RESERVED+PRODUCING 주문 수량 합, 여유/부족/고갈 기준)을 참고하되, 실제 로직이 있으므로 이 저장소의 도메인 모델(Sample/Order dataclass)에 맞춰 TDD로 새로 작성한다.

- **재고 상태 판정 기준**: 재고 ≤ 0 → 고갈, 재고 < 대기수요 → 부족, 그 외 → 여유
- **대기수요** = 해당 시료를 참조하는 주문 중 상태가 `RESERVED` 또는 `PRODUCING`인 것들의 수량 합 (CONFIRMED/RELEASED는 이미 재고에서 처리 완료되었거나 출고된 것으로 간주해 제외, REJECTED는 애초에 유효한 주문이 아니므로 제외)

### 검증할 동작 (Behavior)

1. `MonitoringController.get_order_status_counts()`
   - `RESERVED`/`CONFIRMED`/`PRODUCING`/`RELEASED` 각각의 주문 건수를 반환한다.
   - `REJECTED` 주문은 집계에서 제외한다.
2. `MonitoringController.get_inventory_status()`
   - 시료별로 `sample_id`, `name`, `stock_quantity`, `pending_demand`, `status`(여유/부족/고갈)를 반환한다.
   - 대기수요는 `RESERVED`+`PRODUCING` 주문 수량 합으로 계산한다 (`CONFIRMED`/`RELEASED`/`REJECTED` 제외).
   - 재고 0 → 고갈, 재고 > 0이고 대기수요보다 적음 → 부족, 그 외 → 여유.

### 작성할 테스트
- `tests/controllers/test_monitoring_controller.py` (신규): 실제 Repository(`tmp_path`) 사용, mock 없음
  - 상태별 집계에서 REJECTED 제외 확인
  - 재고 0 → 고갈
  - 재고 > 0, 대기수요 초과 → 부족
  - 재고 > 0, 대기수요 이하 → 여유
  - 대기수요 계산 시 CONFIRMED/RELEASED/REJECTED 주문은 반영되지 않는지 확인

### 프로덕션 코드 계획
- `controllers/monitoring_controller.py` (신규): `get_order_status_counts`, `get_inventory_status`
- `views/monitoring_view.py` (신규, 테스트 없음): 상태별 주문 수, 시료별 재고 현황 출력
- `controllers/main_controller.py`, `main.py`, `views/main_view.py`: "모니터링" 메뉴 연결

### 이번 슬라이스 범위 밖
- 출고 처리 (슬라이스 7)

**상태: GREEN 완료, REVIEW 승인 완료 (커밋 `bb0c275`)**

---

## 슬라이스 7: 출고 처리 (마지막 슬라이스)

### 검증할 동작 (Behavior)

1. `ShipmentController.list_shippable_orders()`: `CONFIRMED` 상태 주문만 반환한다.
2. `ShipmentController.ship(order_id)`: 주문 상태를 `RELEASED`로 전환한다.
3. `ShipmentController.handle_menu()` (슬라이스 4의 `ApprovalController.handle_menu` 패턴과 동일)
   - 출고 가능 목록을 View에 표시하고, 목록이 비어 있으면 그대로 종료한다.
   - 사용자가 선택한 주문번호가 출고 가능 목록에 없으면 View에 에러를 표시한다.
   - 있으면 `ship()`을 호출하고 결과를 View에 표시한다.

### 작성할 테스트
- `tests/controllers/test_shipment_controller.py` (신규): `FakeShipmentView` + 실제 `OrderRepository`(`tmp_path`) 사용, mock 없음

### 프로덕션 코드 계획
- `controllers/shipment_controller.py` (신규): `list_shippable_orders`, `ship`, `handle_menu`
- `views/shipment_view.py` (신규, 테스트 없음): 출고 가능 목록 표시, 주문번호 입력, 결과/에러 표시
- `controllers/main_controller.py`, `main.py`, `views/main_view.py`: "출고 처리" 메뉴 연결, 종료 메뉴 번호 재조정

### 이번 슬라이스 범위 밖
- 없음 — 기능 명세의 마지막 항목
