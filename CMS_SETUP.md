# CMS 로그인 연결 안내

CMS 화면은 `/admin/`에 있고, GitHub 저장소를 CMS 저장소로 사용합니다. GitHub Pages는 정적 파일만 제공하므로 CMS 인증에는 별도 인증 백엔드가 필요합니다. 이 사이트는 OAuth 서버를 직접 운영하지 않아도 되는 Decap Turbo를 사용하도록 준비되어 있습니다.

## 최초 한 번 연결하기

1. [Decap Turbo 설정 안내](https://decapcms.org/docs/turbo-getting-started/)를 열고 Decap Turbo 계정을 만듭니다. 약관 동의가 나오면 내용을 확인한 뒤 직접 동의해 주세요.
2. Turbo 대시보드에서 조직을 만들고 **Git connection**에서 GitHub를 연결합니다.
3. GitHub 앱 설치 화면에서는 전체 저장소 대신 `jeus1998/jeus1998.github.io`만 선택합니다. CMS는 새 글과 이미지를 이 저장소에 커밋하므로 해당 저장소에 대한 쓰기 권한이 필요합니다.
4. Turbo에서 사이트를 추가하고 다음 값을 지정합니다.
   - Git provider: GitHub
   - Repository: `jeus1998/jeus1998.github.io`
   - Branch: `main`
   - Config path: `admin/config.yml`
   - Admin interface URL: `https://jeus1998.github.io/admin/`
5. 생성된 Site ID(UUID)를 복사해 `admin/config.yml`의 `backend.turbo_site_id`에 있는 `SETUP_REQUIRED`를 바꿉니다.
6. `main`에 커밋하면 Pages가 다시 배포됩니다. 이후 `https://jeus1998.github.io/admin/`에서 로그인해 글을 작성할 수 있습니다.

## 이미지 저장 위치

본문에 이미지를 드래그하면 CMS가 WebP로 변환하고, 해당 글의 날짜와 주소를 사용한 폴더에 저장합니다. 예: `assets/images/2026/11/24/spring-batch-retry/`. 글마다 폴더가 달라서 서로 다른 글에서 같은 파일명을 써도 경로가 겹치지 않습니다. CMS가 업로드 파일명을 URL에 쓸 수 있게 정리합니다.

현재 CMS 기본 업로더는 같은 글 폴더 안에서 같은 파일명을 다시 올리면 교체 여부를 확인합니다. 새 이미지로 교체하고 싶다면 원본 파일명을 바꾼 뒤 올려 주세요.
