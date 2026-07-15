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
