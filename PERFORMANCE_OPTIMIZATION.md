# 성능 최적화 가이드

## ChromeDriver 로딩 시간 최적화

### 현재 동작 방식

#### webdriver-manager 사용 시 (기본값)

**첫 실행:**
- `ChromeDriverManager().install()` 호출
- Chrome 브라우저 버전 확인 (~0.5초)
- 해당 버전의 ChromeDriver 다운로드 (인터넷 연결 필요, 5~30초)
- 캐시 디렉토리에 저장: `C:\Users\{username}\.wdm\drivers\chromedriver\{version}\`

**두 번째 실행 이후:**
- 캐시 확인 및 버전 체크 (~0.5~1초)
- 캐시된 ChromeDriver 경로 반환
- 브라우저 시작

**총 시간:**
- 첫 실행: 5~30초 (다운로드 속도에 따라)
- 이후 실행: 0.5~1초

### 최적화 방법

#### 방법 1: 캐시 활용 (현재 방식, 별도 설정 불필요)

**장점:**
- 추가 설정 불필요
- Chrome 업데이트 시 자동으로 새 버전 다운로드
- 사용자별로 독립적인 캐시

**단점:**
- 첫 실행 시 다운로드 시간 필요
- 캐시 체크로 인한 약간의 지연 (0.5~1초)

#### 방법 2: ChromeDriver 직접 지정 (최대 성능)

**설정 방법:**

1. ChromeDriver 다운로드
   - https://googlechromelabs.github.io/chrome-for-testing/
   - Chrome 버전에 맞는 ChromeDriver 다운로드

2. `config.py` 수정:
```python
CHROMEDRIVER_PATH = r"C:\path\to\chromedriver.exe"
```

**장점:**
- 최대 성능 (캐시 체크 없음, 즉시 시작)
- 오프라인 환경에서 사용 가능
- 버전 고정으로 안정성 향상

**단점:**
- Chrome 업데이트 시 수동으로 ChromeDriver 업데이트 필요
- 배포 시 ChromeDriver 파일 포함 필요

**총 시간:**
- 모든 실행: ~0.1초 (거의 즉시)

#### 방법 3: exe와 함께 ChromeDriver 배포

**배포 구조:**
```
배포폴더/
├── tsp_auto.exe
└── chromedriver.exe
```

**config.py 설정:**
```python
import os
import sys

# Get directory where exe is located
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")
```

**장점:**
- exe와 동일한 폴더에서 관리 편리
- 상대 경로로 자동 설정
- 이식성 우수

**단점:**
- Chrome 버전 관리 필요
- 배포 패키지 크기 증가 (~10MB)

### 성능 비교표

| 방법 | 첫 실행 | 이후 실행 | 오프라인 | 유지보수 |
|------|---------|-----------|----------|----------|
| webdriver-manager (기본) | 5~30초 | 0.5~1초 | ❌ | 자동 |
| ChromeDriver 직접 지정 | ~0.1초 | ~0.1초 | ✅ | 수동 |
| exe와 함께 배포 | ~0.1초 | ~0.1초 | ✅ | 수동 |

### 권장 사항

**개발 환경:**
- webdriver-manager 사용 (기본값)
- 자동 업데이트로 최신 상태 유지

**프로덕션 환경:**
- ChromeDriver 직접 지정 또는 exe와 함께 배포
- 최대 성능 및 안정성
- 정기적으로 Chrome/ChromeDriver 버전 업데이트

## 기타 최적화

### 브라우저 재사용

브라우저는 싱글톤 패턴으로 관리되어 이미 실행 중이면 재사용됩니다:
- 로그인 후 브라우저를 종료하지 않고 유지
- 다음 명령 실행 시 로그인 스킵
- VIN 입력 페이지에서 바로 시작

### 디버그 모드 비활성화

프로덕션 환경에서는 `config.py`의 `DEBUG_MODE`를 `False`로 설정:
```python
DEBUG_MODE = False  # 2초 인터벌 비활성화
```

## 문제 해결

### Chrome 버전 불일치

**증상:**
```
SessionNotCreatedException: Message: session not created:
This version of ChromeDriver only supports Chrome version XX
```

**해결:**
1. Chrome 브라우저 버전 확인 (chrome://version)
2. 해당 버전의 ChromeDriver 다운로드
3. `config.py`에 경로 설정

### 캐시 손상

**증상:**
webdriver-manager가 반복적으로 다운로드 시도

**해결:**
캐시 디렉토리 삭제 후 재실행:
```bash
rmdir /s "%USERPROFILE%\.wdm"
```
