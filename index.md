---
layout: default
title: 홈
---
<section class="hero">
  <div class="hero-copy">
    <p class="eyebrow"><span class="status-dot"></span> DEVELOPER · NOTES</p>
    <h1>배우고 만들며<br><em>기록합니다.</em></h1>
    <p class="hero-intro">개발하면서 만난 문제와 배운 내용을 정리합니다.<br>작은 기록이 다음 걸음을 더 쉽게 만들어주니까요.</p>
    <a class="text-link" href="{{ '/about/' | relative_url }}">블로그 소개 <span aria-hidden="true">→</span></a>
  </div>
  <div class="hero-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="orbit orbit-three"></div><span class="hero-symbol">{<br><b>;</b><br>}</span><span class="hero-caption">LEARN / BUILD / SHARE</span></div>
</section>
<section class="posts-section" aria-labelledby="posts-heading">
  <div class="section-heading"><div><p class="eyebrow">THE JOURNAL</p><h2 id="posts-heading">최근 기록</h2></div></div>
  <form class="post-search" role="search" data-post-search>
    <label class="visually-hidden" for="post-search-input">글 검색</label>
    <input id="post-search-input" type="search" placeholder="제목, 내용, 카테고리로 검색" autocomplete="off">
    <span class="search-icon" aria-hidden="true">⌕</span>
  </form>
  <nav class="category-nav" aria-label="카테고리별 글">
    <span class="category-nav-label">카테고리</span>
    {% assign categories = site.blog_categories | sort: "title" %}
    {% for category in categories %}
      {% assign category_posts = site.posts | where_exp: "post", "post.categories contains category.title" %}
      <a href="{{ category.url | relative_url }}">{{ category.title }} <span>{{ category_posts.size }}</span></a>
    {% endfor %}
    <a class="category-all-link" href="{{ '/categories/' | relative_url }}">모두 보기 →</a>
  </nav>
  <div class="section-heading post-results-heading"><h2>모든 글</h2><span class="post-count" data-post-count>{{ site.posts.size }}개의 글</span></div>
  <div class="post-list" data-post-list>
    {% for post in site.posts %}
      {% include post-row.html post=post %}
    {% endfor %}
  </div>
  <p class="empty-state" data-no-results hidden>검색 결과가 없습니다. 다른 검색어를 입력해 보세요.</p>
</section>
<section class="note-card"><span class="note-icon" aria-hidden="true">✳</span><div><p class="eyebrow">A SMALL REMINDER</p><p>완벽한 글보다, 계속 쓰는 기록.</p></div><span class="note-spark" aria-hidden="true">✦</span></section>
