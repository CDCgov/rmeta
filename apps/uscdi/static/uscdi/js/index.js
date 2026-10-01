(() => {
  const table = document.querySelector("#data-elements-table");
  if (!table) return;

  const rows = Array.from(table.querySelectorAll("tbody tr[data-mapped]"));
  const search = document.querySelector("#element-search");
  const mappingFilter = document.querySelector("#mapping-filter");
  const classFilter = document.querySelector("#class-filter");
  const clearButton = document.querySelector("#clear-filters");
  const visibleCount = document.querySelector("#visible-count");
  const noResults = document.querySelector("#no-filter-results");

  const normalize = (value) => value.toLocaleLowerCase().replace(/\s+/g, " ").trim();

  const applyFilters = () => {
    const query = normalize(search.value);
    const mapping = mappingFilter.value;
    const dataClass = classFilter.value;
    let shown = 0;

    rows.forEach((row) => {
      const matchesSearch = !query || normalize(row.textContent).includes(query);
      const matchesMapping = mapping === "all" || row.dataset.mapped === mapping;
      const matchesClass = dataClass === "all" || row.dataset.class === dataClass;
      const isVisible = matchesSearch && matchesMapping && matchesClass;
      row.hidden = !isVisible;
      if (isVisible) shown += 1;
    });

    visibleCount.textContent = shown;
    noResults.hidden = shown !== 0 || rows.length === 0;
  };

  search.addEventListener("input", applyFilters);
  mappingFilter.addEventListener("change", applyFilters);
  classFilter.addEventListener("change", applyFilters);
  clearButton.addEventListener("click", () => {
    search.value = "";
    mappingFilter.value = "all";
    classFilter.value = "all";
    applyFilters();
    search.focus();
  });
})();
