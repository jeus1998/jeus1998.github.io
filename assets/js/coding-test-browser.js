(() => {
 const root=document.querySelector("[data-coding-browser]"); if(!root)return;
 const list=root.querySelector("[data-coding-list]"),detail=root.querySelector("[data-coding-detail]"),search=root.querySelector("[data-coding-search]"),filters=root.querySelector("[data-coding-filters]");
 let problems=[],platform="전체",selected=null;
 const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text)n.textContent=text;return n;};
 const external=(label,url)=>{const a=el("a","",label);a.href=url;a.target="_blank";a.rel="noreferrer";return a;};
 function drawList(){const q=search.value.trim().toLocaleLowerCase(),shown=problems.filter(p=>(platform==="전체"||p.platform===platform)&&(p.title+" "+p.number+" "+p.level).toLocaleLowerCase().includes(q));list.replaceChildren();
  if(!shown.length){list.append(el("p","coding-empty","검색 결과가 없습니다."));return;}
  shown.forEach(p=>{const b=el("button","coding-item"+(selected?.id===p.id?" is-active":""));b.type="button";b.append(el("span","coding-item-platform",p.platform+" · "+p.level),el("strong","",p.title),el("span","coding-item-number","#"+p.number));b.onclick=()=>{selected=p;drawList();drawDetail(p);};list.append(b);});
 }
 function drawDetail(p){detail.replaceChildren();const head=el("div","coding-detail-heading"),copy=el("div");copy.append(el("p","eyebrow",p.platform+" · "+p.level),el("h2","",p.title),el("span","coding-date","문제 번호 "+p.number+" · "+p.date));head.append(copy);
  const actions=el("div","coding-actions");if(p.problem_url)actions.append(external("문제 ↗",p.problem_url));actions.append(external("GitHub ↗",p.github_url));if(p.post_url)actions.append(external("블로그 글 ↗",p.post_url));head.append(actions);detail.append(head);
  const tabs=el("div","coding-tabs"),pane=el("div","coding-content");
  const show=tab=>{tabs.querySelectorAll("button").forEach(b=>b.classList.toggle("is-active",b.dataset.tab===tab));pane.replaceChildren();if(tab==="readme"){const readme=el("div","coding-readme");
   if(window.marked&&window.DOMPurify){readme.innerHTML=window.DOMPurify.sanitize(window.marked.parse(p.readme));}
   else{readme.textContent=p.readme;}
   pane.append(readme);
  }else{const pre=el("pre","coding-code"),code=el("code");code.textContent=p.source;pre.append(code);pane.append(pre);}};
  [["readme","README"],["code","Java 코드"]].forEach(([key,label])=>{const b=el("button","",label);b.type="button";b.dataset.tab=key;b.onclick=()=>show(key);tabs.append(b);});
  detail.append(tabs,pane);show("readme");
 }
 fetch(root.dataset.source).then(r=>{if(!r.ok)throw Error("data");return r.json();}).then(d=>{problems=d.problems||[];
  ["전체",...new Set(problems.map(p=>p.platform))].forEach(name=>{const b=el("button","coding-filter"+(name===platform?" is-active":""),name);b.type="button";b.onclick=()=>{platform=name;filters.querySelectorAll("button").forEach(x=>x.classList.toggle("is-active",x.textContent===name));drawList();};filters.append(b);});
  drawList();if(problems[0]){selected=problems[0];drawList();drawDetail(selected);}
 }).catch(()=>detail.replaceChildren(el("p","coding-placeholder","문제 목록을 불러오지 못했습니다. 잠시 후 다시 확인해 주세요.")));
 search.addEventListener("input",drawList);
})();
