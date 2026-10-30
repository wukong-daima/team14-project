#!/usr/bin/env bash
# 주차 작업을 커밋·푸시하고 main 으로 PR 올리기
#   사용법: scripts/pr-week.sh 03 ["커밋 메시지"]
set -euo pipefail
n=$(printf "%02d" "$((10#${1:?주차 번호를 주세요. 예: scripts/pr-week.sh 03}))")
id="week$n"; br="feat/$id"; msg="${2:-$id: 콘텐츠 작업}"

cur=$(git rev-parse --abbrev-ref HEAD)
[ "$cur" = "$br" ] || { echo "현재 브랜치가 $cur 입니다. 먼저 scripts/new-week.sh $n 을 실행하세요."; exit 1; }

git add -A
git diff --cached --quiet || git commit -m "$msg"
git push -u origin "$br"

if gh pr view "$br" >/dev/null 2>&1; then
  echo "✓ 이미 PR이 있습니다. 푸시만 반영했습니다."; gh pr view "$br" --web 2>/dev/null || true
else
  gh pr create --base main --head "$br" --title "$msg" --body-file .github/pull_request_template.md
fi
