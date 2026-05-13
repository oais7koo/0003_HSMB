# Codex 리뷰 프롬프트 템플릿

ooreview에서 Codex CLI 호출 시 사용하는 프롬프트 모음.

## 사용법

```
/omc-teams 1:codex "[아래 템플릿 중 선택]"
```

또는 codex:rescue 에이전트:
```
Task(subagent_type="codex:rescue", prompt="[아래 템플릿]")
```

---

## 범용 리뷰

```
Review the following code and provide detailed feedback with specific line numbers.
Focus on:
1. Logic defects and edge cases (None, empty input, boundary values)
2. Race conditions or concurrency issues
3. Off-by-one errors in loops and index calculations
4. Resource leaks (file handles, connections, memory)
5. Timeout or infinite loop risks
6. Missing error handling

Code to review:
[파일 경로 또는 코드 붙여넣기]

Format: [SEVERITY][CATEGORY] filename:line — description
SEVERITY: CRITICAL / ERROR / WARNING / INFO
```

---

## 보안 집중 리뷰

```
Security audit the following code. Check for:
1. Injection vulnerabilities (SQL, Command, LDAP, XSS)
2. Authentication/authorization bypass
3. Sensitive data exposure (hardcoded secrets, logging PII)
4. Path traversal vulnerabilities
5. Input validation gaps
6. Insecure deserialization

Code:
[파일 경로 또는 코드]

Report only confirmed or highly probable issues with evidence.
```

---

## 성능 집중 리뷰

```
Performance review of the following code:
1. O(n²) or worse algorithmic complexity
2. Unnecessary repeated database/API calls (N+1 problem)
3. Memory-intensive operations that could be streamed
4. Missing caching opportunities
5. Synchronous blocking in async context
6. Large object creation in loops

Code:
[파일 경로 또는 코드]
```

---

## Python 특화

```
Python code review focusing on:
1. Mutable default arguments (def f(x=[]))
2. Exception swallowing (bare except:)
3. Global state misuse
4. Generator vs list misuse for large datasets
5. Missing __all__ in public modules
6. Type annotation gaps in public APIs

File: [파일 경로]
```

---

## Flutter/Dart 특화

```
Dart/Flutter code review:
1. setState() called after widget disposal
2. async gaps causing BuildContext issues
3. Missing dispose() for controllers/streams
4. Unnecessary rebuilds (missing const, selector misuse)
5. Platform-specific code without proper guards
6. Missing null safety handling

File: [파일 경로]
```
