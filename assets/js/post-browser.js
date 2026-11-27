(() => {
  const form = document.querySelector("[data-post-search]");
  if (!form) return;

  const input = form.querySelector('input[type="search"]');
  const rows = Array.from(document.querySelectorAll("[data-post-row]"));
  const count = document.querySelector("[data-post-count]");
  const empty = document.querySelector("[data-no-results]");
  const paginationList = document.querySelector("[data-post-pagination]");
  const pagination = document.querySelector("[data-pagination]");
  const normalize = (value) => value.toLocaleLowerCase().normalize("NFKC").trim();

  form.addEventListener("submit", (event) => event.preventDefault());

  // The home page paginates its full list and its filtered search results.
  // Category pages intentionally keep their complete Notion-ordered list.
  if (paginationList && pagination) {
    const pageSize = Math.max(1, Number(paginationList.dataset.pageSize) || 10);
    let currentPage = 1;

    function renderPagination(pageCount) {
      pagination.replaceChildren();
      pagination.hidden = pageCount < 2;
      if (pageCount < 2) return;

      const addButton = (label, page, { disabled = false, current = false } = {}) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = current ? "page-button is-current" : "page-button";
        button.textContent = label;
        button.disabled = disabled;
        if (current) button.setAttribute("aria-current", "page");
        button.addEventListener("click", () => {
          currentPage = page;
          render();
          paginationList.scrollIntoView({ behavior: "smooth", block: "start" });
        });
        pagination.append(button);
      };

      addButton("이전", currentPage - 1, { disabled: currentPage === 1 });

      const firstPage = Math.max(1, Math.min(currentPage - 2, pageCount - 4));
      const lastPage = Math.min(pageCount, firstPage + 4);
      if (firstPage > 1) {
        addButton("1", 1, { current: currentPage === 1 });
        if (firstPage > 2) {
          const gap = document.createElement("span");
          gap.className = "page-gap";
          gap.setAttribute("aria-hidden", "true");
          gap.textContent = "…";
          pagination.append(gap);
        }
      }
      for (let page = firstPage; page <= lastPage; page += 1) {
        addButton(String(page), page, { current: currentPage === page });
      }
      if (lastPage < pageCount) {
        if (lastPage < pageCount - 1) {
          const gap = document.createElement("span");
          gap.className = "page-gap";
          gap.setAttribute("aria-hidden", "true");
          gap.textContent = "…";
          pagination.append(gap);
        }
        addButton(String(pageCount), pageCount, { current: currentPage === pageCount });
      }

      addButton("다음", currentPage + 1, { disabled: currentPage === pageCount });
    }

    function render() {
      const terms = normalize(input.value).split(/\s+/).filter(Boolean);
      const matchingRows = rows.filter((row) => {
        const searchableText = normalize(row.dataset.search || "");
        return terms.every((term) => searchableText.includes(term));
      });
      const pageCount = Math.ceil(matchingRows.length / pageSize);
      currentPage = Math.min(currentPage, Math.max(pageCount, 1));
      const start = (currentPage - 1) * pageSize;
      const visibleRows = new Set(matchingRows.slice(start, start + pageSize));

      rows.forEach((row) => {
        row.hidden = !visibleRows.has(row);
      });
      if (count) {
        count.textContent = terms.length
          ? `${matchingRows.length}개의 검색 결과`
          : `${rows.length}개의 글`;
      }
      if (empty) empty.hidden = matchingRows.length !== 0;
      renderPagination(pageCount);
    }

    input.addEventListener("input", () => {
      currentPage = 1;
      render();
    });
    render();
    return;
  }

  // Category archives retain the existing all-results search behavior.
  const initialCount = rows.length;
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
