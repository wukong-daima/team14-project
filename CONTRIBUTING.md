# 작업 규칙 (3명 협업)

## 브랜치

- `main` = 배포 브랜치. 직접 푸시 금지, PR 로만 머지.
- 작업 브랜치: `feat/weekNN` (주차), `feat/site` (공통), `fix/...` (수정).
- 한 주차 = 한 파일(`weeks/weekNN.html`) 이므로 다른 사람과 충돌할 일이 거의 없습니다.
  **공통 파일**(`assets/`, `index.html`, `slides/`)을 고칠 때는 PR 설명에 이유를 쓰고 통합 담당(손)이 리뷰합니다.

## 새 주차 만들기

```bash
git checkout main && git pull
git checkout -b feat/week03
cp weeks/_template.html weeks/week03.html
# content/briefs/week03.md 를 열어 두고 템플릿의 [1]~[10] 슬롯을 채웁니다
python3 -m http.server 8080   # 로컬 확인
git add weeks/week03.html && git commit -m "week03: 1차 콘텐츠"
git push -u origin feat/week03
gh pr create --fill --base main
```

`assets/js/weeks.js` 의 해당 주차 `status` 를 `"todo"` → `"done"` 으로 바꾸는 것도 잊지 마세요.

## 주차 페이지 완성 체크리스트 (PR 올리기 전)

- [ ] 한 줄 요약이 전공/쉬운 두 벌 있다
- [ ] 개념 카드 6개 이상, 각각 전공/쉬운 두 벌 + 도형 1개 이상
- [ ] 요약본과 원본이 다른 곳에 `callout fix` 박스를 넣었다 (브리프의 "요약본 정정" 참고)
- [ ] 대표 인터랙션 1개가 슬라이더/버튼으로 동작하고, 모바일 폭에서도 깨지지 않는다
- [ ] 모델 비교표에 추측이 없다. 모르는 칸은 `비공개`, 2차 자료는 `확인 필요` 배지
- [ ] 시험 포인트 5개 이상 + 예상 문제 5개 (정답 포함)
- [ ] 출처 목록이 있다
- [ ] 헤더의 "중학생 수준으로 이해하기" 버튼을 눌러 전체를 한 번 읽어봤다
- [ ] 다크 모드에서 SVG 글자가 보인다 (`fill="currentColor"` 사용)

## Claude Code 로 작업할 때 권장 프롬프트

```
weeks/_template.html 을 복사해 weeks/week03.html 을 만들어줘.
내용은 content/briefs/week03.md 를 기준으로 하고, 템플릿의 [1]~[10] 슬롯을 모두 채워.
전공 설명과 중학생 설명을 반드시 두 벌 작성하고, 모델 비교표는 브리프에 "확인 필요"로
표시된 항목을 그대로 "확인 필요" 배지로 남겨. 추측으로 칸을 채우지 마.
인터랙션은 브리프의 "대표 인터랙션"을 순수 JS + SVG 로 구현해.
```

## 리뷰

- 리뷰어 1명 승인 후 머지. 내용 정확성(원본 대조) 1회, 쉬운 모드 읽기 1회.
- 머지 후 1~2분 뒤 https://wukong-daima.github.io/team14-project/ 에서 확인.
