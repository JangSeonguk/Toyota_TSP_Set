# TSP 브라우저 자동화 모듈 - TCP 통신 프로토콜 문서

**버전**: 1.0  
**최종 수정일**: 2025-10-13  
**대상 독자**: 외부 시스템 개발자

---

## 📋 목차

1. [개요](#개요)
2. [연결 방법](#연결-방법)
3. [요청 포맷](#요청-포맷)
4. [응답 포맷](#응답-포맷)
5. [에러 코드](#에러-코드)
6. [통신 시나리오](#통신-시나리오)
7. [언어별 구현 예제](#언어별-구현-예제)
8. [주의사항 및 제약](#주의사항-및-제약)

---

## 개요

### 목적
TSP 브라우저 자동화 모듈은 TCP/IP 통신을 통해 웹 브라우저 자동화 작업을 제어할 수 있는 서비스입니다.

### 주요 기능
- VIN 기반 차량 정보 검색
- 함수명(Function Name) 검색 및 선택
- 응답 옵션 설정 (Default / Custom / No Response)
- JSON 데이터 수정 및 업데이트
- 비동기 작업 처리 (큐잉)

### 기술 스펙
- **프로토콜**: TCP/IP
- **포트**: 5000 (기본값, 설정 가능)
- **데이터 포맷**: JSON
- **인코딩**: UTF-8
- **연결 모드**: 단일 클라이언트 연결 (순차 처리)

---

## 연결 방법

### 서버 시작
```bash
# 기본 포트(5000)로 시작
tsp_auto.exe --port 5000 --debug

# 다른 포트로 시작
tsp_auto.exe --port 8080 --debug
```

### 클라이언트 연결 절차

```
1. TCP 소켓 생성
2. 서버에 연결 (localhost:5000 또는 원격 IP:포트)
3. JSON 요청 전송 (UTF-8 인코딩)
4. JSON 응답 수신 (최대 8192 바이트)
5. 소켓 종료
```

**연결 정보**:
- **호스트**: `localhost` 또는 서버 IP
- **포트**: `5000` (기본값)
- **타임아웃**: 권장 30초

---

## 요청 포맷

### 요청 JSON 구조

#### 1. START 명령 (자동화 실행)

**필수 필드**:
```json
{
  "command": "START",
  "id": "string",
  "password": "string",
  "vin": "string",
  "fname1": "string",
  "response_option": 1,
  "option1": "string"
}
```

**전체 필드** (선택 필드 포함):
```json
{
  "command": "START",
  "id": "lge_1",
  "password": "your_password",
  "vin": "KMHXX00XXXX000000",
  "fname1": "CSU_ACN",
  "fname2": "OPTIONAL_FUNC",
  "response_option": 2,
  "option1": "ACK",
  "option2": "NACK"
}
```

**필드 설명**:

| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|------|------|------|
| `command` | string | ✅ | 명령 타입 (고정값: "START") | `"START"` |
| `id` | string | ✅ | 로그인 아이디 | `"lge_1"` |
| `password` | string | ✅ | 로그인 비밀번호 | `"password123"` |
| `vin` | string | ✅ | 차량 VIN 번호 (17자리) | `"KMHXX00XXXX000000"` |
| `fname1` | string | ✅ | 1차 함수명 | `"CSU_ACN"` |
| `fname2` | string | ❌ | 2차 함수명 (선택) | `"FUNC2"` 또는 `null` |
| `response_option` | integer | ✅ | 응답 옵션: 1, 2, 3 | `1` |
| `option1` | string | ✅ | fname1의 옵션 값 | `"ACK"` |
| `option2` | string | ❌ | fname2의 옵션 값 (fname2와 response_option=2일 때 필수) | `"NACK"` 또는 `null` |

**response_option 값**:
- `1`: **Default** - 기본 응답 옵션 (라디오 버튼 1번)
- `2`: **Custom** - 커스텀 응답 옵션 (라디오 버튼 2번, JSON 수정 필요)
- `3`: **No Response** - 무응답 옵션 (라디오 버튼 3번)

**검증 규칙**:
1. `command`는 반드시 `"START"` 또는 `"STOP"`
2. `response_option`은 반드시 1, 2, 3 중 하나 (정수)
3. `fname2`가 있고 `response_option=2`이면 `option2` 필수
4. 모든 문자열은 빈 문자열 불가 (null은 가능)

#### 2. STOP 명령 (서버 종료)

```json
{
  "command": "STOP"
}
```

**필드 설명**:
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `command` | string | ✅ | 명령 타입 (고정값: "STOP") |

---

## 응답 포맷

### 성공 응답

```json
{
  "result": "success",
  "vin": "KMHXX00XXXX000000",
  "fnames": ["CSU_ACN", "FUNC2"],
  "response_type": 2,
  "options": ["ACK", "NACK"],
  "timestamp": "2025-10-13T10:30:45.123456Z"
}
```

**필드 설명**:

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `result` | string | 결과 상태 (고정값: "success") | `"success"` |
| `vin` | string | 처리된 VIN | `"KMHXX00XXXX000000"` |
| `fnames` | array[string] | 처리된 함수명 목록 | `["CSU_ACN", "FUNC2"]` |
| `response_type` | integer | 사용된 응답 옵션 (1/2/3) | `2` |
| `options` | array[string] | 사용된 옵션 값 목록 | `["ACK", "NACK"]` |
| `timestamp` | string | 처리 완료 시각 (ISO 8601, UTC) | `"2025-10-13T10:30:45.123456Z"` |

### 에러 응답

```json
{
  "result": "error",
  "error_code": 1005,
  "error_message": "VIN not found in search results",
  "timestamp": "2025-10-13T10:30:45.123456Z"
}
```

**필드 설명**:

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| `result` | string | 결과 상태 (고정값: "error") | `"error"` |
| `error_code` | integer | 에러 코드 (1001-1011) | `1005` |
| `error_message` | string | 에러 메시지 (한글 또는 영문) | `"VIN not found in search results"` |
| `timestamp` | string | 에러 발생 시각 (ISO 8601, UTC) | `"2025-10-13T10:30:45.123456Z"` |

---

## 에러 코드

### 에러 코드 목록

| 코드 | 이름 | 설명 | 해결 방법 |
|------|------|------|----------|
| `1001` | TCP_CONNECTION_ERROR | TCP 연결 오류 | 서버 연결 상태 확인 |
| `1002` | LOGIN_FAILURE | 로그인 실패 (2회 재시도 후) | 아이디/비밀번호 확인 |
| `1003` | INVALID_COMMAND_FORMAT | 잘못된 명령 포맷 | JSON 포맷 및 필수 필드 확인 |
| `1004` | MISSING_REQUIRED_PARAMS | 필수 파라미터 누락 | 필수 필드 확인 (id, password, vin, fname1, response_option, option1) |
| `1005` | VIN_NOT_FOUND | VIN을 찾을 수 없음 | VIN 번호 확인 (17자리) |
| `1006` | FUNCTION_NAME_NOT_FOUND | 함수명을 찾을 수 없음 | 함수명 철자 확인 |
| `1007` | INVALID_RESPONSE_OPTION | 잘못된 response_option 값 | response_option은 1, 2, 3 중 하나 |
| `1008` | ELEMENT_WAIT_TIMEOUT | 웹 요소 대기 타임아웃 (10초) | 페이지 로딩 확인, 재시도 |
| `1009` | JSON_PARSING_ERROR | JSON 파싱/수정 오류 | JSON 데이터 확인 |
| `1010` | BROWSER_CRASH | 브라우저 크래시 | 서버 재시작 |
| `1011` | UNKNOWN_ERROR | 알 수 없는 오류 | 로그 확인, 서버 재시작 |

### 에러 처리 권장사항

1. **재시도 가능 에러** (일시적):
   - `1008` (ELEMENT_WAIT_TIMEOUT): 1-2회 재시도
   - `1010` (BROWSER_CRASH): 서버 재시작 후 재시도

2. **재시도 불가 에러** (설정 오류):
   - `1002` (LOGIN_FAILURE): 자격 증명 확인 필요
   - `1003`, `1004`, `1007` (검증 오류): 요청 수정 필요
   - `1005`, `1006` (데이터 오류): 입력 데이터 확인 필요

---

## 통신 시나리오

### 시나리오 1: 단일 함수 처리 (성공)

```
클라이언트                              서버
    |                                     |
    |----(1) TCP 연결 요청--------------->|
    |<---(2) 연결 수락--------------------|
    |                                     |
    |----(3) START 요청 전송------------->|
    |       {                             |
    |         "command": "START",         |
    |         "id": "lge_1",              |
    |         "password": "xxx",          |--- 로그인 시도 (재시도 최대 2회)
    |         "vin": "KMHXX00...",        |
    |         "fname1": "CSU_ACN",        |--- VIN 검색
    |         "fname2": null,             |
    |         "response_option": 1,       |--- 함수명 검색 및 처리
    |         "option1": "ACK",           |
    |         "option2": null             |--- 라디오 버튼 선택
    |       }                             |
    |                                     |--- 업데이트 버튼 클릭
    |                                     |
    |<---(4) 성공 응답 수신----------------|
    |       {                             |
    |         "result": "success",        |
    |         "vin": "KMHXX00...",        |
    |         "fnames": ["CSU_ACN"],      |
    |         "response_type": 1,         |
    |         "options": ["ACK"],         |
    |         "timestamp": "..."          |
    |       }                             |
    |                                     |
    |----(5) 연결 종료------------------->|
```

### 시나리오 2: 이중 함수 처리 (Custom 옵션)

```
클라이언트                              서버
    |                                     |
    |----(1) TCP 연결----------------------->|
    |                                     |
    |----(2) START 요청 (fname2 포함)----->|
    |       {                             |
    |         "command": "START",         |
    |         "fname1": "CSU_ACN",        |
    |         "fname2": "FUNC2",          |--- fname1 처리
    |         "response_option": 2,       |
    |         "option1": "ACK",           |--- JSON 수정 (option1="ACK")
    |         "option2": "NACK"           |
    |       }                             |--- fname2 처리
    |                                     |
    |                                     |--- JSON 수정 (option2="NACK")
    |                                     |
    |<---(3) 성공 응답---------------------|
    |       {                             |
    |         "fnames": ["CSU_ACN", "FUNC2"],
    |         "options": ["ACK", "NACK"]  |
    |       }                             |
```

### 시나리오 3: VIN 찾기 실패

```
클라이언트                              서버
    |                                     |
    |----(1) TCP 연결----------------------->|
    |                                     |
    |----(2) START 요청 (잘못된 VIN)------>|
    |       {                             |
    |         "vin": "INVALID_VIN",       |--- 로그인 성공
    |         ...                         |
    |       }                             |--- VIN 검색 실패
    |                                     |
    |<---(3) 에러 응답---------------------|
    |       {                             |
    |         "result": "error",          |
    |         "error_code": 1005,         |
    |         "error_message": "VIN not found..."
    |       }                             |
    |                                     |
    |----(4) 연결 종료------------------->|
```

### 시나리오 4: 서버 종료

```
클라이언트                              서버
    |                                     |
    |----(1) STOP 명령-------------------->|
    |       {                             |
    |         "command": "STOP"           |--- 작업 큐 비우기
    |       }                             |
    |                                     |--- 브라우저 종료
    |<---(2) 종료 확인 응답----------------|
    |       {                             |
    |         "result": "success",        |
    |         "message": "Stopping server"|
    |       }                             |
    |                                     |--- 서버 종료
```

---

## 언어별 구현 예제

### Python

```python
import socket
import json

def send_command(command_dict, host='localhost', port=5000):
    """TSP 서버에 명령 전송"""
    # 소켓 생성 및 연결
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    
    try:
        # JSON 직렬화 및 전송
        command_json = json.dumps(command_dict)
        sock.sendall(command_json.encode('utf-8'))
        
        # 응답 수신
        response_data = sock.recv(8192)
        response = json.loads(response_data.decode('utf-8'))
        
        return response
    finally:
        sock.close()

# 사용 예시
command = {
    "command": "START",
    "id": "lge_1",
    "password": "your_password",
    "vin": "KMHXX00XXXX000000",
    "fname1": "CSU_ACN",
    "fname2": None,
    "response_option": 1,
    "option1": "ACK",
    "option2": None
}

try:
    response = send_command(command)
    if response['result'] == 'success':
        print(f"성공: VIN={response['vin']}, 함수={response['fnames']}")
    else:
        print(f"실패: 코드={response['error_code']}, 메시지={response['error_message']}")
except Exception as e:
    print(f"통신 오류: {e}")
```

### C# (.NET)

```csharp
using System;
using System.Net.Sockets;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

public class TspClient
{
    private string _host;
    private int _port;
    
    public TspClient(string host = "localhost", int port = 5000)
    {
        _host = host;
        _port = port;
    }
    
    public JObject SendCommand(object command)
    {
        using (var client = new TcpClient(_host, _port))
        using (var stream = client.GetStream())
        {
            // JSON 직렬화 및 전송
            string jsonCommand = JsonConvert.SerializeObject(command);
            byte[] data = Encoding.UTF8.GetBytes(jsonCommand);
            stream.Write(data, 0, data.Length);
            
            // 응답 수신
            byte[] buffer = new byte[8192];
            int bytesRead = stream.Read(buffer, 0, buffer.Length);
            string responseJson = Encoding.UTF8.GetString(buffer, 0, bytesRead);
            
            return JObject.Parse(responseJson);
        }
    }
}

// 사용 예시
class Program
{
    static void Main()
    {
        var client = new TspClient("localhost", 5000);
        
        var command = new
        {
            command = "START",
            id = "lge_1",
            password = "your_password",
            vin = "KMHXX00XXXX000000",
            fname1 = "CSU_ACN",
            fname2 = (string)null,
            response_option = 1,
            option1 = "ACK",
            option2 = (string)null
        };
        
        try
        {
            var response = client.SendCommand(command);
            
            if (response["result"].ToString() == "success")
            {
                Console.WriteLine($"성공: VIN={response["vin"]}");
            }
            else
            {
                Console.WriteLine($"실패: 코드={response["error_code"]}, 메시지={response["error_message"]}");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"통신 오류: {ex.Message}");
        }
    }
}
```

### Java

```java
import java.io.*;
import java.net.*;
import com.google.gson.*;

public class TspClient {
    private String host;
    private int port;
    private Gson gson;
    
    public TspClient(String host, int port) {
        this.host = host;
        this.port = port;
        this.gson = new Gson();
    }
    
    public JsonObject sendCommand(JsonObject command) throws IOException {
        try (Socket socket = new Socket(host, port);
             PrintWriter out = new PrintWriter(
                 new OutputStreamWriter(socket.getOutputStream(), "UTF-8"), true);
             BufferedReader in = new BufferedReader(
                 new InputStreamReader(socket.getInputStream(), "UTF-8"))) {
            
            // JSON 전송
            String jsonCommand = gson.toJson(command);
            out.println(jsonCommand);
            
            // 응답 수신
            String responseLine = in.readLine();
            return gson.fromJson(responseLine, JsonObject.class);
        }
    }
    
    // 사용 예시
    public static void main(String[] args) {
        TspClient client = new TspClient("localhost", 5000);
        
        JsonObject command = new JsonObject();
        command.addProperty("command", "START");
        command.addProperty("id", "lge_1");
        command.addProperty("password", "your_password");
        command.addProperty("vin", "KMHXX00XXXX000000");
        command.addProperty("fname1", "CSU_ACN");
        command.add("fname2", null);
        command.addProperty("response_option", 1);
        command.addProperty("option1", "ACK");
        command.add("option2", null);
        
        try {
            JsonObject response = client.sendCommand(command);
            
            if (response.get("result").getAsString().equals("success")) {
                System.out.println("성공: VIN=" + response.get("vin").getAsString());
            } else {
                System.out.println("실패: 코드=" + response.get("error_code").getAsInt());
            }
        } catch (IOException e) {
            System.err.println("통신 오류: " + e.getMessage());
        }
    }
}
```

### Node.js (JavaScript)

```javascript
const net = require('net');

class TspClient {
    constructor(host = 'localhost', port = 5000) {
        this.host = host;
        this.port = port;
    }
    
    sendCommand(command) {
        return new Promise((resolve, reject) => {
            const client = net.createConnection(
                { host: this.host, port: this.port }, 
                () => {
                    // JSON 전송
                    const jsonCommand = JSON.stringify(command);
                    client.write(jsonCommand);
                }
            );
            
            // 응답 수신
            client.on('data', (data) => {
                const response = JSON.parse(data.toString('utf-8'));
                client.end();
                resolve(response);
            });
            
            client.on('error', (err) => {
                reject(err);
            });
        });
    }
}

// 사용 예시
(async () => {
    const client = new TspClient('localhost', 5000);
    
    const command = {
        command: "START",
        id: "lge_1",
        password: "your_password",
        vin: "KMHXX00XXXX000000",
        fname1: "CSU_ACN",
        fname2: null,
        response_option: 1,
        option1: "ACK",
        option2: null
    };
    
    try {
        const response = await client.sendCommand(command);
        
        if (response.result === 'success') {
            console.log(`성공: VIN=${response.vin}, 함수=${response.fnames}`);
        } else {
            console.log(`실패: 코드=${response.error_code}, 메시지=${response.error_message}`);
        }
    } catch (err) {
        console.error('통신 오류:', err);
    }
})();
```

### PowerShell

```powershell
function Send-TspCommand {
    param(
        [Parameter(Mandatory=$true)]
        [hashtable]$Command,
        [string]$Host = "localhost",
        [int]$Port = 5000
    )
    
    try {
        # TCP 연결
        $client = New-Object System.Net.Sockets.TcpClient($Host, $Port)
        $stream = $client.GetStream()
        
        # JSON 직렬화 및 전송
        $jsonCommand = $Command | ConvertTo-Json -Compress -Depth 10
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonCommand)
        $stream.Write($bytes, 0, $bytes.Length)
        
        # 응답 수신
        $buffer = New-Object byte[] 8192
        $bytesRead = $stream.Read($buffer, 0, $buffer.Length)
        $responseJson = [System.Text.Encoding]::UTF8.GetString($buffer, 0, $bytesRead)
        
        # JSON 역직렬화
        $response = $responseJson | ConvertFrom-Json
        
        return $response
    }
    finally {
        if ($stream) { $stream.Close() }
        if ($client) { $client.Close() }
    }
}

# 사용 예시
$command = @{
    command = "START"
    id = "lge_1"
    password = "your_password"
    vin = "KMHXX00XXXX000000"
    fname1 = "CSU_ACN"
    fname2 = $null
    response_option = 1
    option1 = "ACK"
    option2 = $null
}

try {
    $response = Send-TspCommand -Command $command
    
    if ($response.result -eq "success") {
        Write-Host "성공: VIN=$($response.vin), 함수=$($response.fnames -join ', ')"
    } else {
        Write-Host "실패: 코드=$($response.error_code), 메시지=$($response.error_message)"
    }
} catch {
    Write-Error "통신 오류: $_"
}
```

---

## 주의사항 및 제약

### 연결 제약
1. **단일 연결**: 서버는 한 번에 하나의 클라이언트만 처리합니다.
2. **순차 처리**: 여러 요청은 큐에 쌓여 순차적으로 처리됩니다.
3. **블로킹 방식**: 작업이 완료될 때까지 응답이 지연될 수 있습니다 (최대 30초).
4. **재연결**: 작업 완료 후 연결이 종료되면 재연결이 필요합니다.

### 데이터 제약
1. **VIN 형식**: 17자리 영숫자 (예: `KMHXX00XXXX000000`)
2. **함수명**: 대소문자 정확히 일치해야 함
3. **응답 버퍼**: 최대 8192 바이트
4. **인코딩**: 반드시 UTF-8 사용
5. **JSON null**: 선택 필드는 `null` 사용 (빈 문자열 `""` 아님)

### 타임아웃
1. **로그인**: 최대 20초 (재시도 포함)
2. **VIN 검색**: 최대 10초
3. **함수명 검색**: 최대 10초
4. **전체 작업**: 최대 30초

### 에러 처리
1. **자동 재시도**: 로그인은 최대 2회 자동 재시도
2. **복구 불가**: 브라우저 크래시 시 서버 재시작 필요
3. **로그 확인**: `--debug` 플래그로 상세 로그 확인 가능

### 보안
1. **평문 전송**: 현재 버전은 비밀번호를 평문으로 전송합니다.
2. **내부망 권장**: 외부 네트워크 노출 시 VPN 또는 방화벽 사용 권장
3. **접근 제어**: 서버는 모든 IP(`0.0.0.0`)에서 연결 허용

### 성능
1. **브라우저 재사용**: 로그인 상태가 유지되면 재로그인 생략 (2초 단축)
2. **큐 크기**: 큐 크기 제한 없음 (메모리 허용 범위)
3. **동시 실행**: 불가 (순차 처리만 가능)

### 권장 사항
1. **타임아웃 설정**: 클라이언트는 최소 30초 타임아웃 설정
2. **재시도 로직**: 일시적 에러(1008)는 1-2회 재시도
3. **연결 관리**: 작업 완료 후 즉시 소켓 종료
4. **에러 로깅**: 에러 응답 저장 및 모니터링

---

## 부록

### 전체 예제 (Python)

```python
import socket
import json
import time

class TspAutomationClient:
    """TSP 브라우저 자동화 클라이언트"""
    
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
    
    def send_command(self, command_dict, timeout=30):
        """명령 전송 및 응답 수신"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        try:
            sock.connect((self.host, self.port))
            
            # 전송
            command_json = json.dumps(command_dict)
            sock.sendall(command_json.encode('utf-8'))
            
            # 수신
            response_data = sock.recv(8192)
            response = json.loads(response_data.decode('utf-8'))
            
            return response
        finally:
            sock.close()
    
    def execute_automation(self, vin, fname1, option1, 
                          fname2=None, option2=None, 
                          response_option=1,
                          credentials=None):
        """자동화 실행"""
        if credentials is None:
            raise ValueError("자격 증명이 필요합니다")
        
        command = {
            "command": "START",
            "id": credentials['id'],
            "password": credentials['password'],
            "vin": vin,
            "fname1": fname1,
            "fname2": fname2,
            "response_option": response_option,
            "option1": option1,
            "option2": option2
        }
        
        response = self.send_command(command)
        
        if response['result'] == 'success':
            return {
                'success': True,
                'data': response
            }
        else:
            return {
                'success': False,
                'error_code': response['error_code'],
                'error_message': response['error_message']
            }
    
    def stop_server(self):
        """서버 종료"""
        command = {"command": "STOP"}
        return self.send_command(command)

# 사용 예시
if __name__ == "__main__":
    client = TspAutomationClient("localhost", 5000)
    
    credentials = {
        'id': 'lge_1',
        'password': 'your_password'
    }
    
    # 단일 함수 처리
    result = client.execute_automation(
        vin="KMHXX00XXXX000000",
        fname1="CSU_ACN",
        option1="ACK",
        response_option=1,
        credentials=credentials
    )
    
    if result['success']:
        print(f"성공! VIN: {result['data']['vin']}")
        print(f"처리된 함수: {result['data']['fnames']}")
    else:
        print(f"실패! 코드: {result['error_code']}")
        print(f"메시지: {result['error_message']}")
```

### 문의 및 지원

**문서 버전**: 1.0  
**최종 업데이트**: 2025-10-13  

**문의사항**:
- 기술 지원: 프로젝트 README 참조
- 버그 리포트: 로그 파일과 함께 제출

---

**© 2025 TSP Browser Automation Module**



