#!/usr/bin/env bash
# 주차 작업 브랜치 만들기 (또는 이어서 작업하기)
#   사용법: scripts/new-week.sh 03
#   결과:  feat/week03 브랜치로 전환 + weeks/week03.html 준비 + 지시서 위치 안내
set -euo pipefail
n=$(printf "%02d" "$((10#${1:?주차 번호를 주세요. 예: scripts/new-week.sh 03}))")
id="week$n"; br="feat/$id"

git fetch origin --quiet
if git show-ref --verify --quiet "refs/remotes/origin/$br"; then
  git checkout -q -B "$br" "origin/$br"          # 원격에 있으면 그걸 기준으로
  echo "✓ 원격 브랜치 $br 를 가져왔습니다."
else
  git checkout -q -B "$br" "origin/main"         # 없으면 main 최신에서 새로
  echo "✓ main 최신에서 새 브랜치 $br 를 만들었습니다."
fi

if [ ! -f "weeks/$id.html" ]; then
  cp weeks/_template.html "weeks/$id.html"
  echo "✓ weeks/$id.html 을 템플릿에서 생성했습니다."
fi

cat <<MSG

  작업 파일   : weeks/$id.html
  지시서      : content/briefs/$id.md
  완성 예시   : weeks/week02.html
  로컬 확인   : python3 -m http.server 8080  →  http://localhost:8080/weeks/$id.html
  끝나면      : scripts/pr-week.sh $n
MSG
