# TCP 서버 테스트 가이드

이 문서는 tsp_auto TCP 서버의 동작을 테스트하는 방법을 설명합니다.

## 테스트 도구

### 1. `mock_tcp_server.py` - Mock TCP 서버
브라우저 없이 TCP 통신을 테스트할 수 있는 Mock 서버입니다.

**특징:**
- 실제 브라우저 자동화 없이 TCP 프로토콜 테스트
- 명령어 검증 및 에러 응답 시뮬레이션
- 빠른 테스트 실행

**사용법:**
```bash
# 기본 포트(5000)로 시작
python mock_tcp_server.py

# 커스텀 포트로 시작
python mock_tcp_server.py 5001

# 도움말
python mock_tcp_server.py --help
```

**출력 예시:**
```
============================================================
Mock TCP Server Running on port 5001
============================================================
This is a TEST server that simulates responses
Press Ctrl+C to stop
============================================================

[127.0.0.1:52464] Connected
[127.0.0.1:52464] Received 39 bytes
[127.0.0.1:52464] Command: START
[127.0.0.1:52464] Sent response: error
[127.0.0.1:52464] Disconnected
```

---

### 2. `test_tcp_connection.py` - TCP 연결 테스트 클라이언트
서버의 TCP 통신을 자동으로 테스트하는 도구입니다.

**테스트 항목:**
1. **Connection Test** - 기본 TCP 연결 테스트
2. **Invalid JSON Test** - 잘못된 JSON 처리 테스트
3. **Missing Parameters Test** - 필수 파라미터 누락 테스트
4. **Invalid Response Option Test** - 잘못된 response_option 값 테스트

**사용법:**
```bash
# 기본 서버(localhost:5000) 테스트
python test_tcp_connection.py

# 커스텀 서버 테스트
python test_tcp_connection.py localhost 5001
python test_tcp_connection.py 192.168.1.100 5000

# 도움말
python test_tcp_connection.py --help
```

**출력 예시:**
```
============================================================
TCP SERVER TEST SUITE
============================================================
Target: localhost:5001
Time: 2025-10-14 09:22:42

============================================================
TEST 1: Connection Test
============================================================
Attempting to connect to localhost:5001...
[PASS] Connection successful!

...

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

---

### 3. `tcp_client_example.py` - TCP 클라이언트 예제
실제 명령을 서버에 전송하는 클라이언트입니다.

**사용법:**
```bash
# Interactive 모드 (권장)
python tcp_client_example.py interactive

# 테스트 명령 전송
python tcp_client_example.py test

# JSON 파일에서 명령 로드
python tcp_client_example.py custom example_command.json

# STOP 명령 전송
python tcp_client_example.py stop
```

---

## 전체 테스트 워크플로우

### 단계 1: Mock 서버 시작
```bash
# 터미널 1
python mock_tcp_server.py 5001
```

### 단계 2: 자동 테스트 실행
```bash
# 터미널 2
python test_tcp_connection.py localhost 5001
```

**예상 결과:** 모든 테스트 통과
```
Total: 4 | Passed: 4 | Failed: 0
*** All tests passed! ***
```

### 단계 3: 수동 테스트 (Interactive)
```bash
# 터미널 2
python tcp_client_example.py interactive
```

**입력 예시:**
```
Enter choice (1-2): 1
Enter username: test_user
Enter password: test_pass
Enter VIN: TEST123
Enter primary function name (fname1): TEST_FUNC
Enter secondary function name (fname2) [optional, press Enter to skip]:
Enter response option (1-3): 1
Send this command? (y/n): y
```

**예상 응답:**
```json
{
  "result": "success",
  "vin": "TEST123",
  "fnames": ["TEST_FUNC"],
  "response_type": 1,
  "options": ["ACK"],
  "timestamp": "2025-01-01T00:00:00.000Z",
  "mock": true
}
```

### 단계 4: 서버 종료
```bash
# 터미널 1에서 Ctrl+C
```

---

## 실제 서버 테스트

Mock 서버 대신 실제 브라우저 자동화 서버를 테스트하려면:

### 1. 실제 서버 시작
```bash
tsp_auto.exe
```

### 2. 자동 테스트 실행
```bash
python test_tcp_connection.py localhost 5000
```

**참고:** 실제 서버는 브라우저를 실행하고 로그인을 시도하므로:
- `test_missing_params` 등의 검증 테스트는 통과
- `test_connection`은 통과하지만 START 명령은 실제 자격증명이 필요

### 3. 실제 명령 전송
```bash
# example_command.json 파일 편집 (실제 자격증명 입력)
# id, password, vin 등을 실제 값으로 변경

python tcp_client_example.py custom example_command.json
```

---

## 트러블슈팅

### 문제: "Connection refused"
**원인:** 서버가 실행되지 않음
**해결:**
```bash
python mock_tcp_server.py 5001
```

### 문제: "Socket timeout"
**원인:** 서버가 응답하지 않음
**해결:**
- 서버 로그 확인
- 방화벽 설정 확인
- 포트 번호 확인

### 문제: "Address already in use"
**원인:** 포트가 이미 사용 중
**해결:**
```bash
# 다른 포트 사용
python mock_tcp_server.py 5002
python test_tcp_connection.py localhost 5002
```

---

## JSON 명령 파일 예제

### example_command.json (단일 function)
```json
{
  "command": "START",
  "id": "your_username_here",
  "password": "your_password_here",
  "vin": "KMHXX00XXXX000000",
  "fname1": "CSU_ACN",
  "fname2": null,
  "response_option": 1,
  "option1": "ACK",
  "option2": null
}
```

### example_command_dual.json (2개 function)
```json
{
  "command": "START",
  "id": "your_username_here",
  "password": "your_password_here",
  "vin": "KMHXX00XXXX000000",
  "fname1": "CSU_ACN",
  "fname2": "CSU_BFD",
  "response_option": 2,
  "option1": "ACK",
  "option2": "NAK"
}
```

---

## 추가 정보

- **API 프로토콜:** [API_PROTOCOL.md](API_PROTOCOL.md)
- **Quick Start:** [QUICK_START.md](QUICK_START.md)
- **Main README:** [README.md](README.md)
