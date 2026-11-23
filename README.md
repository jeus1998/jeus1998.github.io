# Jeus Log

한국어 개발 기록을 위한 Jekyll 기반 GitHub Pages 블로그입니다.

**블로그 바로가기: [https://jeus1998.github.io](https://jeus1998.github.io)**

## 새 글 작성하기

블로그 화면 자체에는 글쓰기 버튼이나 로그인 편집기가 없습니다. 대신 GitHub 웹에서 글 파일을 추가하면 됩니다. 컴퓨터에 개발 도구를 설치하지 않아도 브라우저만으로 작성할 수 있어요.

### GitHub 웹에서 작성

1. [블로그 저장소](https://github.com/jeus1998/jeus1998.github.io)에 접속하고 `_posts` 폴더를 엽니다.
2. **Add file → Create new file**을 선택합니다.
3. 파일 이름을 `_posts/YYYY-MM-DD-영문-주소.md` 형식으로 입력합니다. 예: `_posts/2026-11-24-spring-batch-retry.md`.
4. 아래 글 틀을 붙여 넣고 제목, 날짜, 분류, 태그, 소개와 본문을 바꿉니다.
5. 페이지 아래 **Commit changes**를 눌러 `main` 브랜치에 저장합니다. 몇 분 뒤 블로그에 반영됩니다.

````markdown
---
layout: post
title: "Spring Batch 재시도 정리"
date: 2026-11-24 20:00:00 +0900
categories: [Spring]
tags: [Java, Spring Batch, 재시도]
description: "Spring Batch에서 실패한 작업을 다시 실행하는 방법을 정리합니다."
---

## 왜 정리했나요?

여기에 글을 씁니다. 문단은 빈 줄로 나눕니다.

## 코드 예시

```java
// 코드를 여기에 붙여 넣으세요.
```

## 마무리

배운 점이나 참고 링크를 적습니다.
````

### 글 머리말 항목

- `layout: post`는 글 전용 레이아웃을 사용합니다. 그대로 둡니다.
- `title`은 글 제목입니다. 콜론(`:`)이나 특수문자가 있으면 따옴표로 감쌉니다.
- `date`는 게시 날짜와 시간입니다. 한국 시간 표기인 `+0900`을 유지하고, 미래 날짜를 넣으면 게시 전까지 목록에 나타나지 않을 수 있습니다.
- `categories`는 글 분류입니다. 예: `[Spring]`, `[Java]`, `[회고]`.
- `tags`는 관련 키워드입니다. 여러 개를 쉼표로 구분합니다.
- `description`은 홈의 글 목록에 보이는 한 줄 소개입니다.

제목과 본문은 Markdown 문법을 사용합니다. `## 소제목`, `- 목록`, `[링크 이름](https://example.com)`, 코드 블록 등을 쓸 수 있습니다. 코드 블록은 세 개의 백틱 뒤에 언어 이름을 적습니다. 예: `` ```java ``. 기존 글을 고치려면 저장소에서 해당 `.md` 파일을 열고 연필 아이콘으로 편집한 뒤 커밋하면 됩니다.

## 이미지 올리고 글에 넣기

이미지는 블로그 저장소에 함께 보관합니다. 별도의 이미지 호스팅 서비스 계정이 필요 없고, 글과 이미지가 한곳에서 관리됩니다.

1. 저장소에서 `assets/images` 폴더를 엽니다.
2. **Add file → Upload files**를 눌러 이미지 파일을 끌어다 놓습니다.
3. 파일명을 `날짜-글주소-설명.webp`처럼 정하고 `main` 브랜치에 커밋합니다. 예: `2026-11-24-spring-batch-retry-flow.webp`.
4. 글 본문에서 이미지를 보여줄 위치에 아래 Markdown을 넣습니다.

```markdown
![Spring Batch 재시도 흐름도](/assets/images/2026-11-24-spring-batch-retry-flow.webp)
```

대괄호 안에는 화면을 보지 못하는 사람도 이미지 내용을 알 수 있도록 설명을 적습니다. PNG와 JPEG도 사용할 수 있지만, 사진이나 큰 이미지는 WebP로 저장하고 가로 폭을 약 1200px 안팎으로 줄이면 페이지가 더 가볍게 열립니다. 한 글의 이미지가 많아지면 파일명 앞부분의 날짜와 글 주소로 묶어 찾으면 됩니다. 글에서 사용 중인 이미지를 삭제하거나 이름을 바꾸면 링크가 깨지므로, 본문 링크도 함께 수정해 주세요.

## 배포 방식

`main` 브랜치에 커밋하면 GitHub Actions가 Jekyll로 사이트를 빌드하고 GitHub Pages에 배포합니다. [Actions 실행 내역](https://github.com/jeus1998/jeus1998.github.io/actions)에서 진행 상태를 확인할 수 있습니다.
