(() => {
  const form = document.querySelector("[data-post-search]");
  if (!form) return;

  const input = form.querySelector('input[type="search"]');
  const rows = Array.from(document.querySelectorAll("[data-post-row]"));
  const count = document.querySelector("[data-post-count]");
  const empty = document.querySelector("[data-no-results]");
  const initialCount = rows.length;
  const normalize = (value) => value.toLocaleLowerCase().normalize("NFKC").trim();

  form.addEventListener("submit", (event) => event.preventDefault());
  input.addEventListener("input", () => {
    const terms = normalize(input.value).split(/\s+/).filter(Boolean);
    let visibleCount = 0;

    rows.forEach((row) => {
      const searchableText = normalize(row.dataset.search || "");
      const matches = terms.every((term) => searchableText.includes(term));
      row.hidden = !matches;
      if (matches) visibleCount += 1;
    });

    if (count) {
      count.textContent = terms.length
        ? `${visibleCount}개의 검색 결과`
        : `${initialCount}개의 글`;
    }
    if (empty) empty.hidden = visibleCount !== 0;
  });
})();
