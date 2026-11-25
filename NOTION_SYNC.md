# Study Record Notion 동기화 준비

`scripts/notion_sync.py`는 `Study Record` 아래 페이지를 재귀적으로 읽어 Jekyll 글과 분류로 저장합니다. `.github/workflows/sync-notion.yml`은 매시간 동기화를 실행하며, Actions의 **Run workflow**로 수동 실행도 할 수 있습니다.

## 처음 한 번만 설정

1. Notion에서 [내 통합](https://www.notion.so/profile/integrations)에 들어가 **새 통합**을 만듭니다. 이름은 `Jeus Log Sync`처럼 알아보기 쉽게 정하고, `Study Record`가 있는 워크스페이스를 선택합니다.
2. 통합 권한은 콘텐츠 읽기만 켭니다. 쓰기와 사용자 정보 권한은 필요하지 않습니다.
3. 통합의 비밀 토큰을 복사합니다. 이 토큰을 채팅이나 공개 저장소에 붙여 넣지 마세요.
4. Notion의 `Study Record` 페이지에서 **공유 → 초대**를 열고 방금 만든 통합을 초대합니다. 상위 페이지에 연결하면 API가 하위 페이지를 읽을 수 있습니다.
5. GitHub에서 [`jeus1998/jeus1998.github.io` 저장소 설정](https://github.com/jeus1998/jeus1998.github.io/settings/secrets/actions)을 열고 **New repository secret**을 누릅니다. 이름은 `NOTION_API_KEY`, 값은 3단계에서 복사한 토큰으로 저장합니다.
6. 저장소의 **Actions → Sync Study Record from Notion → Run workflow**를 눌러 최초 동기화를 실행합니다. 완료되면 블로그에 글이 게시되고, 이후에는 매시간 자동으로 확인합니다.

`NOTION_ROOT_PAGE_ID`는 workflow에 이미 설정되어 있습니다. 토큰 값은 워크플로 로그에도 출력되지 않습니다.

## 변환 범위와 공개 여부

- 하위 페이지를 재귀적으로 가져오며 Notion 페이지 ID를 기준으로 기존 글을 갱신합니다. 새 페이지는 새 글이 됩니다. Notion에서 삭제된 페이지의 가져온 글과 분류는 다음 동기화에서 제거됩니다.
- 계층의 분류 페이지를 블로그 카테고리로 만들고, 글에는 상위 분류 경로를 기록합니다.
- 문단, 제목, 목록, 체크리스트, 코드, 인용문, 구분선, 이미지, 첨부 파일, 북마크, 표를 Markdown 또는 링크로 변환합니다. Notion 데이터베이스의 행과 뷰, 일부 고급 블록은 현재 변환 대상이 아니며 따로 검토해야 합니다.
- Notion에 업로드된 이미지는 GitHub 저장소에 복사됩니다. 외부 이미지 URL은 외부 주소를 참조합니다.
- 가져온 글과 이미지 및 분류는 공개 저장소와 GitHub Pages에 게시됩니다. 최초 실행 전 공개해도 되는 하위 페이지인지 확인하세요.
- 동기화된 `_posts/*-notion-*.md` 파일을 CMS에서 직접 편집하면 다음 실행 때 Notion 내용으로 덮어씁니다. 편집은 Notion에서 하세요. 일반 블로그 글은 영향을 받지 않습니다.

## 실행 실패 시

GitHub 저장소의 **Actions → Sync Study Record from Notion**에서 실패한 실행을 열면 오류 단계가 보입니다. `NOTION_API_KEY` 누락, Notion 페이지에 통합 초대 누락, 또는 통합의 읽기 권한 부족이 흔한 원인입니다. 토큰을 새로 발급했다면 GitHub secret을 교체한 뒤 workflow를 다시 실행하세요.
