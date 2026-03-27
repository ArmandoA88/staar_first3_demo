const state = {
  catalog: null,
  items: [],
  filters: {
    search: "",
    teks: "",
    year: "",
    difficulty: "",
    itemType: "",
    content: "",
    reviewOnly: false,
  },
};

const elements = {
  searchInput: document.querySelector("#search-input"),
  teksFilter: document.querySelector("#teks-filter"),
  yearFilter: document.querySelector("#year-filter"),
  difficultyFilter: document.querySelector("#difficulty-filter"),
  itemTypeFilter: document.querySelector("#item-type-filter"),
  contentFilter: document.querySelector("#content-filter"),
  reviewOnly: document.querySelector("#review-only"),
  resetFilters: document.querySelector("#reset-filters"),
  resultsSummary: document.querySelector("#results-summary"),
  results: document.querySelector("#results"),
  stats: document.querySelector("#catalog-stats"),
  teksGroups: document.querySelector("#teks-groups"),
  yearGroups: document.querySelector("#year-groups"),
  difficultyGroups: document.querySelector("#difficulty-groups"),
  teksCount: document.querySelector("#teks-count"),
  yearCount: document.querySelector("#year-count"),
  difficultyCount: document.querySelector("#difficulty-count"),
  cardTemplate: document.querySelector("#item-card-template"),
};

function normalizeText(value) {
  return (value || "").toLowerCase().trim();
}

function uniqueValues(items, accessor, sorter) {
  const values = [...new Set(items.map(accessor).filter(Boolean))];
  return sorter ? values.sort(sorter) : values.sort();
}

function optionMarkup(option) {
  return option.label ? `<strong>${option.label}.</strong> ${option.text}` : option.text;
}

function difficultyClass(label) {
  return ["easy", "medium", "hard"].includes(label) ? label : "";
}

function buildCounts(items, accessor) {
  const counts = new Map();
  items.forEach((item) => {
    const key = accessor(item);
    if (!key) {
      return;
    }
    counts.set(key, (counts.get(key) || 0) + 1);
  });
  return [...counts.entries()].sort((left, right) => {
    if (right[1] !== left[1]) {
      return right[1] - left[1];
    }
    return String(left[0]).localeCompare(String(right[0]));
  });
}

function populateSelect(select, values, formatter = (value) => value) {
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = formatter(value);
    select.append(option);
  });
}

function installStaticFilters() {
  populateSelect(elements.teksFilter, uniqueValues(state.items, (item) => item.metadata.standard));
  populateSelect(
    elements.yearFilter,
    uniqueValues(state.items, (item) => String(item.metadata.year), (left, right) => Number(right) - Number(left))
  );
  populateSelect(
    elements.difficultyFilter,
    uniqueValues(state.items, (item) => item.metadata.difficulty?.label),
    (value) => value.charAt(0).toUpperCase() + value.slice(1)
  );
  populateSelect(elements.itemTypeFilter, uniqueValues(state.items, (item) => item.metadata.item_type));
  populateSelect(elements.contentFilter, uniqueValues(state.items, (item) => item.metadata.content));
}

function attachEvents() {
  elements.searchInput.addEventListener("input", (event) => {
    state.filters.search = event.target.value;
    render();
  });

  elements.teksFilter.addEventListener("change", (event) => {
    state.filters.teks = event.target.value;
    render();
  });

  elements.yearFilter.addEventListener("change", (event) => {
    state.filters.year = event.target.value;
    render();
  });

  elements.difficultyFilter.addEventListener("change", (event) => {
    state.filters.difficulty = event.target.value;
    render();
  });

  elements.itemTypeFilter.addEventListener("change", (event) => {
    state.filters.itemType = event.target.value;
    render();
  });

  elements.contentFilter.addEventListener("change", (event) => {
    state.filters.content = event.target.value;
    render();
  });

  elements.reviewOnly.addEventListener("change", (event) => {
    state.filters.reviewOnly = event.target.checked;
    render();
  });

  elements.resetFilters.addEventListener("click", () => {
    state.filters = {
      search: "",
      teks: "",
      year: "",
      difficulty: "",
      itemType: "",
      content: "",
      reviewOnly: false,
    };

    elements.searchInput.value = "";
    elements.teksFilter.value = "";
    elements.yearFilter.value = "";
    elements.difficultyFilter.value = "";
    elements.itemTypeFilter.value = "";
    elements.contentFilter.value = "";
    elements.reviewOnly.checked = false;
    render();
  });
}

function filterItems() {
  const search = normalizeText(state.filters.search);
  return state.items.filter((item) => {
    const haystack = normalizeText(
      [
        item.id,
        item.metadata.standard,
        item.metadata.standard_description,
        item.metadata.cluster,
        item.metadata.subcluster,
        item.metadata.content,
        item.question.stem,
        item.question.instruction,
        item.answer_key.correct_text,
        ...(item.answer_key.correct_texts || []),
      ]
        .filter(Boolean)
        .join(" ")
    );

    if (state.filters.teks && item.metadata.standard !== state.filters.teks) {
      return false;
    }
    if (state.filters.year && String(item.metadata.year) !== state.filters.year) {
      return false;
    }
    if (state.filters.difficulty && item.metadata.difficulty?.label !== state.filters.difficulty) {
      return false;
    }
    if (state.filters.itemType && item.metadata.item_type !== state.filters.itemType) {
      return false;
    }
    if (state.filters.content && item.metadata.content !== state.filters.content) {
      return false;
    }
    if (state.filters.reviewOnly && !item.extraction_quality.needs_review) {
      return false;
    }
    if (search && !haystack.includes(search)) {
      return false;
    }
    return true;
  });
}

function setChipGroup(container, counts, totalLabel, activeValue, onClick) {
  container.innerHTML = "";
  if (!counts.length) {
    const empty = document.createElement("span");
    empty.className = "chip-static";
    empty.textContent = "No data";
    container.append(empty);
    return;
  }

  counts.slice(0, 18).forEach(([label, count]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `chip-button${activeValue === label ? " is-active" : ""}`;
    button.textContent = `${label} (${count})`;
    button.addEventListener("click", () => onClick(label));
    container.append(button);
  });

  if (counts.length > 18) {
    const tail = document.createElement("span");
    tail.className = "chip-static";
    tail.textContent = `+${counts.length - 18} more ${totalLabel}`;
    container.append(tail);
  }
}

function renderSummary(filteredItems) {
  elements.resultsSummary.textContent = `${filteredItems.length} of ${state.items.length} problems shown`;
  elements.stats.innerHTML = `
    <strong>${state.catalog.subject || "Unknown subject"} Grade ${state.catalog.grade || "?"}</strong><br />
    ${state.catalog.item_count} extracted items<br />
    ${filteredItems.filter((item) => item.extraction_quality.needs_review).length} visible items marked for review
  `;

  const teksCounts = buildCounts(filteredItems, (item) => item.metadata.standard);
  const yearCounts = buildCounts(filteredItems, (item) => String(item.metadata.year));
  const difficultyCounts = buildCounts(filteredItems, (item) => item.metadata.difficulty?.label);

  elements.teksCount.textContent = `${teksCounts.length} groups`;
  elements.yearCount.textContent = `${yearCounts.length} years`;
  elements.difficultyCount.textContent = `${difficultyCounts.length} levels`;

  setChipGroup(elements.teksGroups, teksCounts, "TEKS groups", state.filters.teks, (label) => {
    state.filters.teks = state.filters.teks === label ? "" : label;
    elements.teksFilter.value = state.filters.teks;
    render();
  });
  setChipGroup(elements.yearGroups, yearCounts, "years", state.filters.year, (label) => {
    state.filters.year = state.filters.year === label ? "" : label;
    elements.yearFilter.value = state.filters.year;
    render();
  });
  setChipGroup(elements.difficultyGroups, difficultyCounts, "difficulty groups", state.filters.difficulty, (label) => {
    state.filters.difficulty = state.filters.difficulty === label ? "" : label;
    elements.difficultyFilter.value = state.filters.difficulty;
    render();
  });
}

function renderAnswer(item) {
  const answer = item.answer_key;
  if (answer.answer_format === "single_choice_label") {
    return `<strong>Answer:</strong> ${answer.correct_label}${answer.correct_text ? ` - ${answer.correct_text}` : ""}`;
  }
  if (answer.answer_format === "multi_select_positions") {
    const joined = (answer.correct_texts || []).join("; ");
    return `<strong>Answer:</strong> positions ${(answer.correct_positions || []).join(", ")}${joined ? ` - ${joined}` : ""}`;
  }
  if (answer.answer_format === "ordered_blanks") {
    return `<strong>Answer:</strong> ${(answer.blank_values || []).join("; ")}`;
  }
  if (answer.correct_text) {
    return `<strong>Answer:</strong> ${answer.correct_text}`;
  }
  return `<strong>Answer:</strong> ${answer.raw_pdf_answer_text || "Unavailable"}`;
}

function renderCard(item) {
  const fragment = elements.cardTemplate.content.cloneNode(true);
  const card = fragment.querySelector(".item-card");
  const meta = fragment.querySelector(".item-meta");
  const title = fragment.querySelector(".item-title");
  const instruction = fragment.querySelector(".item-instruction");
  const optionList = fragment.querySelector(".option-list");
  const responseTemplate = fragment.querySelector(".response-template");
  const visualList = fragment.querySelector(".visual-list");
  const image = fragment.querySelector(".item-image");
  const answerBlock = fragment.querySelector(".answer-block");
  const difficultyBlock = fragment.querySelector(".difficulty-block");

  const pills = [
    item.metadata.standard,
    String(item.metadata.year),
    item.metadata.item_type,
    item.metadata.content,
  ].filter(Boolean);

  pills.forEach((value) => {
    const pill = document.createElement("span");
    pill.className = "meta-pill";
    pill.textContent = value;
    meta.append(pill);
  });

  const difficultyLabel = item.metadata.difficulty?.label || "unknown";
  const difficultyPill = document.createElement("span");
  difficultyPill.className = `meta-pill ${difficultyClass(difficultyLabel)}`;
  difficultyPill.textContent = `${difficultyLabel} difficulty`;
  meta.append(difficultyPill);

  if (item.extraction_quality.needs_review) {
    const reviewPill = document.createElement("span");
    reviewPill.className = "meta-pill review";
    reviewPill.textContent = "needs review";
    meta.append(reviewPill);
  }

  title.textContent = item.question.stem || item.id;
  instruction.textContent = item.question.instruction || "";
  instruction.hidden = !item.question.instruction;

  if (item.question.options?.length) {
    optionList.innerHTML = item.question.options
      .map((option) => `<li>${optionMarkup(option)}</li>`)
      .join("");
  } else {
    optionList.remove();
  }

  if (item.question.response_template) {
    responseTemplate.innerHTML = `<strong>Response template:</strong> ${item.question.response_template}`;
    if (item.question.choice_pool?.length) {
      responseTemplate.innerHTML += `<br /><strong>Choice pool:</strong> ${item.question.choice_pool.join(", ")}`;
    }
  } else {
    responseTemplate.remove();
  }

  if (item.question.visual_elements?.length) {
    visualList.innerHTML = `<strong>Visual elements:</strong> ${item.question.visual_elements.join(", ")}`;
  } else {
    visualList.remove();
  }

  image.src = item.source.question_image;
  image.alt = `${item.metadata.standard} ${item.metadata.year} question ${item.metadata.question_number}`;

  answerBlock.innerHTML = `
    ${renderAnswer(item)}<br />
    <strong>Cluster:</strong> ${item.metadata.cluster || "Unknown"}<br />
    <strong>Subcluster:</strong> ${item.metadata.subcluster || "Unknown"}
  `;

  difficultyBlock.innerHTML = `
    <strong>State % correct:</strong> ${item.metadata.difficulty?.percent_correct ?? "n/a"}<br />
    <strong>Difficulty score:</strong> ${item.metadata.difficulty?.score ?? "n/a"}${item.metadata.difficulty?.score ? "/5" : ""}<br />
    <strong>Why:</strong> ${item.metadata.difficulty?.rationale || "No rationale"}<br />
    <strong>Vision confidence:</strong> ${item.extraction_quality.vision_confidence ?? "n/a"}
  `;

  card.dataset.id = item.id;
  return fragment;
}

function renderResults(filteredItems) {
  elements.results.innerHTML = "";
  if (!filteredItems.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "No problems match the current filters.";
    elements.results.append(empty);
    return;
  }

  filteredItems.forEach((item) => {
    elements.results.append(renderCard(item));
  });
}

function render() {
  const filteredItems = filterItems().sort((left, right) => {
    if (right.metadata.year !== left.metadata.year) {
      return right.metadata.year - left.metadata.year;
    }
    if (left.metadata.standard !== right.metadata.standard) {
      return left.metadata.standard.localeCompare(right.metadata.standard);
    }
    return left.metadata.question_number - right.metadata.question_number;
  });

  renderSummary(filteredItems);
  renderResults(filteredItems);
}

async function init() {
  try {
    const response = await fetch("./data/staar_catalog.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    state.catalog = await response.json();
    state.items = state.catalog.items || [];
    installStaticFilters();
    attachEvents();
    render();
  } catch (error) {
    elements.resultsSummary.textContent = "Catalog failed to load.";
    elements.results.innerHTML = `<div class="empty-state">Unable to load ./data/staar_catalog.json. ${error.message}</div>`;
  }
}

init();
