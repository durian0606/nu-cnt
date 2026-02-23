# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

[프로젝트 설명 작성 필요]

**Language**: [주 사용 언어]
**Status**: 초기 개발 단계

### 주요 기능
- [기능 1]
- [기능 2]
- [기능 3]

---

## 기술 스택

- **프로그래밍 언어**: [예: Python, JavaScript, TypeScript]
- **프레임워크**: [예: React, Vue, Django, Flask]
- **데이터베이스**: [예: PostgreSQL, MySQL, Firebase, LocalStorage]
- **배포 환경**: [예: Vercel, AWS, Docker]
- **주요 라이브러리**: [라이브러리 목록]

---

## 개발 환경 설정

### 의존성 설치
```bash
# Python 프로젝트인 경우
pip install -r requirements.txt

# Node.js 프로젝트인 경우
npm install
# 또는
yarn install

# 기타 언어/프레임워크의 경우
[설치 명령어 작성]
```

### 개발 서버 실행
```bash
# 개발 서버 시작
[명령어 작성 필요]

# 예시:
# python main.py
# npm run dev
# yarn dev
```

### 빌드 및 배포
```bash
# 프로덕션 빌드
[빌드 명령어 작성 필요]

# 배포
[배포 명령어 작성 필요]
```

---

## 프로젝트 구조

```
gamgi/
├── [주요 파일/디렉토리 설명]
│
├── [Python 프로젝트인 경우]
│   ├── config/           # 설정 파일
│   ├── models/           # 데이터 모델
│   ├── services/         # 비즈니스 로직
│   ├── utils/            # 유틸리티 함수
│   └── main.py           # 진입점
│
├── [웹 프로젝트인 경우]
│   ├── index.html
│   ├── css/
│   │   ├── styles.css
│   │   └── variables.css
│   ├── js/
│   │   ├── models/       # 데이터 모델
│   │   ├── services/     # 비즈니스 로직
│   │   ├── ui/           # UI 컴포넌트
│   │   └── utils/        # 유틸리티
│   └── assets/
│
└── [기타]
    ├── tests/            # 테스트 파일
    ├── docs/             # 문서
    └── .gitignore
```

---

## 아키텍처

### 전체 구조
[프로젝트의 고수준 아키텍처 설명]
- 주요 컴포넌트 간 상호작용
- 데이터 흐름
- 외부 API/서비스 연동

### 주요 컴포넌트
- **[컴포넌트명 1]**: [역할 및 책임 설명]
- **[컴포넌트명 2]**: [역할 및 책임 설명]
- **[컴포넌트명 3]**: [역할 및 책임 설명]

### 데이터 저장소
- **저장 방식**: [LocalStorage / Firebase / Database / File]
- **데이터 모델**: [주요 데이터 구조 설명]

```javascript
// 예시: 데이터 구조
{
  "items": [
    {
      "id": "uuid",
      "name": "예시",
      "createdAt": "2025-02-20T00:00:00.000Z"
    }
  ]
}
```

---

## 개발 작업

### 테스트 실행
```bash
# 모든 테스트 실행
[테스트 명령어]

# 특정 테스트 실행
[단일 테스트 명령어]

# 예시:
# pytest tests/
# npm test
# yarn test
```

### 코드 품질 검사
```bash
# 린팅
[린터 명령어]

# 포맷팅
[포맷터 명령어]

# 예시:
# pylint src/
# eslint src/
# prettier --write src/
```

### 디버깅
- [디버깅 방법 설명]
- [로깅 설정]
- [일반적인 디버깅 팁]

---

## 중요 구현 사항

### 코딩 컨벤션
- **들여쓰기**: [스페이스/탭, 개수]
- **변수명**: [camelCase / snake_case / PascalCase]
- **파일명**: [kebab-case / snake_case / PascalCase]
- **주석**: [주석 작성 규칙]

### 보안 고려사항
- **Credentials 관리**: API 키, 비밀번호 등은 별도 파일로 관리
  - Python: `credentials.py`, `.env`
  - JavaScript: `config.js`, `.env`
  - 반드시 `.gitignore`에 추가
- **민감 정보 처리**: [보안 관련 특이사항]

### 성능 최적화
- [성능 관련 중요 사항]
- [최적화 팁]

### 알려진 제약사항
- [특정 환경에서의 제약]
- [해결 방법 또는 대안]

---

## Git 작업 흐름

### 브랜치 전략
- `main` - 프로덕션 코드
- `develop` - 개발 브랜치
- `feature/*` - 기능 개발

### 커밋 메시지 형식
```
<type>: <description>

[optional body]

[optional footer]
```

**Type:**
- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

---

## 자주 묻는 질문 (FAQ)

### [질문 1]
[답변]

### [질문 2]
[답변]

---

## 참고 자료

- [관련 문서 링크]
- [외부 API 문서]
- [참고한 프로젝트]

---

**마지막 업데이트**: 2025-02-20
**버전**: 0.1.0
