# SampleOrderSystem — 반도체 시료 생산주문관리 시스템

가상의 반도체 회사 "S-Semi"의 시료(Sample) 생산·주문·재고를 관리하는 콘솔(CLI) 애플리케이션입니다.
자세한 배경과 기능 명세는 [CLAUDE.md](./CLAUDE.md), 요구사항 정리는 [PRD.md](./PRD.md)를 참고하세요.

## 기술 스택

- Python 3 (표준 라이브러리 중심)
- 데이터 저장: JSON 파일 기반 영속성 (`data/` 디렉토리, 실행 시 자동 생성)
- 아키텍처: MVC (Model / View / Controller)
- 테스트: pytest

## 실행 방법

### 1. 가상환경 준비 및 의존성 설치

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 애플리케이션 실행

```bash
python main.py
```

실행하면 콘솔 메뉴가 표시됩니다.

```
===== S-Semi 시료 생산주문관리 시스템 =====
1. 시료 등록
2. 시료 조회
3. 시료 주문(예약)
4. 주문 승인/거절
5. 생산 라인 조회
6. 모니터링
7. 출고 처리
8. 종료
메뉴를 선택하세요:
```

번호를 입력해 원하는 기능으로 이동합니다. 데이터는 `data/samples.json`, `data/orders.json`,
`data/production_queue.json`에 저장되며, 애플리케이션을 다시 실행해도 이전 데이터가 유지됩니다.

### 3. 테스트 실행

```bash
pytest

# 특정 파일만
pytest tests/controllers/test_sample_controller.py

# 자세한 출력
pytest -v
```

## 기능 요약

| 메뉴 | 설명 |
|---|---|
| 시료 등록/조회 | 시료 ID·이름·평균 생산시간·수율을 등록하고, 전체 목록 또는 이름으로 검색 조회 |
| 시료 주문(예약) | 시료 ID·고객명·수량으로 주문 생성 (`RESERVED`) |
| 주문 승인/거절 | 재고 충분 시 즉시 `CONFIRMED`, 부족 시 생산 큐 등록 후 `PRODUCING`, 거절 시 `REJECTED` |
| 생산 라인 조회 | FIFO 생산 큐 처리 — 실 생산량(`ceil(부족분/수율)`)·총 생산 시간 계산, 시간 경과 시 `PRODUCING → CONFIRMED` |
| 모니터링 | 상태별 주문 수(REJECTED 제외), 시료별 재고 상태(여유/부족/고갈) |
| 출고 처리 | `CONFIRMED` 상태 주문을 `RELEASED`로 전환 |

## 프로젝트 구조

```
main.py                        # 진입점
models/                        # 도메인 모델 (Sample, Order, ProductionQueueEntry)
repository/                    # JSON 파일 기반 영속성 계층
controllers/                   # 비즈니스 로직 (Model ↔ View 조율)
views/                         # 콘솔 입출력 전담 (로직 없음)
tests/                         # pytest 테스트 스위트 (controllers/, repository/)
data/                          # 실행 시 생성되는 JSON 데이터 파일 (git 추적 제외)
.claude/skills/tdd-skill/      # 이 저장소가 따르는 TDD 워크플로우 정의
.claude/agents/                # 구현/검증용 서브에이전트 정의
Plan.md                        # 슬라이스별 TDD 계획 및 진행 이력
```
