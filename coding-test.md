---
layout: default
title: 코딩 테스트 풀이
permalink: /coding-test/
---
<section class="coding-page">
  <header class="coding-intro">
    <p class="eyebrow">CODING TEST ARCHIVE</p>
    <h1>코딩 테스트 풀이</h1>
    <p>저장소의 문제 목록과 README, Java 코드를 블로그에서 바로 찾아볼 수 있습니다. 새 풀이를 푸시하면 자동으로 갱신됩니다.</p>
    <a class="text-link" href="https://github.com/jeus1998/coding-test" target="_blank" rel="noreferrer">GitHub 저장소 열기 ↗</a>
  </header>
  <div class="coding-browser" data-coding-browser data-source="{{ '/assets/data/coding-test-files.json' | relative_url }}">
    <aside class="coding-sidebar">
      <label class="visually-hidden" for="coding-search">문제 검색</label>
      <input id="coding-search" type="search" placeholder="문제명, 번호 검색" data-coding-search>
      <div class="coding-filters" data-coding-filters></div>
      <div class="coding-list" data-coding-list aria-live="polite"></div>
    </aside>
    <section class="coding-detail" data-coding-detail aria-live="polite"><p class="coding-placeholder">왼쪽에서 문제를 선택하세요.</p></section>
  </div>
</section>
<script defer src="{{ '/assets/js/coding-test-browser.js' | relative_url }}"></script>
