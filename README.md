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

실행하면 시스템 현황과 함께 콘솔 메뉴가 표시됩니다.

```
===== S-Semi 시료 생산주문관리 시스템 =====
시스템 현황: 2026-07-15 14:15:50
등록시료: 12종   총 재고: 2523ea
전체 주문: 3건   생산라인: 1건 대기

1. 시료 등록
2. 시료 조회
3. 시료 주문(예약)
4. 주문 승인/거절
5. 생산 라인 조회
6. 모니터링
7. 출고 처리
8. [Test용] Dummy data 생성(시료)
9. [Test용] 생산 시간 강제 경과
10. 종료
메뉴를 선택하세요:
```

번호를 입력해 원하는 기능으로 이동합니다. 데이터는 `data/samples.json`, `data/orders.json`,
`data/production_queue.json`에 저장되며, 애플리케이션을 다시 실행해도 이전 데이터가 유지됩니다.
각 메뉴 처리 후에는 "계속하려면 Enter를 누르세요..."가 표시되며, Enter를 누르면 화면이
정리되고 메인 메뉴로 돌아갑니다.

시료 목록/주문 목록처럼 여러 건을 보여주는 화면은 10개씩 페이지로 표시되며,
`n`(다음 페이지)/`p`(이전 페이지)/`b`(이전 메뉴로) 명령과 항목 번호 선택을 지원합니다.

8, 9번 메뉴는 채점/시연을 돕기 위한 테스트 전용 기능입니다. 8번은 임의의 더미 시료를
지정한 개수만큼 생성하고, 9번은 현재 생산 중인 항목을 실제 시간이 지나기를 기다리지 않고
즉시 완료 처리합니다.

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
| 시료 등록/조회 | 시료 이름·평균 생산시간·수율·재고를 등록(ID 자동 채번, 이름 중복 불가). 전체 목록/이름 검색 결과를 페이지 테이블로 조회 |
| 시료 주문(예약) | 페이지 테이블에서 시료를 번호로 선택 → 고객명·수량 입력 → 입력 내용 확인(Y/N) 후 주문 생성 (`RESERVED`) |
| 주문 승인/거절 | 주문 선택 시 시료·현재 재고·부족분(부족하면 실 생산량/생산 시간까지) 요약을 보여준 뒤 승인/거절 결정. 재고 충분 시 즉시 `CONFIRMED`, 부족 시 생산 큐 등록 후 `PRODUCING`, 거절 시 `REJECTED` |
| 생산 라인 조회 | FIFO 생산 큐 처리 — 실 생산량(`ceil(부족분/수율)`)·총 생산 시간 계산, 시간 경과 시 `PRODUCING → CONFIRMED`. 완료 후 잉여 재고로 다음 대기 주문이 추가 생산 없이 바로 확정될 수 있음 |
| 모니터링 | 상태별 주문 수(REJECTED 제외), 시료별 재고 상태(여유/부족/고갈) |
| 출고 처리 | `CONFIRMED` 상태 주문을 페이지 테이블에서 선택해 `RELEASED`로 전환 |
| [Test용] Dummy data 생성(시료) | 개수를 입력받아 임의의 더미 시료를 생성 (이름 후보 소진 시에도 유일성 보장) |
| [Test용] 생산 시간 강제 경과 | 현재 생산 중인 큐 항목을 실제 시간 경과 없이 즉시 완료 처리 |

## 프로젝트 구조

```
main.py                        # 진입점
models/                        # 도메인 모델 (Sample, Order, ProductionQueueEntry)
repository/                    # JSON 파일 기반 영속성 계층
controllers/                   # 비즈니스 로직 (Model ↔ View 조율), pagination.py는 페이지네이션 공용 유틸
views/                         # 콘솔 입출력 전담 (로직 없음). screen.py(화면 정리), table.py(표 정렬 계산)는 예외적으로 순수 로직 포함
tests/                         # pytest 테스트 스위트 (controllers/, repository/, views/)
data/                          # 실행 시 생성되는 JSON 데이터 파일 (git 추적 제외)
.claude/skills/tdd-skill/      # 이 저장소가 따르는 TDD 워크플로우 정의
.claude/agents/                # 구현/검증용 서브에이전트 정의
Plan.md                        # 슬라이스별 TDD 계획 및 진행 이력
```
