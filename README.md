# TCP-Controlled Web Browser Automation Module

웹 브라우저 자동화를 TCP 명령으로 제어하는 Python 모듈입니다.

## 빠른 시작

```bash
# 1. Mock 서버 시작 (테스트용)
python mock_tcp_server.py 5001

# 2. 다른 터미널에서 테스트 실행
python test_tcp_connection.py localhost 5001

# 3. Interactive 클라이언트 시험
python tcp_client_example.py interactive
```

더 자세한 가이드는 [QUICK_START.md](QUICK_START.md)와 [TESTING.md](TESTING.md)를 참조하세요.

## 기능

- **TCP 서버 모드**: 외부 애플리케이션에서 TCP/IP로 명령을 보내 브라우저 자동화 실행
- **CLI 모드**: 명령줄 인자로 직접 실행 (테스트/디버깅용)
- **명령 큐잉**: 여러 명령을 순차적으로 처리
- **브라우저 재사용**: 로그인 상태 유지로 성능 향상
- **에러 처리**: 11가지 에러 코드로 상세한 오류 보고
- **디버그 로깅**: `--debug` 플래그로 실시간 로그 출력
- **테스트 도구**: Mock 서버 및 자동화된 연결 테스트 포함
- **Interactive 클라이언트**: 대화형 명령 작성 도구

## 설치

### 요구사항
- Python 3.13 이상
- Chrome 브라우저
- Windows 11

### 의존성 설치

```bash
# uv 사용 (권장)
uv sync

# 또는 pip 사용
pip install selenium webdriver-manager ipykernel
```

## 사용 방법

### 1. CLI 모드 (테스트용)

명령줄에서 직접 자동화를 실행합니다:

```bash
python browser_module.py \
  --id your_username \
  --password your_password \
  --vin KMHXX00XXXX000000 \
  --fname1 CSU_ACN \
  --response 1 \
  --opt1 ACK \
  --debug
```

**fname2 포함 예제:**

```bash
python browser_module.py \
  --id your_username \
  --password your_password \
  --vin KMHXX00XXXX000000 \
  --fname1 CSU_ACN \
  --fname2 CSU_ACN/VCT \
  --response 2 \
  --opt1 ACK \
  --opt2 NACK \
  --debug
```

### 2. TCP 서버 모드 (프로덕션)

TCP 서버를 시작하고 명령을 대기합니다:

```bash
python browser_module.py --port 5000 --debug
```

**TCP 클라이언트에서 명령 전송:**

```bash
# Interactive 모드 (권장)
python tcp_client_example.py interactive

# 테스트 명령
python tcp_client_example.py test

# JSON 파일에서 로드
python tcp_client_example.py custom example_command.json
```

또는 직접 소켓으로 JSON 전송:

```python
import socket
import json

command = {
    "command": "START",
    "id": "your_username",
    "password": "your_password",
    "vin": "KMHXX00XXXX000000",
    "fname1": "CSU_ACN",
    "response_option": 1,
    "option1": "ACK"
}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 5000))
sock.sendall(json.dumps(command).encode('utf-8'))
response = sock.recv(8192)
print(json.loads(response.decode('utf-8')))
sock.close()
```

## 명령 형식

### START 명령

```json
{
  "command": "START",
  "id": "lge_1",
  "password": "your_password",
  "vin": "KMHXX00XXXX000000",
  "fname1": "CSU_ACN",
  "fname2": "CSU_ACN/VCT",
  "response_option": 2,
  "option1": "ACK",
  "option2": "NACK"
}
```

**필수 파라미터:**
- `command`: "START"
- `id`: 로그인 ID
- `password`: 로그인 비밀번호
- `vin`: VIN 검색어
- `fname1`: 첫 번째 함수명
- `response_option`: 응답 옵션 (1=default, 2=custom, 3=no_response)
- `option1`: fname1의 타입 값

**선택 파라미터:**
- `fname2`: 두 번째 함수명 (선택)
- `option2`: fname2의 타입 값 (fname2가 있고 response_option=2일 때 필수)

### STOP 명령

```json
{
  "command": "STOP"
}
```

현재 작업 완료 후 브라우저를 닫고 서버를 종료합니다.

## 응답 형식

### 성공 응답

```json
{
  "result": "success",
  "vin": "KMHXX00XXXX000000",
  "fnames": ["CSU_ACN", "CSU_ACN/VCT"],
  "response_type": 2,
  "options": ["ACK", "NACK"],
  "timestamp": "2025-10-13T15:30:00.123Z"
}
```

### 에러 응답

```json
{
  "result": "error",
  "error_code": 1005,
  "error_message": "VIN not found: KMHXX00XXXX000000",
  "timestamp": "2025-10-13T15:30:00.123Z"
}
```

## 에러 코드

| 코드 | 설명 |
|------|------|
| 1001 | TCP connection error |
| 1002 | Login failure after maximum retries |
| 1003 | Invalid command format |
| 1004 | Missing required parameters |
| 1005 | VIN not found |
| 1006 | Function name not found |
| 1007 | Invalid response_option value |
| 1008 | Element wait timeout |
| 1009 | JSON parsing or modification error |
| 1010 | Browser crash |
| 1011 | Unknown error |

## 프로젝트 구조

```
tsp_auto/
├── browser_module.py          # 메인 진입점
├── config.py                  # 설정 및 셀렉터
├── logger.py                  # 로깅 시스템
├── error_codes.py             # 에러 코드 정의
├── browser_manager.py         # 브라우저 생명주기 관리
├── automation_workflow.py     # 자동화 워크플로우 (개선된 대기 로직)
├── response_handler.py        # 응답 생성
├── command_processor.py       # 명령 처리 및 큐
├── tcp_server.py              # TCP 서버
├── tcp_client_example.py      # TCP 클라이언트 예제 (interactive 모드 포함)
├── mock_tcp_server.py         # Mock TCP 서버 (테스트용)
├── test_tcp_connection.py     # 자동화된 TCP 연결 테스트
├── example_command.json       # 단일 function 예제
├── example_command_dual.json  # 2개 function 예제
├── tests/                     # 유닛 테스트
│   ├── __init__.py
│   └── test_unit_basic.py    # 17개 기본 테스트
├── README.md                  # 이 파일
├── QUICK_START.md             # 빠른 시작 가이드
├── API_PROTOCOL.md            # API 프로토콜 문서
└── TESTING.md                 # 테스트 가이드
```

## 자동화 워크플로우

1. **로그인**: 대상 사이트에 로그인 (재시도 최대 2회)
2. **VIN 검색**: VIN으로 검색하여 첫 번째 결과 선택
3. **함수명 검색 (fname1)**: 테이블에서 함수명 찾아 선택
4. **응답 옵션 선택**: 라디오 버튼 선택 (1/2/3)
5. **JSON 수정** (response_option=2인 경우): `header.message.type` 값 변경
6. **업데이트**: 업데이트 버튼 클릭
7. **fname2 처리** (제공된 경우): 3-6 단계 반복
8. **응답 반환**: 성공/에러 JSON 응답

## 테스트

### 유닛 테스트 실행

```bash
# 모든 유닛 테스트 (17개)
pytest tests/test_unit_basic.py -v

# 특정 테스트 클래스만
pytest tests/test_unit_basic.py::TestCommandValidation -v
```

### TCP 연결 자동 테스트

Mock 서버를 사용한 빠른 테스트:

**터미널 1 - Mock 서버 시작:**
```bash
python mock_tcp_server.py 5001
```

**터미널 2 - 자동 테스트 실행:**
```bash
python test_tcp_connection.py localhost 5001
```

**예상 결과:**
```
============================================================
TEST SUMMARY
============================================================
[PASS]     Connection Test
[PASS]     Invalid JSON Test
[PASS]     Missing Parameters Test
[PASS]     Invalid Response Option Test

Total: 4 | Passed: 4 | Failed: 0

*** All tests passed! ***
```

### 실제 서버 테스트

**터미널 1 - 실제 서버 시작:**
```bash
python browser_module.py --port 5000 --debug
```

**터미널 2 - Interactive 클라이언트:**
```bash
python tcp_client_example.py interactive
```

더 자세한 테스트 가이드는 [TESTING.md](TESTING.md)를 참조하세요.

## 설정

`config.py`에서 다음 항목을 수정할 수 있습니다:

- **TARGET_URL**: 대상 웹사이트 URL
- **DEFAULT_TCP_PORT**: 기본 TCP 포트
- **ELEMENT_WAIT_TIMEOUT**: 요소 대기 시간 (초)
- **SELECTORS**: CSS 셀렉터 (웹사이트 구조 변경 시 수정)
- **MAX_LOGIN_RETRIES**: 로그인 재시도 횟수

## 문제 해결

### 브라우저가 시작되지 않음
- Chrome이 설치되어 있는지 확인
- ChromeDriver가 자동으로 다운로드되는지 확인
- 방화벽/백신 소프트웨어가 차단하는지 확인

### 로그인 실패
- 자격 증명이 올바른지 확인
- 웹사이트가 접근 가능한지 확인
- `--debug` 플래그로 상세 로그 확인

### 요소를 찾을 수 없음 (1008 에러)
- 웹사이트 구조가 변경되었을 수 있음
- `config.py`의 CSS 셀렉터 업데이트 필요
- 네트워크 지연으로 타임아웃 발생 가능

### TCP 연결 실패 (1001 에러)
- 서버가 실행 중인지 확인
- 포트 번호가 올바른지 확인
- 방화벽이 포트를 차단하는지 확인

## 개발자 정보

### 디버그 모드 활성화

```bash
python browser_module.py --debug
```

실시간 로그가 `[INFO]`, `[SUCCESS]`, `[FAIL]` 접두사와 함께 출력됩니다.

### 코드 구조

- **browser_module.py**: TCP/CLI 모드 분기, 워커 스레드 관리
- **browser_manager.py**: Selenium WebDriver 래퍼, 상태 감지
- **automation_workflow.py**: 8단계 워크플로우 구현 (개선된 명시적 대기)
- **tcp_server.py**: 소켓 관리, 단일 클라이언트 연결
- **command_processor.py**: 명령 검증, FIFO 큐
- **mock_tcp_server.py**: 브라우저 없는 테스트 서버
- **test_tcp_connection.py**: 4가지 자동 테스트 시나리오

### 최근 개선 사항

- **에러 핸들링**: `time.sleep()` → 명시적 대기 로직으로 변경
  - `search_vin()`: 결과 로드를 위한 명시적 대기
  - `search_function_name()`: 테이블 로드를 위한 폴링 대기 (최대 10초)
  - `process_function_name()`: 페이지 안정화 시간 최소화 (2s → 0.5s)
  - `click_update_button()`: 전환 대기 최소화 (2s → 0.5s)

- **TCP 클라이언트**: Interactive 모드 및 JSON 파일 로드 지원
- **테스트 도구**: Mock 서버와 자동화된 연결 테스트 추가
- **문서화**: TESTING.md, API_PROTOCOL.md, QUICK_START.md 추가

## 라이선스

이 프로젝트는 내부 사용을 위해 개발되었습니다.

## 추가 문서

- **[QUICK_START.md](QUICK_START.md)** - 5분 안에 시작하기
- **[TESTING.md](TESTING.md)** - 완전한 테스트 가이드
- **[API_PROTOCOL.md](API_PROTOCOL.md)** - 상세한 API 프로토콜 문서

## 주의사항

- **Headless 모드 비활성화**: 버튼이 headless 모드에서 보이지 않아 `headless=False`로 설정됨
- **단일 연결**: TCP 서버는 한 번에 하나의 클라이언트 연결만 허용
- **브라우저 재사용**: STOP 명령 없이는 브라우저가 열린 상태로 유지됨
- **비밀번호 보안**: 명령줄에서 비밀번호가 노출될 수 있으므로 프로덕션에서는 TCP 모드 사용 권장
- **ID/PW 관리**: 모든 자격증명은 클라이언트에서 파라미터로 전달됨 (코드에 하드코딩 없음)
