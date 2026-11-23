# Jeus Log

한국어 개발 기록을 위한 Jekyll 기반 GitHub Pages 블로그입니다.

## 글 쓰기

`_posts` 폴더에 `YYYY-MM-DD-영문-주소.md` 형식의 Markdown 파일을 추가합니다.

```yaml
---
layout: post
title: 글 제목
date: 2026-11-23 12:00:00 +0900
categories: [Spring]
tags: [Java, 공부]
description: 목록에 표시될 한 줄 소개
---

여기에 글을 씁니다.
```

`main` 브랜치에 push하면 GitHub Actions가 사이트를 빌드하고 배포합니다. 저장소의 **Settings → Pages**에서 배포 소스가 **GitHub Actions**인지 확인해 주세요.
