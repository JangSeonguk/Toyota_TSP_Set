# TSP Auto - TCP 브라우저 자동화 모듈

웹 브라우저 자동화를 TCP 명령으로 제어하는 Python 모듈입니다.

---

## 1. 설치

### 개발 환경
- Python 3.13+
- Chrome 브라우저
- Windows 11

### 의존성 설치
```bash
pip install -r requirements.txt
```

---

## 2. 빌드

### 서버 빌드
```bash
pyinstaller --onefile --name tsp_auto browser_module.py
```

### 클라이언트 빌드
```bash
pyinstaller --onefile --name tsp_client tsp_client.py
```

빌드 결과: `dist/tsp_auto.exe`, `dist/tsp_client.exe`

---

## 3. 실행

### 서버 실행
```bash
# Python
python browser_module.py --port 5000 --debug

# EXE
dist\tsp_auto.exe --port 5000 --debug
```

### 클라이언트 실행
```bash
# 인터랙티브 모드
python tsp_client.py

# JSON 파일 전송
python tsp_client.py --file command.json
```

---

## 4. 명령 형식

### START - 자동화 실행

```json
{
  "command": "START",
  "id": "lge_1",
  "password": "your_password",
  "vin": "KMHXX00XXXX000000",
  "fname1": "CSU_ACN",
  "response_option": 1,
  "add_request": false
}
```

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| `id` | O | 로그인 ID |
| `password` | O | 로그인 비밀번호 |
| `vin` | O | VIN 번호 (17자리) |
| `fname1` | O | 함수명 |
| `response_option` | O | 응답 옵션 (1=default, 2=custom, 3=no_response) |
| `option1` | X | 타입 값 (response_option=2일 때 필수) |
| `fname2` | X | 2차 함수명 |
| `response_option2` | X | fname2 응답 옵션 |
| `option2` | X | fname2 타입 값 |
| `add_request` | X | 세션 유지 모드 (기본값: false) |

### SET - 추가 fname 처리 (add_request 모드)

```json
{
  "command": "SET",
  "fname": "CSU_ACN",
  "response_option": 2,
  "option": "ACK"
}
```

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| `fname` | O | 함수명 |
| `response_option` | O | 응답 옵션 (1=default, 2=custom, 3=no_response) |
| `option` | X | 타입 값 (response_option=2일 때 필수) |

### PUSH - DCM Push 명령 (add_request 모드)

```json
{
  "command": "PUSH",
  "topic": "voicekill",
  "push_template": "voicekill"
}
```

| 파라미터 | 필수 | 설명 |
|----------|------|------|
| `topic` | O | Push 토픽 (예: voicekill) |
| `push_template` | O | Push 템플릿 이름 (예: voicekill) |

### CLOSE - 세션 종료 (add_request 모드)

```json
{
  "command": "CLOSE"
}
```

파라미터 없음. 현재 세션을 종료하고 브라우저를 닫습니다.

### STOP - 서버 종료

```json
{
  "command": "STOP"
}
```

파라미터 없음. 서버를 완전히 종료합니다.

---

## 5. 응답 형식

### 성공 응답
```json
{
  "result": "success",
  "vin": "KMHXX00XXXX000000",
  "fnames": ["CSU_ACN"],
  "response_type": 1,
  "timestamp": "2025-10-13T10:30:45.123456Z"
}
```

### 에러 응답
```json
{
  "result": "error",
  "error_code": 1005,
  "error_message": "VIN not found",
  "timestamp": "2025-10-13T10:30:45.123456Z"
}
```

---

## 6. 에러 코드

| 코드 | 설명 |
|------|------|
| 1001 | TCP 연결 오류 |
| 1002 | 로그인 실패 |
| 1003 | 잘못된 명령 형식 |
| 1004 | 필수 파라미터 누락 |
| 1005 | VIN 없음 |
| 1006 | 함수명 없음 |
| 1007 | 잘못된 response_option |
| 1008 | 요소 대기 타임아웃 |
| 1009 | JSON 파싱 오류 |
| 1010 | 브라우저 크래시 |
| 1011 | 알 수 없는 오류 |
| 1012 | Push 명령 실패 |
| 1014 | 활성 세션 없음 |

---

## 7. add_request 모드 흐름

```
1. START (add_request: true) → 로그인, VIN 검색, fname1 처리, 세션 시작
2. SET → 추가 fname 처리 (반복 가능)
3. PUSH → DCM Push 명령 전송 (반복 가능)
4. CLOSE → 세션 종료, 브라우저 닫기
```

---

## 8. 필수 파일

### 핵심 모듈
| 파일 | 설명 |
|------|------|
| `browser_module.py` | 메인 진입점 |
| `tcp_server.py` | TCP 서버 |
| `command_processor.py` | 명령 처리 |
| `automation_workflow.py` | 자동화 워크플로우 |
| `browser_manager.py` | 브라우저 관리 |
| `session_manager.py` | 세션 관리 |
| `response_handler.py` | 응답 생성 |
| `error_codes.py` | 에러 코드 |
| `config.py` | 설정 |
| `logger.py` | 로깅 |

### 클라이언트
| 파일 | 설명 |
|------|------|
| `tsp_client.py` | Interactive TCP 클라이언트 |
| `tcp_client_example.py` | 단순 TCP 클라이언트 예제 |

---

## 9. 사용 예제

### Python 코드
```python
import socket
import json

# 연결
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 5000))

# 명령 전송
command = {
    "command": "START",
    "id": "lge_1",
    "password": "xxx",
    "vin": "KMHXX00XXXX000000",
    "fname1": "CSU_ACN",
    "response_option": 1
}
sock.sendall(json.dumps(command).encode('utf-8'))

# 응답 수신
response = json.loads(sock.recv(8192).decode('utf-8'))
print(response)
sock.close()
```

### tsp_client.py 인터랙티브 명령
```
load <file.json>  - JSON 파일 전송
send <json>       - 인라인 JSON 전송
set               - SET 명령 빌더
push              - PUSH 명령 빌더
close             - CLOSE 명령
status            - 연결 상태
quit              - 종료
```
