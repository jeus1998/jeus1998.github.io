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
  <div class="section-heading"><div><p class="eyebrow">THE JOURNAL</p><h2 id="posts-heading">최근 기록</h2></div><span class="post-count">{{ site.posts.size }}개의 글</span></div>
  <div class="post-list">
    {% for post in site.posts %}
    <article class="post-row">
      <time datetime="{{ post.date | date_to_xmlschema }}">{{ post.date | date: '%Y.%m.%d' }}</time>
      <div class="post-summary">
        <div class="eyebrow">{% for category in post.categories %}<span>{{ category }}</span>{% endfor %}</div>
        <h3><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
        <p>{{ post.description | default: post.excerpt | strip_html | truncate: 110 }}</p>
        {% if post.tags.size > 0 %}<div class="tag-list">{% for tag in post.tags %}<span>#{{ tag }}</span>{% endfor %}</div>{% endif %}
      </div>
      <a class="row-arrow" href="{{ post.url | relative_url }}" aria-label="{{ post.title }} 읽기">↗</a>
    </article>
    {% endfor %}
  </div>
</section>
<section class="note-card"><span class="note-icon" aria-hidden="true">✳</span><div><p class="eyebrow">A SMALL REMINDER</p><p>완벽한 글보다, 계속 쓰는 기록.</p></div><span class="note-spark" aria-hidden="true">✦</span></section>
