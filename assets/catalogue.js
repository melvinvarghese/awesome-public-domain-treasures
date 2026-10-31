(function (root) {
  "use strict";

  const SEARCH_FIELDS = [
    "title", "creator", "year", "description", "institution", "region",
    "formats", "tags", "category", "rights_status", "rights_evidence"
  ];

  function textValue(value) {
    if (value == null) return "";
    if (Array.isArray(value)) return value.map(textValue).filter(Boolean).join(" ");
    return String(value);
  }

  function getSearchableText(record) {
    return SEARCH_FIELDS.map(function (field) {
      return textValue(record[field]);
    }).filter(Boolean).join(" ");
  }

  function getFilterValues(entries, field) {
    return Array.from(new Set(entries.map(function (record) {
      return record[field];
    }).filter(function (value) {
      return typeof value === "string" && value.length > 0;
    })));
  }

  function populateFilter(select, entries, field) {
    const label = field === "category" ? "categories" : "rights statuses";
    select.replaceChildren();
    const allOption = document.createElement("option");
    allOption.value = "";
    allOption.textContent = "All " + label;
    select.append(allOption);
    getFilterValues(entries, field).forEach(function (value) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      select.append(option);
    });
  }

  function matchesRecord(record, query, category, rightsStatus) {
    const normalizedQuery = query.trim().toLocaleLowerCase();
    if (normalizedQuery && !getSearchableText(record).toLocaleLowerCase().includes(normalizedQuery)) {
      return false;
    }
    if (category && record.category !== category) return false;
    if (rightsStatus && record.rights_status !== rightsStatus) return false;
    return true;
  }

  function filterRecords(entries, query, category, rightsStatus) {
    return entries.filter(function (record) {
      return matchesRecord(record, query, category, rightsStatus);
    });
  }

  function makeElement(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text != null) element.textContent = text;
    return element;
  }

  function makeExternalLink(label, href, title) {
    const link = makeElement("a", "", label);
    link.href = href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", label + ": " + title);
    return link;
  }

  function addMetadata(container, label, value) {
    if (!value) return;
    const entry = makeElement("p");
    const name = makeElement("strong", "", label + ": ");
    const content = makeElement("span", "", value);
    entry.append(name, content);
    container.append(entry);
  }

  function renderRecord(record) {
    const article = makeElement("article", "treasure-card");
    const category = makeElement("p", "card-category", record.category);
    const title = makeElement("h2", "card-title", record.title);
    const description = makeElement("p", "card-description", record.description);
    article.append(category, title, description);

    const metadata = makeElement("div", "card-metadata");
    addMetadata(metadata, "Creator", record.creator);
    addMetadata(metadata, "Year", record.year);
    addMetadata(metadata, "Institution", record.institution);
    addMetadata(metadata, "Region", record.region);
    article.append(metadata);

    article.append(makeElement("p", "rights-status", record.rights_status));

    if (record.rights_evidence) {
      const evidence = makeElement("details", "evidence-note");
      evidence.append(makeElement("summary", "", "What the rights record says"));
      evidence.append(makeElement("p", "", record.rights_evidence));
      article.append(evidence);
    }

    const links = makeElement("div", "card-links");
    links.append(
      makeExternalLink("Item record", record.item_url, record.title),
      makeExternalLink("Rights evidence", record.rights_url, record.title)
    );
    article.append(links);
    return article;
  }

  function renderResults(entries, query, category, rightsStatus) {
    const results = filterRecords(entries, query, category, rightsStatus);
    const list = document.getElementById("results-list");
    const count = document.getElementById("results-count");
    const empty = document.getElementById("empty-state");
    list.replaceChildren.apply(list, results.map(renderRecord));
    count.textContent = results.length + (results.length === 1 ? " treasure found" : " treasures found");
    empty.hidden = results.length !== 0;
    return results.length;
  }

  async function loadCatalogue() {
    const count = document.getElementById("results-count");
    const error = document.getElementById("catalogue-error");
    const search = document.getElementById("search-input");
    const category = document.getElementById("category-filter");
    const rights = document.getElementById("rights-filter");
    const clear = document.getElementById("clear-filters");

    try {
      const response = await fetch("./data/treasures.json");
      if (!response.ok) throw new Error("Catalogue request failed: " + response.status);
      const entries = await response.json();
      if (!Array.isArray(entries)) throw new Error("Catalogue data is not a list.");

      populateFilter(category, entries, "category");
      populateFilter(rights, entries, "rights_status");

      function updateResults() {
        renderResults(entries, search.value, category.value, rights.value);
      }

      search.addEventListener("input", updateResults);
      category.addEventListener("change", updateResults);
      rights.addEventListener("change", updateResults);
      clear.addEventListener("click", function () {
        search.value = "";
        category.value = "";
        rights.value = "";
        updateResults();
        search.focus();
      });
      updateResults();
    } catch (cause) {
      count.textContent = "The catalogue could not be loaded.";
      error.hidden = false;
    }
  }

  const api = {
    SEARCH_FIELDS: SEARCH_FIELDS,
    getSearchableText: getSearchableText,
    getFilterValues: getFilterValues,
    populateFilter: populateFilter,
    matchesRecord: matchesRecord,
    filterRecords: filterRecords,
    renderRecord: renderRecord,
    renderResults: renderResults,
    loadCatalogue: loadCatalogue
  };

  root.CatalogueBrowser = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", loadCatalogue, { once: true });
    } else {
      loadCatalogue();
    }
  }
})(typeof globalThis !== "undefined" ? globalThis : window);
