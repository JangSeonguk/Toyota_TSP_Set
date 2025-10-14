# TSP 자동화 모듈 - 빠른 시작 가이드

## 📡 연결 방법

```
서버: localhost:5000
프로토콜: TCP/IP
데이터: JSON (UTF-8)
```

---

## 📤 요청 JSON

### 기본 사용 (필수 항목만)

```json
{
  "command": "START",
  "id": "lge_1",
  "password": "your_password",
  "vin": "KMHXX00XXXX000000",
  "fname1": "CSU_ACN",
  "response_option": 1,
  "option1": "ACK"
}
```

### fname2 포함 (2개 함수 처리)

```json
{
  "command": "START",
  "id": "lge_1",
  "password": "your_password",
  "vin": "KMHXX00XXXX000000",
  "fname1": "CSU_ACN",
  "fname2": "SECOND_FUNC",
  "response_option": 2,
  "option1": "ACK",
  "option2": "NACK"
}
```

### 서버 종료

```json
{
  "command": "STOP"
}
```

---

## 📥 응답 JSON

### 성공

```json
{
  "result": "success",
  "vin": "KMHXX00XXXX000000",
  "fnames": ["CSU_ACN"],
  "response_type": 1,
  "options": ["ACK"],
  "timestamp": "2025-10-13T10:30:45.123456Z"
}
```

### 실패

```json
{
  "result": "error",
  "error_code": 1005,
  "error_message": "VIN not found in search results",
  "timestamp": "2025-10-13T10:30:45.123456Z"
}
```

---

## 🔧 파라미터 설명

| 필드 | 필수 | 타입 | 설명 | 예시 |
|------|------|------|------|------|
| `command` | ✅ | string | "START" 또는 "STOP" | `"START"` |
| `id` | ✅ | string | 로그인 아이디 | `"lge_1"` |
| `password` | ✅ | string | 로그인 비밀번호 | `"pass123"` |
| `vin` | ✅ | string | 차량 VIN (17자리) | `"KMHXX00..."` |
| `fname1` | ✅ | string | 1차 함수명 | `"CSU_ACN"` |
| `fname2` | ❌ | string/null | 2차 함수명 | `"FUNC2"` |
| `response_option` | ✅ | integer | 1, 2, 3 중 선택 | `1` |
| `option1` | ✅ | string | fname1 옵션값 | `"ACK"` |
| `option2` | ❌ | string/null | fname2 옵션값 (fname2 있고 response_option=2면 필수) | `"NACK"` |

**response_option**:
- `1` = Default (기본값)
- `2` = Custom (JSON 수정)
- `3` = No Response (무응답)

---

## 💻 코드 예제

### Python

```python
import socket
import json

def send_command(command_dict):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5000))
    
    # 전송
    sock.sendall(json.dumps(command_dict).encode('utf-8'))
    
    # 수신
    response = json.loads(sock.recv(8192).decode('utf-8'))
    sock.close()
    
    return response

# 실행
command = {
    "command": "START",
    "id": "lge_1",
    "password": "xxx",
    "vin": "KMHXX00XXXX000000",
    "fname1": "CSU_ACN",
    "fname2": None,
    "response_option": 1,
    "option1": "ACK",
    "option2": None
}

response = send_command(command)
print(response)
```


## ⚠️ 주요 에러 코드

| 코드 | 의미 | 해결 방법 |
|------|------|----------|
| `1002` | 로그인 실패 | 아이디/비밀번호 확인 |
| `1004` | 필수 파라미터 누락 | JSON 필드 확인 |
| `1005` | VIN 없음 | VIN 번호 확인 |
| `1006` | 함수명 없음 | 함수명 철자 확인 |
| `1007` | response_option 오류 | 1, 2, 3 중 하나 사용 |

---

## 📝 체크리스트

**보내기 전 확인**:
- [ ] UTF-8 인코딩
- [ ] `response_option`은 정수 (문자열 아님)
- [ ] 선택 필드는 `null` (빈 문자열 아님)
- [ ] VIN은 17자리
- [ ] `fname2` + `response_option=2`이면 `option2` 필수

**서버 실행**:
```bash
tsp_auto.exe --port 5000 --debug
```


