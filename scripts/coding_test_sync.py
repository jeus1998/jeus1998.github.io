#!/usr/bin/env python3
"""Import BaekjoonHub README/Java pairs as Jekyll posts and browser data."""
from __future__ import annotations
import json, re, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path
OWNER, REPO, BRANCH = "jeus1998", "coding-test", "main"
ROOT = Path(__file__).resolve().parents[1]
POSTS, CATEGORIES, DATA = ROOT / "_posts", ROOT / "_blog_categories", ROOT / "assets/data/coding-test-files.json"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"

def get_json(url):
    req = urllib.request.Request(url, headers={"Accept":"application/vnd.github+json","User-Agent":"JeusLogSync"})
    with urllib.request.urlopen(req, timeout=45) as response: return json.load(response)

def get_text(path):
    url = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/" + urllib.parse.quote(path, safe="/")
    req = urllib.request.Request(url, headers={"User-Agent":"JeusLogSync"})
    with urllib.request.urlopen(req, timeout=45) as response: return response.read().decode("utf-8")

def redact(text):
    text = re.sub(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", "[REDACTED PRIVATE KEY]", text, flags=re.S)
    text = re.sub(r"\b(?:AKIA|ASIA|AIDA|AROA|ANPA|ANVA|AGPA)[A-Z0-9]{16}\b", "[REDACTED AWS ACCESS KEY]", text)
    text = re.sub(r"""(?im)(aws[_ -]?secret[_ -]?access[_ -]?key|secret[_ -]?access[_ -]?key|client[_ -]?secret|access[_ -]?token|api[_ -]?key|password|passwd|token)(\s*[:=]\s*)(?:"[^"]*"|'[^']*'|[^\s,;]+)""", r"\1\2[REDACTED]", text)
    return re.sub(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b", "[REDACTED GITHUB TOKEN]", text)

def info(readme, folder):
    m = re.search(r"^#\s+\[([^]]+)\]\s+(.+?)\s+-\s+(\d+)\s*$", readme, re.M)
    level,title,number=(m.group(1).strip(),m.group(2).strip(),m.group(3)) if m else ("풀이",Path(folder).name,re.search(r"(\d+)",folder).group(1))
    d = re.search(r"### 제출 일자\s*\n\s*(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", readme)
    day=f"{d.group(1)}-{int(d.group(2)):02d}-{int(d.group(3)):02d}" if d else datetime.utcnow().strftime("%Y-%m-%d")
    platform="프로그래머스" if folder.startswith("프로그래머스/") else "백준"
    u=re.search(r"\[문제 링크\]\(([^)]+)\)",readme)
    return title,number,level,day,platform,u.group(1) if u else ""

def main():
    POSTS.mkdir(exist_ok=True); CATEGORIES.mkdir(exist_ok=True); DATA.parent.mkdir(parents=True,exist_ok=True)
    tree=get_json(f"{API}/git/trees/{BRANCH}?recursive=1")
    if tree.get("truncated"): raise RuntimeError("coding-test tree was truncated; refusing to delete generated posts")
    files={x["path"] for x in tree.get("tree",[]) if x.get("type")=="blob"}
    folders=sorted({p.rsplit("/",1)[0] for p in files if p.endswith("/README.md")})
    problems,written=[],set()
    for folder in folders:
        rp=folder+"/README.md"
        java=sorted(p for p in files if p.startswith(folder+"/") and p.endswith(".java"))
        if not java: continue
        sp=java[0]; readme,source=redact(get_text(rp)),redact(get_text(sp))
        title,number,level,day,platform,problem_url=info(readme,folder)
        pid=f"{'programmers' if platform=='프로그래머스' else 'boj'}-{number}"
        cat="프로그래머스" if platform=="프로그래머스" else "백준"
        post=POSTS/f"{day}-coding-test-{pid}.md"
        folder_url="https://github.com/jeus1998/coding-test/tree/main/"+urllib.parse.quote(folder,safe="/")
        source_url="https://github.com/jeus1998/coding-test/blob/main/"+urllib.parse.quote(sp,safe="/")
        summary=re.sub(r"(?s)^#.*?\n\s*### 성능 요약.*?(?=### 문제 설명|### 입력 형식|### 입력\b)","",readme).strip()
        fence=chr(96)*3
        body=(f"이 글은 [jeus1998/coding-test]({folder_url}) 저장소의 풀이를 자동으로 가져온 기록입니다. "
              f"원본은 [Java 파일]({source_url})에서 확인할 수 있습니다.\n\n"
              f"## 문제\n\n{summary}\n\n## 풀이 코드\n\n{fence}java\n{source.rstrip()}\n{fence}\n")
        front=["---","layout: post",f"title: {json.dumps(title+' - '+number,ensure_ascii=False)}",
               f"date: {day} 12:00:00 +0900", f"permalink: /coding-test/posts/{pid}/",
               f"categories: [{json.dumps('코딩 테스트',ensure_ascii=False)}, {json.dumps(cat,ensure_ascii=False)}]",
               f"tags: [{json.dumps(platform,ensure_ascii=False)}, {json.dumps(level,ensure_ascii=False)}]",
               f"description: {json.dumps(platform+' '+number+'번 문제 풀이 ('+level+')',ensure_ascii=False)}",
               f"coding_test_id: {json.dumps(pid)}","---",""]
        post.write_text("\n".join(front)+body,encoding="utf-8"); written.add(post)
        slug=cat.replace(" ","-")
        post_url=f"/coding-test/posts/{pid}/"
        problems.append({"id":pid,"title":title,"number":number,"platform":platform,"level":level,"date":day,
          "path":folder,"readme_path":rp,"source_path":sp,"source":source,"readme":readme,
          "problem_url":problem_url,"github_url":folder_url,"source_url":source_url,"post_url":post_url})
    if not problems: raise RuntimeError("No README/Java problem pairs found; refusing to delete generated posts")
    for p in POSTS.glob("*-coding-test-*.md"):
        if p not in written: p.unlink()
    DATA.write_text(json.dumps({"repository":f"{OWNER}/{REPO}","updated_at":get_json(API).get("pushed_at",""),
      "problems":sorted(problems,key=lambda p:(p["date"],p["platform"],p["number"]),reverse=True)},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for title,slug in (("코딩 테스트","coding-test"),("백준","boj"),("프로그래머스","programmers")):
        (CATEGORIES/f"{slug}.md").write_text("---\nlayout: category\n"+f"title: {json.dumps(title,ensure_ascii=False)}\nslug: {slug}\n"+
          f"description: {json.dumps('coding-test 저장소에서 자동으로 동기화한 문제 풀이입니다.',ensure_ascii=False)}\n---\n",encoding="utf-8")
    print(f"Synced {len(problems)} coding-test problems.")

if __name__=="__main__": main()
