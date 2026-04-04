const STORAGE_KEY = "staar-teacher-builder-v1";
const PRESET_TITLES = {
  hardest_test: "Hardest Test",
  easier_test: "Easier Test",
  easy_only: "Easy Questions Only",
  hard_only: "Harder Questions Only",
  latest_only: "Latest Questions Only",
  spiral_review: "Spiral Review",
  single_teks_mastery: "Single-TEKS Mastery",
  intervention_set: "Intervention Set",
  reteach_set: "Reteach Set",
  challenge_set: "Challenge Set",
  mixed_difficulty_checkpoint: "Mixed Difficulty Checkpoint",
  exit_ticket: "Exit Ticket",
  warm_up: "Warm-Up",
  benchmark_lite: "Benchmark Lite",
  latest_released_mix: "Latest Released Mix",
  multi_select_only: "Multi-Select Only",
  constructed_response_only: "Constructed Response Only",
  passage_set: "Passage Set",
  one_passage_per_test: "One Passage Per Test",
  genre_mix: "Genre Mix",
  readiness_only: "Readiness Only",
  supporting_only: "Supporting Only",
  low_review_risk: "Low Review Risk",
  needs_review_audit: "Needs Review Audit",
  year_over_year: "Year-over-Year",
  newest_per_teks: "Newest Per TEKS",
  one_per_teks: "One Per TEKS",
  mini_quiz: "Mini Quiz",
  unit_test: "Unit Test",
};
const ELAR_ONLY_PRESETS = new Set(["passage_set", "one_passage_per_test", "genre_mix"]);
const CONSTRUCTED_RESPONSE_TYPES = new Set([
  "constructed_response",
  "short_constructed_response",
  "short_constructed_response_(2)",
  "extended_constructed_response",
  "extended_constructed_response_(composition)",
  "numeric_response",
  "text_entry",
  "equation_editor",
  "graphing",
  "number_line",
]);
const DEFAULT_THEME = {
  bgStart: "#f8f2e8",
  bgEnd: "#eef3f5",
  burstA: "#d6e2e9",
  burstB: "#efdcc2",
  panelStrong: "#fffaf0",
  accent: "#0f6c7d",
  ink: "#163042",
  muted: "#576977",
};
const SUBJECT_THEME_DEFAULTS = {
  Math: {
    bgStart: "#f5f1dc",
    bgEnd: "#e5f1f6",
    burstA: "#b8dbe6",
    burstB: "#f0d4a7",
    panelStrong: "#fffbf1",
    accent: "#11758b",
    ink: "#153241",
    muted: "#566e7b",
  },
  ELAR: {
    bgStart: "#f7eee5",
    bgEnd: "#ece2d7",
    burstA: "#dcc4b0",
    burstB: "#ead6c0",
    panelStrong: "#fff8f1",
    accent: "#985731",
    ink: "#382c29",
    muted: "#685954",
  },
  Science: {
    bgStart: "#eef4e0",
    bgEnd: "#e0efe6",
    burstA: "#bfdab4",
    burstB: "#d9e8c1",
    panelStrong: "#f9fdf4",
    accent: "#3a7d4b",
    ink: "#1f3728",
    muted: "#597060",
  },
  "Social Studies": {
    bgStart: "#f4eadb",
    bgEnd: "#e6e2d6",
    burstA: "#d9c2a4",
    burstB: "#d5d4ba",
    panelStrong: "#fff9f3",
    accent: "#8b5d33",
    ink: "#3a3027",
    muted: "#6d6155",
  },
};
const COLLECTION_THEME_PRESETS = {
  "Math-3": {
    bgStart: "#f8f1dd",
    bgEnd: "#e7f3f6",
    burstA: "#bbdbe8",
    burstB: "#f2d2a0",
    panelStrong: "#fffbf1",
    accent: "#0f6c7d",
    ink: "#163042",
    muted: "#576977",
  },
  "Math-4": {
    bgStart: "#edf5df",
    bgEnd: "#e1edf8",
    burstA: "#b5d7e7",
    burstB: "#cfe2b0",
    panelStrong: "#f8fcf4",
    accent: "#1d6f99",
    ink: "#17354a",
    muted: "#58707f",
  },
  "Math-5": {
    bgStart: "#eef1de",
    bgEnd: "#e5ebf8",
    burstA: "#c3d7f0",
    burstB: "#d8e2b1",
    panelStrong: "#fbfcf4",
    accent: "#355fa8",
    ink: "#1f3556",
    muted: "#5d6f86",
  },
  "Math-6": {
    bgStart: "#edf1e2",
    bgEnd: "#dde8f6",
    burstA: "#b8d2ec",
    burstB: "#d5e1b7",
    panelStrong: "#fafcf4",
    accent: "#3d5fa1",
    ink: "#213655",
    muted: "#607287",
  },
  "ELAR-3": {
    bgStart: "#f9efe2",
    bgEnd: "#efe2d5",
    burstA: "#dcc3ad",
    burstB: "#edd6bf",
    panelStrong: "#fff8f1",
    accent: "#9d5a2f",
    ink: "#3d2f2a",
    muted: "#6c5b54",
  },
  "ELAR-4": {
    bgStart: "#f7ece8",
    bgEnd: "#ece4d8",
    burstA: "#d9c1c7",
    burstB: "#e7d4bb",
    panelStrong: "#fff8f4",
    accent: "#8d4157",
    ink: "#372a31",
    muted: "#675761",
  },
  "ELAR-5": {
    bgStart: "#f4ece7",
    bgEnd: "#efe6da",
    burstA: "#d8c7ba",
    burstB: "#e7d6c4",
    panelStrong: "#fff9f4",
    accent: "#7d4f3f",
    ink: "#392d29",
    muted: "#6a5c55",
  },
  "ELAR-6": {
    bgStart: "#f3ede8",
    bgEnd: "#e9e1d8",
    burstA: "#d5c0c7",
    burstB: "#e4d1bf",
    panelStrong: "#fff9f5",
    accent: "#8b4c62",
    ink: "#372a32",
    muted: "#665862",
  },
  "Science-5": {
    bgStart: "#edf4e2",
    bgEnd: "#e0efe8",
    burstA: "#b8d8bf",
    burstB: "#d8e8bf",
    panelStrong: "#f9fcf4",
    accent: "#2f7c58",
    ink: "#21382c",
    muted: "#5c7263",
  },
};

const state = {
  collectionIndex: null,
  collections: [],
  activeCollectionId: "",
  builderStore: {},
  catalog: null,
  items: [],
  itemsById: new Map(),
  stimulusGroupsById: new Map(),
  selectedIds: [],
  filters: {
    search: "",
    teks: [],
    year: [],
    difficulty: [],
    itemType: "",
    content: "",
    reviewOnly: false,
  },
  packet: {
    title: "",
    teacher: "",
    studentPrintFormat: "png",
  },
  includeInlineChoiceQuestions: false,
  selectionSummaryExpanded: false,
  teksSort: "importance",
  showResultsOcr: false,
  printMode: "",
  printPreparingMode: "",
  pdfExportMode: "",
};

const elements = {
  appLoading: document.querySelector("#app-loading"),
  appLoadingStatus: document.querySelector("#app-loading-status"),
  collectionFilter: document.querySelector("#collection-filter"),
  collectionStatus: document.querySelector("#collection-status"),
  searchInput: document.querySelector("#search-input"),
  teksFilter: document.querySelector("#teks-filter"),
  teksFilterStatus: document.querySelector("#teks-filter-status"),
  yearFilter: document.querySelector("#year-filter"),
  yearFilterStatus: document.querySelector("#year-filter-status"),
  difficultyFilter: document.querySelector("#difficulty-filter"),
  difficultyFilterStatus: document.querySelector("#difficulty-filter-status"),
  itemTypeFilter: document.querySelector("#item-type-filter"),
  contentFilter: document.querySelector("#content-filter"),
  includeInlineChoice: document.querySelector("#include-inline-choice"),
  reviewOnly: document.querySelector("#review-only"),
  resetFilters: document.querySelector("#reset-filters"),
  resultsSummary: document.querySelector("#results-summary"),
  results: document.querySelector("#results"),
  stats: document.querySelector("#catalog-stats"),
  teksGroups: document.querySelector("#teks-groups"),
  teksSort: document.querySelector("#teks-sort"),
  yearGroups: document.querySelector("#year-groups"),
  difficultyGroups: document.querySelector("#difficulty-groups"),
  teksCount: document.querySelector("#teks-count"),
  yearCount: document.querySelector("#year-count"),
  difficultyCount: document.querySelector("#difficulty-count"),
  selectionActionCopy: document.querySelector("#selection-action-copy"),
  cardTemplate: document.querySelector("#item-card-template"),
  selectedItemTemplate: document.querySelector("#selected-item-template"),
  selectedCount: document.querySelector("#selected-count"),
  selectionSummary: document.querySelector("#selection-summary"),
  testTitle: document.querySelector("#test-title"),
  teacherName: document.querySelector("#teacher-name"),
  studentPrintFormat: document.querySelector("#student-print-format"),
  studentPrintFormatNote: document.querySelector("#student-print-format-note"),
  addSelection: document.querySelector("#add-selection"),
  removeSelection: document.querySelector("#remove-selection"),
  toggleResultsOcr: document.querySelector("#toggle-results-ocr"),
  addVisible: document.querySelector("#add-visible"),
  removeVisible: document.querySelector("#remove-visible"),
  clearSelection: document.querySelector("#clear-selection"),
  presetSize: document.querySelector("#preset-size"),
  presetType: document.querySelector("#preset-type"),
  buildPreset: document.querySelector("#build-preset"),
  printTest: document.querySelector("#print-test"),
  printAnswerKey: document.querySelector("#print-answer-key"),
  downloadTestPdf: document.querySelector("#download-test-pdf"),
  downloadAnswerKeyPdf: document.querySelector("#download-answer-key-pdf"),
  printWorkspace: document.querySelector("#print-workspace"),
};

function normalizeText(value) {
  return (value || "").toLowerCase().trim();
}

function getQuestionDisplayTitle(item) {
  const stem = String(item?.question?.stem || "").replace(/\s+/g, " ").trim();
  if (stem) {
    return stem;
  }

  const year = item?.metadata?.year;
  const questionNumber = item?.metadata?.question_number;
  const questionLabel = item?.metadata?.question_label;
  const standard = item?.metadata?.standard;

  const parts = [];
  if (year) {
    parts.push(String(year));
  }
  if (questionNumber) {
    parts.push(`Q${questionNumber}`);
  } else if (questionLabel) {
    parts.push(String(questionLabel));
  }

  const baseTitle = parts.join(" - ");
  if (baseTitle && standard) {
    return `${baseTitle} | ${standard}`;
  }
  return baseTitle || standard || item.id;
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function rgbaFromHex(hex, alpha) {
  const normalized = String(hex || "").replace("#", "").trim();
  const safeHex = normalized.length === 3 ? normalized.split("").map((value) => `${value}${value}`).join("") : normalized;
  if (!/^[0-9a-fA-F]{6}$/.test(safeHex)) {
    return `rgba(0, 0, 0, ${alpha})`;
  }
  const red = Number.parseInt(safeHex.slice(0, 2), 16);
  const green = Number.parseInt(safeHex.slice(2, 4), 16);
  const blue = Number.parseInt(safeHex.slice(4, 6), 16);
  return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
}

function getCollectionTheme(collection = getActiveCollection()) {
  const subject = collection?.subject || state.catalog?.subject || "";
  const grade = String(collection?.grade || state.catalog?.grade || "");
  const presetKey = `${subject}-${grade}`;
  return {
    ...DEFAULT_THEME,
    ...(SUBJECT_THEME_DEFAULTS[subject] || {}),
    ...(COLLECTION_THEME_PRESETS[presetKey] || {}),
  };
}

function applyCollectionTheme(collection = getActiveCollection()) {
  const theme = getCollectionTheme(collection);
  const root = document.documentElement;
  const themeVars = {
    "--bg-start": theme.bgStart,
    "--bg-end": theme.bgEnd,
    "--bg-orb-a": rgbaFromHex(theme.burstA, 0.82),
    "--bg-orb-b": rgbaFromHex(theme.burstB, 0.5),
    "--panel-strong": theme.panelStrong,
    "--panel": rgbaFromHex(theme.panelStrong, 0.88),
    "--panel-soft": rgbaFromHex(theme.panelStrong, 0.92),
    "--line": rgbaFromHex(theme.ink, 0.12),
    "--ink": theme.ink,
    "--muted": theme.muted,
    "--accent": theme.accent,
    "--accent-soft": rgbaFromHex(theme.accent, 0.12),
    "--accent-soft-strong": rgbaFromHex(theme.accent, 0.1),
    "--accent-soft-surface": rgbaFromHex(theme.accent, 0.06),
    "--ink-soft-surface": rgbaFromHex(theme.ink, 0.05),
    "--ink-strong-surface": rgbaFromHex(theme.ink, 0.06),
    "--surface-selected": rgbaFromHex(theme.ink, 0.12),
    "--selection-outline": rgbaFromHex(theme.accent, 0.16),
    "--builder-gradient-a": rgbaFromHex(theme.panelStrong, 0.94),
    "--builder-gradient-b": rgbaFromHex(theme.burstA, 0.24),
    "--shadow": `0 24px 60px ${rgbaFromHex(theme.ink, 0.08)}`,
  };
  Object.entries(themeVars).forEach(([name, value]) => {
    root.style.setProperty(name, value);
  });
  document.body.dataset.subject = normalizeText(collection?.subject || "");
  document.body.dataset.grade = String(collection?.grade || "");
}

function uniqueValues(items, accessor, sorter) {
  const values = [...new Set(items.map(accessor).filter(Boolean))];
  return sorter ? values.sort(sorter) : values.sort();
}

function sortCountEntries(entries, sortMode = "importance") {
  const sortedEntries = [...entries];
  if (sortMode === "alphabetical") {
    return sortedEntries.sort(([leftLabel], [rightLabel]) => compareGroupKey(leftLabel, rightLabel));
  }
  return sortedEntries.sort((left, right) => {
    if (right[1] !== left[1]) {
      return right[1] - left[1];
    }
    return compareGroupKey(left[0], right[0]);
  });
}

function normalizeFilterValues(value) {
  if (Array.isArray(value)) {
    return [...new Set(value.map((entry) => String(entry || "").trim()).filter(Boolean))];
  }
  if (!value) {
    return [];
  }
  return [String(value).trim()].filter(Boolean);
}

function toggleFilterValue(filterKey, value) {
  const normalizedValue = String(value || "").trim();
  if (!normalizedValue) {
    return;
  }
  const activeValues = normalizeFilterValues(state.filters[filterKey]);
  state.filters[filterKey] = activeValues.includes(normalizedValue)
    ? activeValues.filter((entry) => entry !== normalizedValue)
    : [...activeValues, normalizedValue];
}

function setSingleFilterValue(filterKey, value) {
  state.filters[filterKey] = normalizeFilterValues(value);
}

function getSingleFilterValue(value) {
  const activeValues = normalizeFilterValues(value);
  return activeValues.length === 1 ? activeValues[0] : "";
}

function formatMultiFilterStatus(values, emptyLabel) {
  const activeValues = normalizeFilterValues(values);
  if (!activeValues.length) {
    return emptyLabel;
  }
  const preview = activeValues.slice(0, 2).join(", ");
  const remaining = activeValues.length - Math.min(activeValues.length, 2);
  if (remaining > 0) {
    return `${activeValues.length} selected: ${preview}, +${remaining} more`;
  }
  return `Selected: ${preview}`;
}

function renderMultiFilterStatus() {
  elements.teksFilter.value = getSingleFilterValue(state.filters.teks);
  elements.yearFilter.value = "";
  elements.difficultyFilter.value = "";
  elements.teksFilterStatus.textContent = formatMultiFilterStatus(state.filters.teks, "No TEKS selected");
  elements.yearFilterStatus.textContent = formatMultiFilterStatus(state.filters.year, "No years selected");
  elements.difficultyFilterStatus.textContent = formatMultiFilterStatus(
    state.filters.difficulty,
    "No difficulty levels selected"
  );
}

function optionMarkup(option) {
  return option.label ? `<strong>${escapeHtml(option.label)}.</strong> ${escapeHtml(option.text)}` : escapeHtml(option.text);
}

function getStudentPrintFormat() {
  return state.packet.studentPrintFormat === "ocr" ? "ocr" : "png";
}

function getStudentPrintFormatLabel() {
  return getStudentPrintFormat() === "ocr" ? "OCR text" : "Original PNG images";
}

function isInlineChoiceItem(item) {
  return item?.metadata?.item_type === "inline_choice";
}

function shouldIncludeInTeacherWorkspace(item) {
  return state.includeInlineChoiceQuestions || !isInlineChoiceItem(item);
}

function getTeacherWorkspaceItems(items = []) {
  return items.filter(shouldIncludeInTeacherWorkspace);
}

function getHiddenInlineChoiceSelectedItems() {
  return state.selectedIds
    .map((id) => state.itemsById.get(id))
    .filter((item) => item && !shouldIncludeInTeacherWorkspace(item));
}

function setStartupStatus(message) {
  if (elements.appLoadingStatus) {
    elements.appLoadingStatus.textContent = message;
  }
}

function hideStartupOverlay() {
  document.body.classList.add("app-ready");
  if (elements.appLoading) {
    elements.appLoading.setAttribute("aria-hidden", "true");
  }
}

async function releaseDesktopStartupGate() {
  hideStartupOverlay();
  await new Promise((resolve) => {
    window.setTimeout(resolve, 40);
  });

  try {
    await window.staarDesktopBridge?.notifyAppReady?.();
  } catch (error) {
    // Desktop splash release should not block the app if the bridge is unavailable.
  }
}

function difficultyClass(label) {
  return ["easy", "medium", "hard"].includes(label) ? label : "";
}

function getActiveCollection() {
  return state.collections.find((collection) => collection.id === state.activeCollectionId) || null;
}

function buildFallbackStimulusGroup(item) {
  const year = item?.metadata?.year || "unknown";
  const label = item?.metadata?.stimulus_reference || item?.stimulus?.label || "Stimulus bundle";
  return {
    id: `fallback:${year}:${label}`,
    label,
    year,
    page_count: 0,
    page_numbers: [],
    page_images: [],
    question_ids: [],
    missing: true,
  };
}

function getStimulusGroupForItem(item) {
  if (!item) {
    return null;
  }
  if (!item?.stimulus?.group_id) {
    return item.metadata?.stimulus_reference ? buildFallbackStimulusGroup(item) : null;
  }
  const group = state.stimulusGroupsById.get(item.stimulus.group_id) || null;
  if (!group) {
    return buildFallbackStimulusGroup(item);
  }

  const itemYear = Number(item.metadata?.year);
  const groupYear = Number(group.year);
  const expectedLabel = String(item.metadata?.stimulus_reference || "").trim();
  const actualLabel = String(group.label || "").trim();
  const hasYearMismatch = Number.isFinite(itemYear) && Number.isFinite(groupYear) && itemYear !== groupYear;
  const hasLabelMismatch = expectedLabel && actualLabel && expectedLabel !== actualLabel;

  if (hasYearMismatch || hasLabelMismatch) {
    return buildFallbackStimulusGroup(item);
  }

  return group;
}

function getStimulusGroupKey(item) {
  return getStimulusGroupForItem(item)?.id || `item:${item.id}`;
}

function shouldRenderStimulusBundles(collection = getActiveCollection()) {
  return collection?.subject === "ELAR" && Number(collection?.grade) === 3;
}

function buildStimulusBundles(items) {
  const bundles = [];
  const bundlesByKey = new Map();

  getSortedItems(items).forEach((item) => {
    const key = getStimulusGroupKey(item);
    if (!bundlesByKey.has(key)) {
      const bundle = {
        key,
        stimulusGroup: getStimulusGroupForItem(item),
        items: [],
      };
      bundlesByKey.set(key, bundle);
      bundles.push(bundle);
    }
    bundlesByKey.get(key).items.push(item);
  });

  return bundles;
}

function isExternalPath(value) {
  return /^https?:\/\//i.test(value) || String(value || "").startsWith("data:");
}

function normalizeRepoPath(value) {
  return String(value || "")
    .replaceAll("\\", "/")
    .replace(/^\.\//, "")
    .replace(/^\/+/, "");
}

function resolveCollectionAssetPath(pathValue, collection = getActiveCollection()) {
  if (!pathValue) {
    return "";
  }
  if (isExternalPath(pathValue)) {
    return pathValue;
  }

  const normalized = normalizeRepoPath(pathValue);
  const repoBase = new URL("../", window.location.href);

  if (normalized.startsWith("collections/") || normalized.startsWith("app/") || normalized.startsWith("docs/")) {
    return new URL(normalized, repoBase).href;
  }

  if (collection?.root) {
    const collectionRoot = normalizeRepoPath(collection.root).replace(/\/+$/, "");
    return new URL(`${collectionRoot}/${normalized}`, repoBase).href;
  }

  return new URL(normalized, repoBase).href;
}

function compareStandard(left, right) {
  return (left.metadata.standard || "").localeCompare(right.metadata.standard || "", undefined, {
    numeric: true,
    sensitivity: "base",
  });
}

function compareNewest(left, right) {
  if (right.metadata.year !== left.metadata.year) {
    return right.metadata.year - left.metadata.year;
  }
  if (compareStandard(left, right) !== 0) {
    return compareStandard(left, right);
  }
  return left.metadata.question_number - right.metadata.question_number;
}

function getPercentCorrect(item) {
  return item.metadata.difficulty?.percent_correct;
}

function getDifficultyScore(item) {
  return item.metadata.difficulty?.score;
}

function hasKnownDifficulty(item) {
  return Number.isFinite(getPercentCorrect(item));
}

function getPresetLimit() {
  return elements.presetSize.value === "all" ? Infinity : Number(elements.presetSize.value || 10);
}

function takePresetItems(items) {
  return takeUniqueItems(items);
}

function rankHardest(items) {
  return [...items].sort((left, right) => {
    const leftScore = getDifficultyScore(left) ?? -1;
    const rightScore = getDifficultyScore(right) ?? -1;
    if (rightScore !== leftScore) {
      return rightScore - leftScore;
    }
    const leftPercent = getPercentCorrect(left) ?? 101;
    const rightPercent = getPercentCorrect(right) ?? 101;
    if (leftPercent !== rightPercent) {
      return leftPercent - rightPercent;
    }
    return compareNewest(left, right);
  });
}

function rankEasiest(items) {
  return [...items].sort((left, right) => {
    const leftScore = getDifficultyScore(left) ?? 99;
    const rightScore = getDifficultyScore(right) ?? 99;
    if (leftScore !== rightScore) {
      return leftScore - rightScore;
    }
    const leftPercent = getPercentCorrect(left) ?? -1;
    const rightPercent = getPercentCorrect(right) ?? -1;
    if (rightPercent !== leftPercent) {
      return rightPercent - leftPercent;
    }
    return compareNewest(left, right);
  });
}

function compareGroupKey(left, right) {
  return String(left).localeCompare(String(right), undefined, {
    numeric: true,
    sensitivity: "base",
  });
}

function hasStimulusLink(item) {
  return Boolean(item?.stimulus?.group_id || item?.metadata?.stimulus_reference);
}

function isReadinessItem(item) {
  return item?.metadata?.content === "Readiness";
}

function isSupportingItem(item) {
  return item?.metadata?.content === "Supporting";
}

function isMultiSelectItem(item) {
  return item?.metadata?.item_type === "multiselect" || item?.answer_key?.answer_format === "multi_select_positions";
}

function isConstructedResponseItem(item) {
  return CONSTRUCTED_RESPONSE_TYPES.has(item?.metadata?.item_type || "");
}

function groupItemsBy(items, keyFn) {
  const groups = new Map();
  items.forEach((item) => {
    const key = keyFn(item);
    if (!key) {
      return;
    }
    if (!groups.has(key)) {
      groups.set(key, []);
    }
    groups.get(key).push(item);
  });
  return groups;
}

function buildGroupQueues(items, keyFn, sortItems = getSortedItems, keySort = compareGroupKey) {
  const groups = groupItemsBy(items, keyFn);
  return [...groups.entries()]
    .sort(([leftKey], [rightKey]) => keySort(leftKey, rightKey))
    .map(([, groupItems]) => sortItems(groupItems));
}

function takeUniqueItems(items, limit = getPresetLimit()) {
  const selected = [];
  const seen = new Set();
  for (const item of items) {
    if (!item || seen.has(item.id)) {
      continue;
    }
    selected.push(item);
    seen.add(item.id);
    if (Number.isFinite(limit) && selected.length >= limit) {
      break;
    }
  }
  return selected;
}

function takeUniqueFromLists(lists, limit = getPresetLimit()) {
  const queues = lists.map((list) => [...list]);
  const selected = [];
  const seen = new Set();

  while ((!Number.isFinite(limit) || selected.length < limit) && queues.some((queue) => queue.length)) {
    let addedThisPass = false;

    for (const queue of queues) {
      while (queue.length && seen.has(queue[0].id)) {
        queue.shift();
      }
      if (!queue.length) {
        continue;
      }

      const item = queue.shift();
      selected.push(item);
      seen.add(item.id);
      addedThisPass = true;

      if (Number.isFinite(limit) && selected.length >= limit) {
        break;
      }
    }

    if (!addedThisPass) {
      break;
    }
  }

  return selected;
}

function roundRobinByGroup(items, keyFn, sortItems = getSortedItems, keySort = compareGroupKey) {
  return takeUniqueFromLists(buildGroupQueues(items, keyFn, sortItems, keySort));
}

function firstPerGroup(items, keyFn, sortItems = getSortedItems, keySort = compareGroupKey) {
  const groups = groupItemsBy(items, keyFn);
  const firstItems = [...groups.entries()]
    .sort(([leftKey], [rightKey]) => keySort(leftKey, rightKey))
    .map(([, groupItems]) => sortItems(groupItems)[0])
    .filter(Boolean);
  return takeUniqueItems(firstItems);
}

function getPassageBundles(items) {
  return buildStimulusBundles(items).filter((bundle) => bundle.items.some(hasStimulusLink));
}

function compareBundleNewest(left, right) {
  const leftTop = getSortedItems(left.items)[0];
  const rightTop = getSortedItems(right.items)[0];
  if (!leftTop || !rightTop) {
    return 0;
  }
  return compareNewest(leftTop, rightTop);
}

function takePassageBundles(items, { singleBundle = false } = {}) {
  const bundles = getPassageBundles(items);
  if (!bundles.length) {
    return [];
  }

  const limit = getPresetLimit();
  const sortedBundles = [...bundles].sort((left, right) => {
    if (singleBundle && Number.isFinite(limit)) {
      const sizeDelta = Math.abs(left.items.length - limit) - Math.abs(right.items.length - limit);
      if (sizeDelta !== 0) {
        return sizeDelta;
      }
    }
    return compareBundleNewest(left, right);
  });

  if (singleBundle) {
    return getSortedItems(sortedBundles[0].items);
  }

  const selected = [];
  let selectedCount = 0;
  for (const bundle of sortedBundles) {
    if (Number.isFinite(limit) && selected.length && selectedCount >= limit) {
      break;
    }
    const bundleItems = getSortedItems(bundle.items);
    selected.push(...bundleItems);
    selectedCount += bundleItems.length;
  }

  return takeUniqueItems(selected, Infinity);
}

function rankLowRisk(items) {
  return [...items].sort((left, right) => {
    const leftConfidence = left?.extraction_quality?.vision_confidence ?? 0;
    const rightConfidence = right?.extraction_quality?.vision_confidence ?? 0;
    if (rightConfidence !== leftConfidence) {
      return rightConfidence - leftConfidence;
    }
    const leftReview = Number(Boolean(left?.extraction_quality?.needs_review));
    const rightReview = Number(Boolean(right?.extraction_quality?.needs_review));
    if (leftReview !== rightReview) {
      return leftReview - rightReview;
    }
    const leftPercent = getPercentCorrect(left) ?? -1;
    const rightPercent = getPercentCorrect(right) ?? -1;
    if (rightPercent !== leftPercent) {
      return rightPercent - leftPercent;
    }
    return compareNewest(left, right);
  });
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
  return sortCountEntries([...counts.entries()]);
}

function populateSelect(select, values, formatter = (value) => value) {
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = formatter(value);
    select.append(option);
  });
}

function resetSelectOptions(select, defaultLabel) {
  select.innerHTML = "";
  const option = document.createElement("option");
  option.value = "";
  option.textContent = defaultLabel;
  select.append(option);
}

function syncFiltersToAvailableItems(items) {
  const teksValues = new Set(items.map((item) => item.metadata.standard).filter(Boolean));
  const yearValues = new Set(items.map((item) => String(item.metadata.year)).filter(Boolean));
  const difficultyValues = new Set(items.map((item) => item.metadata.difficulty?.label).filter(Boolean));
  const itemTypeValues = new Set(items.map((item) => item.metadata.item_type).filter(Boolean));
  const contentValues = new Set(items.map((item) => item.metadata.content).filter(Boolean));

  state.filters.teks = state.filters.teks.filter((value) => teksValues.has(value));
  state.filters.year = state.filters.year.filter((value) => yearValues.has(String(value)));
  state.filters.difficulty = state.filters.difficulty.filter((value) => difficultyValues.has(value));

  if (state.filters.itemType && !itemTypeValues.has(state.filters.itemType)) {
    state.filters.itemType = "";
  }

  if (state.filters.content && !contentValues.has(state.filters.content)) {
    state.filters.content = "";
  }
}

function installStaticFilters() {
  const availableItems = getTeacherWorkspaceItems(state.items);
  syncFiltersToAvailableItems(availableItems);
  resetSelectOptions(elements.teksFilter, "All TEKS");
  resetSelectOptions(elements.yearFilter, "All years");
  resetSelectOptions(elements.difficultyFilter, "All levels");
  resetSelectOptions(elements.itemTypeFilter, "All types");
  resetSelectOptions(elements.contentFilter, "All content");
  populateSelect(elements.teksFilter, uniqueValues(availableItems, (item) => item.metadata.standard, compareGroupKey));
  populateSelect(
    elements.yearFilter,
    uniqueValues(availableItems, (item) => String(item.metadata.year), (left, right) => Number(right) - Number(left))
  );
  populateSelect(
    elements.difficultyFilter,
    uniqueValues(availableItems, (item) => item.metadata.difficulty?.label),
    (value) => value.charAt(0).toUpperCase() + value.slice(1)
  );
  populateSelect(elements.itemTypeFilter, uniqueValues(availableItems, (item) => item.metadata.item_type));
  populateSelect(elements.contentFilter, uniqueValues(availableItems, (item) => item.metadata.content));
  elements.itemTypeFilter.value = state.filters.itemType;
  elements.contentFilter.value = state.filters.content;
}

function installCollectionOptions() {
  elements.collectionFilter.innerHTML = "";
  state.collections.forEach((collection) => {
    const option = document.createElement("option");
    option.value = collection.id;
    option.textContent = `${collection.label}${collection.status !== "ready" ? ` (${collection.status.replaceAll("_", " ")})` : ""}`;
    elements.collectionFilter.append(option);
  });
  elements.collectionFilter.value = state.activeCollectionId;
}

function readStoredBuilder() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return;
    }
    const parsed = JSON.parse(raw);
    state.activeCollectionId = parsed.activeCollectionId || "";
    state.builderStore = parsed.builderStore || {};
    state.includeInlineChoiceQuestions = Boolean(parsed.includeInlineChoiceQuestions);
    state.teksSort = parsed.teksSort === "alphabetical" ? "alphabetical" : "importance";
  } catch (error) {
    state.activeCollectionId = "";
    state.builderStore = {};
    state.includeInlineChoiceQuestions = false;
    state.teksSort = "importance";
  }
}

function persistBuilder() {
  const collectionId = state.activeCollectionId || "default";
  const nextStore = {
    ...(state.builderStore || {}),
    [collectionId]: {
      selectedIds: state.selectedIds,
      packet: state.packet,
    },
  };
  state.builderStore = nextStore;
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      activeCollectionId: state.activeCollectionId,
      builderStore: nextStore,
      includeInlineChoiceQuestions: state.includeInlineChoiceQuestions,
      teksSort: state.teksSort,
    })
  );
}

function hydrateBuilderForCollection(collectionId) {
  const stored = state.builderStore?.[collectionId] || {};
  state.selectedIds = Array.isArray(stored.selectedIds) ? stored.selectedIds : [];
  state.packet.title = stored.packet?.title || "";
  state.packet.teacher = stored.packet?.teacher || "";
  state.packet.studentPrintFormat = stored.packet?.studentPrintFormat === "ocr" ? "ocr" : "png";
  state.selectionSummaryExpanded = false;
}

function attachEvents() {
  elements.collectionFilter.addEventListener("change", async (event) => {
    await switchCollection(event.target.value);
  });

  elements.searchInput.addEventListener("input", (event) => {
    state.filters.search = event.target.value;
    render();
  });

  elements.teksFilter.addEventListener("change", (event) => {
    setSingleFilterValue("teks", event.target.value);
    render();
  });

  elements.teksSort.addEventListener("change", (event) => {
    state.teksSort = event.target.value === "alphabetical" ? "alphabetical" : "importance";
    persistBuilder();
    render();
  });

  elements.yearFilter.addEventListener("change", (event) => {
    toggleFilterValue("year", event.target.value);
    event.target.value = "";
    render();
  });

  elements.difficultyFilter.addEventListener("change", (event) => {
    toggleFilterValue("difficulty", event.target.value);
    event.target.value = "";
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

  elements.includeInlineChoice.addEventListener("change", (event) => {
    state.includeInlineChoiceQuestions = event.target.checked;
    persistBuilder();
    installStaticFilters();
    render();
  });

  elements.reviewOnly.addEventListener("change", (event) => {
    state.filters.reviewOnly = event.target.checked;
    render();
  });

  elements.resetFilters.addEventListener("click", () => {
    resetFiltersState();
    render();
  });

  elements.testTitle.addEventListener("input", (event) => {
    state.packet.title = event.target.value;
    persistBuilder();
    renderBuilder();
  });

  elements.teacherName.addEventListener("input", (event) => {
    state.packet.teacher = event.target.value;
    persistBuilder();
    renderBuilder();
  });

  elements.studentPrintFormat.addEventListener("change", (event) => {
    state.packet.studentPrintFormat = event.target.value === "ocr" ? "ocr" : "png";
    persistBuilder();
    renderBuilder();
  });

  elements.presetType.addEventListener("change", () => {
    renderBuilder();
  });

  elements.addSelection.addEventListener("click", () => {
    const addedCount = addItemsToSelection(getSortedItems(getFilteredItems()));
    if (!addedCount) {
      window.alert("All questions in the current selection are already in the test.");
    }
  });

  elements.removeSelection.addEventListener("click", () => {
    const removedCount = removeItemsFromSelection(getFilteredItems().map((item) => item.id));
    if (!removedCount) {
      window.alert("No matching questions are currently in the test.");
    }
  });

  elements.toggleResultsOcr.addEventListener("click", () => {
    state.showResultsOcr = !state.showResultsOcr;
    render();
  });

  elements.addVisible.addEventListener("click", () => {
    const addedCount = addItemsToSelection(getSortedItems(getFilteredItems()));
    if (!addedCount) {
      window.alert("No filtered questions were added. They may already be selected.");
    }
  });

  elements.removeVisible.addEventListener("click", () => {
    const removedCount = removeItemsFromSelection(getFilteredItems().map((item) => item.id));
    if (!removedCount) {
      window.alert("No filtered questions were removed.");
    }
  });

  elements.clearSelection.addEventListener("click", () => {
    if (!state.selectedIds.length) {
      return;
    }
    state.selectedIds = [];
    elements.presetType.value = "";
    persistBuilder();
    render();
  });

  elements.buildPreset.addEventListener("click", () => {
    if (!elements.presetType.value) {
      window.alert("Choose a preset type first.");
      return;
    }
    applyPreset(elements.presetType.value);
  });

  elements.printTest.addEventListener("click", () => {
    preparePrint("student");
  });

  elements.printAnswerKey.addEventListener("click", () => {
    preparePrint("answer-key");
  });

  elements.downloadTestPdf.addEventListener("click", () => {
    downloadPdf("student");
  });

  elements.downloadAnswerKeyPdf.addEventListener("click", () => {
    downloadPdf("answer-key");
  });

  window.addEventListener("afterprint", () => {
    cleanupPrintWorkspace();
    if (state.printPreparingMode) {
      state.printPreparingMode = "";
      renderBuilder();
    }
  });
}

function resetFiltersState() {
  state.filters = {
    search: "",
    teks: [],
    year: [],
    difficulty: [],
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
}

async function loadCollectionCatalog(collection) {
  state.catalog = null;
  state.items = [];
  state.itemsById = new Map();
  state.stimulusGroupsById = new Map();

  if (!collection || !collection.catalog) {
    return false;
  }

  const response = await fetch(`../${collection.catalog}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  state.catalog = await response.json();
  state.items = state.catalog.items || [];
  state.itemsById = new Map(state.items.map((item) => [item.id, item]));
  state.stimulusGroupsById = new Map((state.catalog.stimulus_groups || []).map((group) => [group.id, group]));
  state.selectedIds = state.selectedIds.filter((id) => state.itemsById.has(id));
  return true;
}

async function switchCollection(collectionId) {
  state.activeCollectionId = collectionId;
  const collection = getActiveCollection();
  hydrateBuilderForCollection(collectionId);
  resetFiltersState();
  await loadCollectionCatalog(collection);
  installCollectionOptions();
  installStaticFilters();
  persistBuilder();
  render();
}

function getFilteredItems(options = {}) {
  const filters = {
    ...state.filters,
    ...(options.filters || {}),
  };
  const ignoredFilters = new Set(options.ignore || []);
  const search = normalizeText(filters.search);
  const teksFilters = normalizeFilterValues(filters.teks);
  const yearFilters = normalizeFilterValues(filters.year);
  const difficultyFilters = normalizeFilterValues(filters.difficulty);
  return getTeacherWorkspaceItems(state.items).filter((item) => {
    const haystack = normalizeText(
      [
        item.id,
        item.metadata.standard,
        item.metadata.standard_description,
        item.metadata.cluster,
        item.metadata.subcluster,
        item.metadata.content,
        item.metadata.stimulus_reference,
        item.stimulus?.label,
        item.question.stem,
        item.question.instruction,
        item.answer_key.correct_text,
        ...(item.answer_key.correct_texts || []),
      ]
        .filter(Boolean)
        .join(" ")
    );

    if (!ignoredFilters.has("teks") && teksFilters.length && !teksFilters.includes(item.metadata.standard)) {
      return false;
    }
    if (!ignoredFilters.has("year") && yearFilters.length && !yearFilters.includes(String(item.metadata.year))) {
      return false;
    }
    if (!ignoredFilters.has("difficulty") && difficultyFilters.length) {
      const difficultyLabel = item.metadata.difficulty?.label || "";
      if (!difficultyFilters.includes(difficultyLabel)) {
        return false;
      }
    }
    if (!ignoredFilters.has("itemType") && filters.itemType && item.metadata.item_type !== filters.itemType) {
      return false;
    }
    if (!ignoredFilters.has("content") && filters.content && item.metadata.content !== filters.content) {
      return false;
    }
    if (!ignoredFilters.has("reviewOnly") && filters.reviewOnly && !item.extraction_quality.needs_review) {
      return false;
    }
    if (search && !haystack.includes(search)) {
      return false;
    }
    return true;
  });
}

function getSortedItems(items) {
  return [...items].sort((left, right) => {
    if (right.metadata.year !== left.metadata.year) {
      return right.metadata.year - left.metadata.year;
    }
    if ((left.source?.page_number || 0) !== (right.source?.page_number || 0)) {
      return (left.source?.page_number || 0) - (right.source?.page_number || 0);
    }
    if (left.metadata.standard !== right.metadata.standard) {
      return left.metadata.standard.localeCompare(right.metadata.standard);
    }
    return left.metadata.question_number - right.metadata.question_number;
  });
}

function getSelectedItems() {
  return state.selectedIds.map((id) => state.itemsById.get(id)).filter((item) => item && shouldIncludeInTeacherWorkspace(item));
}

function replaceSelection(items) {
  state.selectedIds = items.map((item) => item.id);
  persistBuilder();
  render();
}

function addItemsToSelection(items) {
  let addedCount = 0;
  items.forEach((item) => {
    if (!state.selectedIds.includes(item.id)) {
      state.selectedIds.push(item.id);
      addedCount += 1;
    }
  });
  if (addedCount) {
    persistBuilder();
    render();
  }
  return addedCount;
}

function removeItemsFromSelection(ids) {
  const currentSize = state.selectedIds.length;
  const removedSet = new Set(ids);
  state.selectedIds = state.selectedIds.filter((id) => !removedSet.has(id));
  const removedCount = currentSize - state.selectedIds.length;
  if (removedCount) {
    persistBuilder();
    render();
  }
  return removedCount;
}

function toggleSelection(itemId) {
  if (state.selectedIds.includes(itemId)) {
    removeItemsFromSelection([itemId]);
    return;
  }
  addItemsToSelection([state.itemsById.get(itemId)].filter(Boolean));
}

function moveSelection(itemId, direction) {
  const index = state.selectedIds.indexOf(itemId);
  const targetIndex = index + direction;
  if (index === -1 || targetIndex < 0 || targetIndex >= state.selectedIds.length) {
    return;
  }
  const nextIds = [...state.selectedIds];
  [nextIds[index], nextIds[targetIndex]] = [nextIds[targetIndex], nextIds[index]];
  state.selectedIds = nextIds;
  persistBuilder();
  renderBuilder();
  renderResults(getSortedItems(getFilteredItems()));
}

function buildPresetSelection(presetName, pool) {
  const visiblePool = getSortedItems(pool);
  const standardKey = (item) => item.metadata.standard;
  const clusterKey = (item) => item.metadata.cluster;
  const easyItems = visiblePool.filter((item) => item.metadata.difficulty?.label === "easy");
  const mediumItems = visiblePool.filter((item) => item.metadata.difficulty?.label === "medium");
  const hardItems = visiblePool.filter((item) => item.metadata.difficulty?.label === "hard");
  const knownDifficultyItems = visiblePool.filter(hasKnownDifficulty);
  const readinessItems = visiblePool.filter(isReadinessItem);
  const supportingItems = visiblePool.filter(isSupportingItem);
  const lowRiskItems = visiblePool.filter((item) => !item.extraction_quality?.needs_review);

  switch (presetName) {
    case "hardest_test":
      return takePresetItems(rankHardest(knownDifficultyItems));
    case "easier_test":
      return takePresetItems(rankEasiest(knownDifficultyItems));
    case "easy_only":
      return takePresetItems(rankEasiest(easyItems));
    case "hard_only":
      return takePresetItems(rankHardest(hardItems));
    case "latest_only":
      return takePresetItems([...visiblePool].sort(compareNewest));
    case "spiral_review":
      return roundRobinByGroup(visiblePool, standardKey, (items) => [...items].sort(compareNewest), compareGroupKey);
    case "single_teks_mastery": {
      const selectedStandards = normalizeFilterValues(state.filters.teks);
      const targetStandard =
        selectedStandards.find((standard) => visiblePool.some((item) => item.metadata.standard === standard)) ||
        buildCounts(visiblePool, standardKey)[0]?.[0];
      if (!targetStandard) {
        return [];
      }
      const targetItems = visiblePool.filter((item) => item.metadata.standard === targetStandard);
      return takeUniqueFromLists([rankEasiest(targetItems), rankHardest(targetItems), getSortedItems(targetItems)]);
    }
    case "intervention_set": {
      const interventionPool = lowRiskItems.filter((item) => ["easy", "medium"].includes(item.metadata.difficulty?.label));
      return takeUniqueFromLists([
        ...buildGroupQueues(interventionPool.filter((item) => item.metadata.difficulty?.label === "easy"), standardKey, rankEasiest, compareGroupKey),
        ...buildGroupQueues(
          interventionPool.filter((item) => item.metadata.difficulty?.label === "medium"),
          standardKey,
          rankEasiest,
          compareGroupKey
        ),
        rankLowRisk(interventionPool),
      ]);
    }
    case "reteach_set": {
      const reteachPool = lowRiskItems.filter(hasKnownDifficulty);
      return takeUniqueFromLists([
        ...buildGroupQueues(reteachPool.filter((item) => item.metadata.difficulty?.label === "medium"), standardKey, rankHardest, compareGroupKey),
        ...buildGroupQueues(reteachPool.filter((item) => item.metadata.difficulty?.label === "hard"), standardKey, rankHardest, compareGroupKey),
        rankHardest(reteachPool),
      ]);
    }
    case "challenge_set":
      return takePresetItems(rankHardest(hardItems.length ? hardItems : knownDifficultyItems));
    case "mixed_difficulty_checkpoint":
      return takeUniqueFromLists([
        ...buildGroupQueues(easyItems, standardKey, rankEasiest, compareGroupKey),
        ...buildGroupQueues(mediumItems, standardKey, getSortedItems, compareGroupKey),
        ...buildGroupQueues(hardItems, standardKey, rankHardest, compareGroupKey),
      ]);
    case "exit_ticket":
      return takeUniqueFromLists([
        firstPerGroup(easyItems.length ? easyItems : visiblePool, standardKey, rankEasiest, compareGroupKey),
        firstPerGroup(mediumItems.length ? mediumItems : visiblePool, standardKey, getSortedItems, compareGroupKey),
        rankLowRisk(lowRiskItems),
      ]);
    case "warm_up":
      return takeUniqueFromLists([
        ...buildGroupQueues(easyItems, standardKey, rankEasiest, compareGroupKey),
        ...buildGroupQueues(mediumItems, standardKey, rankEasiest, compareGroupKey),
      ]);
    case "benchmark_lite":
      return takeUniqueFromLists([
        ...buildGroupQueues(readinessItems, standardKey, getSortedItems, compareGroupKey),
        ...buildGroupQueues(supportingItems, standardKey, getSortedItems, compareGroupKey),
      ]);
    case "latest_released_mix": {
      const latestYears = [...new Set(visiblePool.map((item) => item.metadata.year))].sort((left, right) => right - left);
      const focusYears = new Set(latestYears.slice(0, 2));
      const latestPool = visiblePool.filter((item) => focusYears.has(item.metadata.year));
      return roundRobinByGroup(latestPool, standardKey, (items) => [...items].sort(compareNewest), compareGroupKey);
    }
    case "multi_select_only":
      return takePresetItems(getSortedItems(visiblePool.filter(isMultiSelectItem)));
    case "constructed_response_only":
      return takePresetItems(getSortedItems(visiblePool.filter(isConstructedResponseItem)));
    case "passage_set":
      return takePassageBundles(visiblePool);
    case "one_passage_per_test":
      return takePassageBundles(visiblePool, { singleBundle: true });
    case "genre_mix":
      return roundRobinByGroup(visiblePool.filter((item) => item.metadata.cluster), clusterKey, getSortedItems, compareGroupKey);
    case "readiness_only":
      return takeUniqueFromLists([
        ...buildGroupQueues(readinessItems, standardKey, getSortedItems, compareGroupKey),
        rankHardest(readinessItems.filter(hasKnownDifficulty)),
      ]);
    case "supporting_only":
      return takeUniqueFromLists([
        ...buildGroupQueues(supportingItems, standardKey, getSortedItems, compareGroupKey),
        rankEasiest(supportingItems.filter(hasKnownDifficulty)),
      ]);
    case "low_review_risk":
      return takePresetItems(rankLowRisk(lowRiskItems));
    case "needs_review_audit":
      return takePresetItems(getSortedItems(visiblePool.filter((item) => item.extraction_quality?.needs_review)));
    case "year_over_year": {
      const standardYearGroups = [...groupItemsBy(visiblePool, standardKey).entries()]
        .filter(([, items]) => new Set(items.map((item) => item.metadata.year)).size > 1)
        .sort(([leftKey], [rightKey]) => compareGroupKey(leftKey, rightKey))
        .map(([, items]) =>
          [...groupItemsBy(items, (item) => item.metadata.year).entries()]
            .sort(([leftYear], [rightYear]) => Number(rightYear) - Number(leftYear))
            .map(([, yearItems]) => getSortedItems(yearItems)[0])
            .filter(Boolean)
        );
      return takeUniqueFromLists(standardYearGroups);
    }
    case "newest_per_teks":
      return roundRobinByGroup(visiblePool, standardKey, (items) => [...items].sort(compareNewest), compareGroupKey);
    case "one_per_teks":
      return firstPerGroup(visiblePool, standardKey, (items) => [...items].sort(compareNewest), compareGroupKey);
    case "mini_quiz":
      return takeUniqueFromLists([
        firstPerGroup(visiblePool, standardKey, (items) => [...items].sort(compareNewest), compareGroupKey),
        rankEasiest(easyItems),
        rankHardest(hardItems),
      ]);
    case "unit_test":
      return takeUniqueFromLists([
        ...buildGroupQueues(readinessItems, standardKey, getSortedItems, compareGroupKey),
        ...buildGroupQueues(supportingItems, standardKey, getSortedItems, compareGroupKey),
        rankHardest(hardItems),
        rankEasiest(easyItems),
      ]);
    default:
      return [];
  }
}

function applyPreset(presetName) {
  if (ELAR_ONLY_PRESETS.has(presetName) && getActiveCollection()?.subject !== "ELAR") {
    window.alert(`"${PRESET_TITLES[presetName] || "That preset"}" is only available for ELAR collections.`);
    return;
  }
  const visiblePool = getFilteredItems();
  const presetItems = buildPresetSelection(presetName, visiblePool);
  if (!presetItems.length) {
    window.alert("That preset did not find any matching questions in the current filtered results.");
    return;
  }
  replaceSelection(presetItems);
  if (!state.packet.title.trim()) {
    state.packet.title = PRESET_TITLES[presetName] || "Generated Test";
    persistBuilder();
    renderBuilder();
  }
}

function setChipGroup(container, counts, totalLabel, activeValue, onClick, options = {}) {
  container.innerHTML = "";
  const activeValues = normalizeFilterValues(activeValue);
  if (!counts.length) {
    if (activeValues.length) {
      activeValues.forEach((label) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "chip-button is-active";
        button.textContent = `${label} (0)`;
        button.addEventListener("click", () => onClick(label));
        container.append(button);
      });
      return;
    }
    const empty = document.createElement("span");
    empty.className = "chip-static";
    empty.textContent = "No data";
    container.append(empty);
    return;
  }

  const limit = options.limit ?? 18;
  const showAll = limit === "all";
  const activeSet = new Set(activeValues);
  let visibleCounts = showAll ? [...counts] : counts.slice(0, Math.max(0, limit));

  activeValues.forEach((activeLabel) => {
    if (visibleCounts.some(([label]) => label === activeLabel)) {
      return;
    }
    const activeEntry = counts.find(([label]) => label === activeLabel) || [activeLabel, 0];
    if (activeEntry) {
      if (!showAll && visibleCounts.length >= limit && limit > 0) {
        visibleCounts = visibleCounts.slice(0, -1);
      }
      visibleCounts.push(activeEntry);
    }
  });

  visibleCounts.forEach(([label, count]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `chip-button${activeSet.has(label) ? " is-active" : ""}`;
    button.textContent = `${label} (${count})`;
    button.addEventListener("click", () => onClick(label));
    container.append(button);
  });

  if (!showAll && counts.length > visibleCounts.length) {
    const tail = document.createElement("span");
    tail.className = "chip-static";
    tail.textContent = `+${counts.length - visibleCounts.length} more ${totalLabel}`;
    container.append(tail);
  }
}

function renderSummary(filteredItems) {
  const collection = getActiveCollection();
  const collectionReady = collection?.status === "ready";
  const bundleMode = shouldRenderStimulusBundles(collection);
  const catalogSubject = state.catalog?.subject || collection?.subject || "Unknown subject";
  const catalogGrade = state.catalog?.grade || collection?.grade || "?";
  const itemCount = state.catalog?.item_count || 0;
  const availableItems = getTeacherWorkspaceItems(state.items);
  const selectedItems = getSelectedItems();
  const hiddenInlineChoiceCount = state.includeInlineChoiceQuestions ? 0 : state.items.filter(isInlineChoiceItem).length;
  const hiddenSelectedInlineChoiceCount = getHiddenInlineChoiceSelectedItems().length;
  const selectedItemIds = new Set(selectedItems.map((item) => item.id));
  const visibleBundleCount = bundleMode
    ? buildStimulusBundles(filteredItems).length
    : new Set(filteredItems.map((item) => getStimulusGroupKey(item)).filter(Boolean)).size;
  const selectedVisibleCount = filteredItems.filter((item) => selectedItemIds.has(item.id)).length;
  const addableVisibleCount = filteredItems.length - selectedVisibleCount;
  const selectedQuestionNote =
    collectionReady && selectedItems.length && normalizeFilterValues(state.filters.teks).length
      ? ` Current test keeps ${selectedItems.length} saved question${
          selectedItems.length === 1 ? "" : "s"
        } while you browse other TEKS.`
      : "";

  elements.resultsSummary.textContent = bundleMode
    ? `${visibleBundleCount} passage bundles containing ${filteredItems.length} of ${availableItems.length} problems shown`
    : `${filteredItems.length} of ${availableItems.length} problems shown`;
  elements.stats.innerHTML = `
    <strong>${escapeHtml(catalogSubject)} Grade ${escapeHtml(catalogGrade)}</strong><br />
    ${itemCount} extracted items<br />
    ${
      hiddenInlineChoiceCount
        ? `${hiddenInlineChoiceCount} inline choice item${hiddenInlineChoiceCount === 1 ? "" : "s"} hidden by default<br />`
        : ""
    }
    ${visibleBundleCount} visible stimulus bundles<br />
    ${filteredItems.filter((item) => item.extraction_quality.needs_review).length} visible items marked for review<br />
    ${selectedItems.length} problems in the current test${
      hiddenSelectedInlineChoiceCount
        ? `<br />${hiddenSelectedInlineChoiceCount} saved inline choice problem${
            hiddenSelectedInlineChoiceCount === 1 ? "" : "s"
          } hidden until enabled`
        : ""
    }
  `;

  const teksCounts = buildCounts(getFilteredItems({ ignore: ["teks"] }), (item) => item.metadata.standard);
  const sortedTeksCounts = sortCountEntries(teksCounts, state.teksSort);
  const yearCounts = buildCounts(getFilteredItems({ ignore: ["year"] }), (item) => String(item.metadata.year));
  const difficultyCounts = buildCounts(getFilteredItems({ ignore: ["difficulty"] }), (item) => item.metadata.difficulty?.label);

  elements.teksCount.textContent = `${teksCounts.length} groups`;
  elements.yearCount.textContent = `${yearCounts.length} years`;
  elements.difficultyCount.textContent = `${difficultyCounts.length} levels`;
  elements.teksSort.value = state.teksSort;
  renderMultiFilterStatus();

  if (!collectionReady) {
    elements.selectionActionCopy.textContent = "This collection is indexed but does not have extracted questions yet.";
    elements.addSelection.textContent = "Add All Questions From Selection";
    elements.addSelection.disabled = true;
    elements.removeSelection.textContent = "Remove Matching Questions";
    elements.removeSelection.disabled = true;
  } else if (!filteredItems.length) {
    elements.selectionActionCopy.textContent = "No questions match the current selection yet.";
    elements.addSelection.textContent = "Add All Questions From Selection";
    elements.addSelection.disabled = true;
    elements.removeSelection.textContent = "Remove Matching Questions";
    elements.removeSelection.disabled = true;
  } else if (!addableVisibleCount) {
    elements.selectionActionCopy.textContent = `${filteredItems.length} questions match the current selection, and all of them are already in the test.`;
    elements.addSelection.textContent = "All Matching Questions Added";
    elements.addSelection.disabled = true;
    elements.removeSelection.textContent = `Remove ${selectedVisibleCount} Question${selectedVisibleCount === 1 ? "" : "s"} From Selection`;
    elements.removeSelection.disabled = false;
  } else if (!selectedVisibleCount) {
    elements.selectionActionCopy.textContent = `${filteredItems.length} questions match the current selection. ${addableVisibleCount} can be added to the test right now.`;
    elements.addSelection.textContent = `Add ${addableVisibleCount} Question${addableVisibleCount === 1 ? "" : "s"} From Selection`;
    elements.addSelection.disabled = false;
    elements.removeSelection.textContent = "No Matching Questions In Test";
    elements.removeSelection.disabled = true;
  } else {
    elements.selectionActionCopy.textContent = `${filteredItems.length} questions match the current selection. ${addableVisibleCount} can be added, and ${selectedVisibleCount} can be removed right now.`;
    elements.addSelection.textContent = `Add ${addableVisibleCount} Question${addableVisibleCount === 1 ? "" : "s"} From Selection`;
    elements.addSelection.disabled = false;
    elements.removeSelection.textContent = `Remove ${selectedVisibleCount} Question${selectedVisibleCount === 1 ? "" : "s"} From Selection`;
    elements.removeSelection.disabled = false;
  }

  if (selectedQuestionNote) {
    elements.selectionActionCopy.textContent += selectedQuestionNote;
  }

  elements.toggleResultsOcr.textContent = state.showResultsOcr ? "Hide OCR For All" : "Show OCR For All";
  elements.toggleResultsOcr.disabled = !collectionReady || !filteredItems.length;

  setChipGroup(
    elements.teksGroups,
    sortedTeksCounts,
    "TEKS groups",
    state.filters.teks,
    (label) => {
      toggleFilterValue("teks", label);
      render();
    },
    { limit: "all" }
  );
  setChipGroup(elements.yearGroups, yearCounts, "years", state.filters.year, (label) => {
    toggleFilterValue("year", label);
    render();
  });
  setChipGroup(elements.difficultyGroups, difficultyCounts, "difficulty groups", state.filters.difficulty, (label) => {
    toggleFilterValue("difficulty", label);
    render();
  });
}

function renderAnswer(item) {
  const answer = item.answer_key;
  if (answer.answer_format === "single_choice_label") {
    return `${answer.correct_label}${answer.correct_text ? ` - ${answer.correct_text}` : ""}`;
  }
  if (answer.answer_format === "multi_select_positions") {
    const joined = (answer.correct_texts || []).join("; ");
    return `positions ${(answer.correct_positions || []).join(", ")}${joined ? ` - ${joined}` : ""}`;
  }
  if (answer.answer_format === "ordered_blanks") {
    return (answer.blank_values || []).join("; ");
  }
  if (answer.correct_text) {
    return answer.correct_text;
  }
  return answer.raw_pdf_answer_text || "Unavailable";
}

function renderCard(item, options = {}) {
  const { hideStimulusMeta = false } = options;
  const collection = getActiveCollection();
  const stimulusGroup = getStimulusGroupForItem(item);
  const fragment = elements.cardTemplate.content.cloneNode(true);
  const card = fragment.querySelector(".item-card");
  const meta = fragment.querySelector(".item-meta");
  const selectButton = fragment.querySelector(".select-button");
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

  if (!hideStimulusMeta && stimulusGroup?.label) {
    const stimulusPill = document.createElement("span");
    stimulusPill.className = "meta-pill stimulus";
    stimulusPill.textContent = stimulusGroup.label;
    meta.append(stimulusPill);
  }

  if (stimulusGroup?.missing) {
    const missingPill = document.createElement("span");
    missingPill.className = "meta-pill review";
    missingPill.textContent = "passage image missing";
    meta.append(missingPill);
  }

  const difficultyLabel = item.metadata.difficulty?.label || "unknown";
  const difficultyPill = document.createElement("span");
  difficultyPill.className = `meta-pill ${difficultyClass(difficultyLabel)}`;
  difficultyPill.textContent = `${difficultyLabel} difficulty`;
  meta.append(difficultyPill);

  if (state.selectedIds.includes(item.id)) {
    const selectedPill = document.createElement("span");
    selectedPill.className = "meta-pill selected";
    selectedPill.textContent = "selected";
    meta.append(selectedPill);
    card.classList.add("is-selected");
  }

  if (item.extraction_quality.needs_review) {
    const reviewPill = document.createElement("span");
    reviewPill.className = "meta-pill review";
    reviewPill.textContent = "needs review";
    meta.append(reviewPill);
  }

  selectButton.textContent = state.selectedIds.includes(item.id) ? "Remove from Test" : "Add to Test";
  selectButton.classList.toggle("is-selected", state.selectedIds.includes(item.id));
  selectButton.addEventListener("click", () => {
    toggleSelection(item.id);
  });

  title.textContent = getQuestionDisplayTitle(item);
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
    responseTemplate.innerHTML = `<strong>Response template:</strong> ${escapeHtml(item.question.response_template)}`;
    if (item.question.choice_pool?.length) {
      responseTemplate.innerHTML += `<br /><strong>Choice pool:</strong> ${escapeHtml(item.question.choice_pool.join(", "))}`;
    }
  } else {
    responseTemplate.remove();
  }

  if (item.question.visual_elements?.length) {
    visualList.innerHTML = `<strong>Visual elements:</strong> ${escapeHtml(item.question.visual_elements.join(", "))}`;
  } else {
    visualList.remove();
  }

  image.src = resolveCollectionAssetPath(item.source.question_image, collection);
  image.alt = `${item.metadata.standard} ${item.metadata.year} question ${item.metadata.question_number}`;

  answerBlock.innerHTML = `
    <strong>Answer:</strong> ${escapeHtml(renderAnswer(item))}<br />
    <strong>Cluster:</strong> ${escapeHtml(item.metadata.cluster || "Unknown")}<br />
    <strong>Subcluster:</strong> ${escapeHtml(item.metadata.subcluster || "Unknown")}${
      stimulusGroup?.label ? `<br /><strong>Stimulus:</strong> ${escapeHtml(stimulusGroup.label)}` : ""
    }
  `;

  difficultyBlock.innerHTML = `
    <strong>State % correct:</strong> ${item.metadata.difficulty?.percent_correct ?? "n/a"}<br />
    <strong>Difficulty score:</strong> ${item.metadata.difficulty?.score ?? "n/a"}${item.metadata.difficulty?.score ? "/5" : ""}<br />
    <strong>Why:</strong> ${escapeHtml(item.metadata.difficulty?.rationale || "No rationale")}<br />
    <strong>Vision confidence:</strong> ${item.extraction_quality.vision_confidence ?? "n/a"}
  `;

  card.dataset.id = item.id;
  card.classList.toggle("is-ocr-collapsed", !state.showResultsOcr);
  return card;
}

function renderStimulusBundle(bundle) {
  const collection = getActiveCollection();
  const stimulusGroup = bundle.stimulusGroup;
  const article = document.createElement("article");
  article.className = "stimulus-bundle";

  const selectedCount = bundle.items.filter((item) => state.selectedIds.includes(item.id)).length;
  if (selectedCount === bundle.items.length) {
    article.classList.add("is-selected");
  }

  const header = document.createElement("div");
  header.className = "stimulus-bundle-header";

  const copy = document.createElement("div");
  copy.className = "stimulus-bundle-copy";

  const eyebrow = document.createElement("p");
  eyebrow.className = "eyebrow";
  eyebrow.textContent = "Passage Bundle";
  copy.append(eyebrow);

  const title = document.createElement("h3");
  title.className = "stimulus-bundle-title";
  title.textContent =
    stimulusGroup?.label || bundle.items[0]?.metadata?.stimulus_reference || "Stimulus-linked questions";
  copy.append(title);

  const note = document.createElement("p");
  note.className = "stimulus-bundle-note";
  const totalQuestionCount = stimulusGroup?.question_ids?.length || bundle.items.length;
  note.textContent =
    totalQuestionCount > bundle.items.length
      ? `Showing ${bundle.items.length} of ${totalQuestionCount} questions from this passage based on the current filters.`
      : `${bundle.items.length} questions are linked to this passage.`;
  copy.append(note);

  const meta = document.createElement("div");
  meta.className = "stimulus-bundle-meta";
  [
    String(bundle.items[0]?.metadata?.year || stimulusGroup?.year || ""),
    `${bundle.items.length} question${bundle.items.length === 1 ? "" : "s"}`,
    stimulusGroup?.page_images?.length
      ? `${stimulusGroup.page_images.length} passage page${stimulusGroup.page_images.length === 1 ? "" : "s"}`
      : "passage image missing",
    selectedCount ? `${selectedCount} selected` : "",
  ]
    .filter(Boolean)
    .forEach((value) => {
      const pill = document.createElement("span");
      pill.className = "meta-pill";
      pill.textContent = value;
      meta.append(pill);
    });
  copy.append(meta);

  const actions = document.createElement("div");
  actions.className = "stimulus-bundle-actions";

  const toggleBundleButton = document.createElement("button");
  toggleBundleButton.type = "button";
  toggleBundleButton.className = "tiny-button";
  if (selectedCount === bundle.items.length) {
    toggleBundleButton.textContent = "Remove Passage Questions";
    toggleBundleButton.addEventListener("click", () => {
      removeItemsFromSelection(bundle.items.map((item) => item.id));
    });
  } else if (selectedCount > 0) {
    toggleBundleButton.textContent = `Add ${bundle.items.length - selectedCount} Remaining Questions`;
    toggleBundleButton.addEventListener("click", () => {
      addItemsToSelection(bundle.items.filter((item) => !state.selectedIds.includes(item.id)));
    });
  } else {
    toggleBundleButton.textContent = `Add All ${bundle.items.length} Questions`;
    toggleBundleButton.addEventListener("click", () => {
      addItemsToSelection(bundle.items);
    });
  }
  actions.append(toggleBundleButton);

  header.append(copy, actions);
  article.append(header);

  if (stimulusGroup?.page_images?.length) {
    const gallery = document.createElement("div");
    gallery.className = "stimulus-bundle-gallery";

    stimulusGroup.page_images.forEach((imagePath, index) => {
      const image = document.createElement("img");
      image.className = "stimulus-bundle-image";
      image.src = resolveCollectionAssetPath(imagePath, collection);
      image.alt = `${title.textContent} page ${index + 1}`;
      image.loading = "lazy";
      gallery.append(image);
    });

    article.append(gallery);
  } else {
    const warning = document.createElement("div");
    warning.className = "stimulus-bundle-warning";
    warning.textContent =
      "Passage image is missing in this catalog. Keep these questions out of student packets until the source passage is recovered.";
    article.append(warning);
  }

  const questionList = document.createElement("div");
  questionList.className = "stimulus-question-list";
  bundle.items.forEach((item) => {
    const card = renderCard(item, { hideStimulusMeta: true });
    card.classList.add("stimulus-question-card");
    questionList.append(card);
  });
  article.append(questionList);

  return article;
}

function renderResults(filteredItems) {
  elements.results.innerHTML = "";
  const collection = getActiveCollection();
  if (collection && collection.status !== "ready") {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = `${collection.label} is indexed but does not have an extracted catalog yet. Add source files and run the extraction pipeline for this collection.`;
    elements.results.append(empty);
    return;
  }
  if (!filteredItems.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "No problems match the current filters.";
    elements.results.append(empty);
    return;
  }

  if (shouldRenderStimulusBundles(collection)) {
    buildStimulusBundles(filteredItems).forEach((bundle) => {
      elements.results.append(renderStimulusBundle(bundle));
    });
    return;
  }

  filteredItems.forEach((item) => {
    elements.results.append(renderCard(item));
  });
}

function renderBuilder() {
  const collection = getActiveCollection();
  const selectedItems = getSelectedItems();
  const hiddenInlineChoiceSelectedItems = getHiddenInlineChoiceSelectedItems();
  const teksCounts = buildCounts(selectedItems, (item) => item.metadata.standard);
  const typeCounts = buildCounts(selectedItems, (item) => item.metadata.item_type);
  const stimulusGroupCount = new Set(selectedItems.map((item) => item.stimulus?.group_id).filter(Boolean)).size;

  elements.selectedCount.textContent = hiddenInlineChoiceSelectedItems.length
    ? `${selectedItems.length} selected, ${hiddenInlineChoiceSelectedItems.length} inline hidden`
    : `${selectedItems.length} selected`;
  elements.testTitle.value = state.packet.title;
  elements.teacherName.value = state.packet.teacher;
  elements.studentPrintFormat.value = getStudentPrintFormat();
  elements.studentPrintFormatNote.hidden = getStudentPrintFormat() !== "ocr";
  elements.studentPrintFormatNote.textContent =
    "OCR text may not preserve the original layout exactly. Review each problem before printing or sharing.";
  const collectionReady = collection?.status === "ready";
  const exportLocked = Boolean(state.pdfExportMode);
  const printLocked = Boolean(state.printPreparingMode);
  const outputLocked = exportLocked || printLocked;
  elements.printTest.disabled = selectedItems.length === 0 || !collectionReady || outputLocked;
  elements.printAnswerKey.disabled = selectedItems.length === 0 || !collectionReady || outputLocked;
  elements.downloadTestPdf.disabled = selectedItems.length === 0 || !collectionReady || outputLocked;
  elements.downloadAnswerKeyPdf.disabled = selectedItems.length === 0 || !collectionReady || outputLocked;
  elements.printTest.textContent =
    state.printPreparingMode === "student" ? "Preparing Student Print..." : "Print Student Test";
  elements.printAnswerKey.textContent =
    state.printPreparingMode === "answer-key" ? "Preparing Answer Key Print..." : "Print Answer Key";
  elements.downloadTestPdf.textContent =
    state.pdfExportMode === "student" ? "Preparing Student PDF..." : "Download Student PDF";
  elements.downloadAnswerKeyPdf.textContent =
    state.pdfExportMode === "answer-key" ? "Preparing Answer Key PDF..." : "Download Answer Key PDF";
  elements.clearSelection.disabled = state.selectedIds.length === 0;
  elements.addVisible.disabled = !collectionReady;
  elements.removeVisible.disabled = !collectionReady;
  elements.buildPreset.disabled = !collectionReady || !elements.presetType.value;

  if (!collectionReady) {
    elements.selectionSummary.innerHTML = `
      <div class="empty-selection">
        This collection is scaffolded but does not have an extracted catalog yet.
      </div>
    `;
    return;
  }

  if (!selectedItems.length) {
    elements.selectionSummary.innerHTML = `
      <div class="empty-selection">
        ${
          hiddenInlineChoiceSelectedItems.length
            ? `${hiddenInlineChoiceSelectedItems.length} inline choice question${
                hiddenInlineChoiceSelectedItems.length === 1 ? " is" : "s are"
              } currently hidden. Turn on Include inline choice questions to use them in this test.`
            : "Filter the catalog, add the problems you want, and print a ready-to-use student packet and answer key."
        }
      </div>
    `;
    return;
  }

  const summaryHtml = `
    <div class="selection-metrics">
      <span class="chip-static">${selectedItems.length} questions</span>
      <span class="chip-static">${teksCounts.length} TEKS groups</span>
      <span class="chip-static">${typeCounts.length} item types</span>
      <span class="chip-static">${stimulusGroupCount} stimulus bundles</span>
      <span class="chip-static">${escapeHtml(getStudentPrintFormatLabel())}</span>
    </div>
    <div class="selection-bands">
      <div><strong>TEKS:</strong> ${escapeHtml(teksCounts.map(([label, count]) => `${label} (${count})`).join("; "))}</div>
      <div><strong>Item types:</strong> ${escapeHtml(typeCounts.map(([label, count]) => `${label} (${count})`).join("; "))}</div>
      <div><strong>Student packet format:</strong> ${escapeHtml(getStudentPrintFormatLabel())}</div>
      ${
        stimulusGroupCount
          ? "<div><strong>Print note:</strong> ELAR stimulus pages will print with the linked questions.</div>"
          : ""
      }
    </div>
  `;

  elements.selectionSummary.innerHTML = `
    <details class="selection-disclosure"${state.selectionSummaryExpanded ? " open" : ""}>
      <summary class="selection-disclosure-summary">
        <div class="selection-disclosure-heading">
          <div class="selection-disclosure-copy">
            <div class="selection-disclosure-title">Selected packet details</div>
            <p class="selection-disclosure-note">
              Review question order, TEKS coverage, item types, and packet format.
            </p>
          </div>
          <div class="selection-disclosure-pills">
            <span class="count-pill">${selectedItems.length} questions</span>
            <span class="selection-disclosure-toggle" aria-hidden="true"></span>
          </div>
        </div>
      </summary>
      <div class="selection-disclosure-body">
        ${summaryHtml}
      </div>
    </details>
  `;

  const disclosure = elements.selectionSummary.querySelector(".selection-disclosure");
  const disclosureBody = disclosure.querySelector(".selection-disclosure-body");
  disclosure.addEventListener("toggle", () => {
    if (state.selectionSummaryExpanded === disclosure.open) {
      return;
    }
    state.selectionSummaryExpanded = disclosure.open;
  });
  const list = document.createElement("div");
  list.className = "selected-item-list";

  selectedItems.forEach((item, index) => {
    const stimulusGroup = getStimulusGroupForItem(item);
    const fragment = elements.selectedItemTemplate.content.cloneNode(true);
    const title = fragment.querySelector(".selected-item-title");
    const meta = fragment.querySelector(".selected-item-meta");
    const moveUp = fragment.querySelector(".move-up");
    const moveDown = fragment.querySelector(".move-down");
    const removeButton = fragment.querySelector(".remove-item");

    title.textContent = `${index + 1}. ${getQuestionDisplayTitle(item)}`;
    meta.textContent = `${item.metadata.standard} | ${item.metadata.year} | ${item.metadata.item_type}${
      stimulusGroup?.label ? ` | ${stimulusGroup.label}` : ""
    }`;
    moveUp.disabled = index === 0;
    moveDown.disabled = index === selectedItems.length - 1;

    moveUp.addEventListener("click", () => moveSelection(item.id, -1));
    moveDown.addEventListener("click", () => moveSelection(item.id, 1));
    removeButton.addEventListener("click", () => removeItemsFromSelection([item.id]));

    list.append(fragment);
  });

  disclosureBody.append(list);
}

function render() {
  const collection = getActiveCollection();
  applyCollectionTheme(collection);
  elements.collectionFilter.value = state.activeCollectionId;
  elements.includeInlineChoice.checked = state.includeInlineChoiceQuestions;
  elements.collectionStatus.textContent = collection
    ? collection.status === "ready"
      ? `${collection.label} is ready for browsing and printing.`
      : `${collection.label} is indexed as ${collection.status.replaceAll("_", " ")}.`
    : "No collection selected.";
  const filteredItems = getSortedItems(getFilteredItems());
  renderSummary(filteredItems);
  renderBuilder();
  renderResults(filteredItems);
}

function buildPrintChunks(selectedItems) {
  const chunks = [];
  selectedItems.forEach((item) => {
    const groupKey = getStimulusGroupKey(item);
    const previousChunk = chunks[chunks.length - 1];
    if (!previousChunk || previousChunk.groupKey !== groupKey) {
      chunks.push({
        groupKey,
        stimulusGroup: getStimulusGroupForItem(item),
        items: [item],
      });
      return;
    }
    previousChunk.items.push(item);
  });
  return chunks;
}

function buildPacketTitle() {
  const collection = getActiveCollection();
  return (
    state.packet.title.trim() ||
    `${state.catalog?.subject || collection?.subject || "STAAR"} Grade ${state.catalog?.grade || collection?.grade || ""} Test`
  );
}

function buildPrintOptionMarkup(option, index) {
  const label = option.label || String(option.position || index + 1);
  return `
    <li class="print-option-item">
      <span class="print-option-tag">${escapeHtml(label)}</span>
      <span>${escapeHtml(option.text || "")}</span>
    </li>
  `;
}

function buildPrintResponseTemplateMarkup(template) {
  return escapeHtml(template || "").replace(/\[[^\]]+\]/g, '<span class="print-blank">________</span>');
}

function buildStudentQuestionImageMarkup(item, questionNumber, collection) {
  return `
    <section class="print-question" data-item-id="${escapeHtml(item.id)}" data-question-number="${questionNumber}">
      <div class="print-question-header">
        <span>Question ${questionNumber}</span>
      </div>
      <img class="print-question-image" src="${escapeHtml(
        resolveCollectionAssetPath(item.source.question_image, collection)
      )}" alt="Question ${questionNumber}" loading="eager" decoding="sync" fetchpriority="high" />
    </section>
  `;
}

function buildStudentQuestionOcrMarkup(item, questionNumber, options = {}) {
  const hasOptions = Boolean(item.question.options?.length);
  const hasResponseTemplate = Boolean(item.question.response_template);
  const hasChoicePool = Boolean(item.question.choice_pool?.length);
  const hasVisualElements = Boolean(item.question.visual_elements?.length);
  const needsResponseLines = !hasOptions;
  const fallbackNotice = options.fallbackNotice || "";

  return `
    <section class="print-question print-question-ocr" data-item-id="${escapeHtml(item.id)}" data-question-number="${questionNumber}">
      <div class="print-question-header">
        <span>Question ${questionNumber}</span>
        <span class="print-question-type">${escapeHtml(item.metadata.declared_item_type_display || item.metadata.item_type || "")}</span>
      </div>
      ${
        fallbackNotice
          ? `<div class="print-image-fallback-note">${escapeHtml(fallbackNotice)}</div>`
          : ""
      }
      <div class="print-question-stem">${escapeHtml(getQuestionDisplayTitle(item))}</div>
      ${
        item.question.instruction
          ? `<div class="print-question-instruction">${escapeHtml(item.question.instruction)}</div>`
          : ""
      }
      ${
        hasOptions
          ? `
            <ol class="print-option-list">
              ${item.question.options.map((option, index) => buildPrintOptionMarkup(option, index)).join("")}
            </ol>
          `
          : ""
      }
      ${
        hasResponseTemplate
          ? `
            <div class="print-response-block">
              <div class="print-response-label">Response template</div>
              <div class="print-response-template">${buildPrintResponseTemplateMarkup(item.question.response_template)}</div>
            </div>
          `
          : ""
      }
      ${
        hasChoicePool
          ? `
            <div class="print-choice-pool">
              <strong>Choice pool:</strong> ${escapeHtml(item.question.choice_pool.join(", "))}
            </div>
          `
          : ""
      }
      ${
        hasVisualElements
          ? `
            <div class="print-visual-elements">
              <strong>Included visual/text elements:</strong> ${escapeHtml(item.question.visual_elements.join("; "))}
            </div>
          `
          : ""
      }
      ${
        needsResponseLines
          ? `
            <div class="print-response-lines">
              <div class="print-response-label">Student response</div>
              <div class="print-line"></div>
              <div class="print-line"></div>
            </div>
          `
          : ""
      }
    </section>
  `;
}

function buildStudentQuestionMarkup(item, questionNumber, collection) {
  if (getStudentPrintFormat() === "ocr") {
    return buildStudentQuestionOcrMarkup(item, questionNumber);
  }
  return buildStudentQuestionImageMarkup(item, questionNumber, collection);
}

function buildStudentPrintMarkup(selectedItems) {
  const collection = getActiveCollection();
  const testTitle = buildPacketTitle();
  const chunks = buildPrintChunks(selectedItems);
  const studentPrintFormat = getStudentPrintFormat();
  let questionNumber = 0;
  return `
    <div class="print-document print-document-student">
      <section class="print-cover">
        <p class="print-eyebrow">Student Test</p>
        <h1>${escapeHtml(testTitle)}</h1>
        <div class="print-cover-lines">
          <div><strong>Teacher / Class:</strong> ${escapeHtml(state.packet.teacher || "____________________________")}</div>
          <div><strong>Name:</strong> ____________________________</div>
          <div><strong>Date:</strong> ____________________________</div>
          <div><strong>Question format:</strong> ${escapeHtml(getStudentPrintFormatLabel())}</div>
        </div>
        <p class="print-instructions">Answer each question. Show work where needed.</p>
        ${
          studentPrintFormat === "ocr"
            ? '<p class="print-instructions">Passage bundles still print from the original PNG pages so reading selections stay intact.</p>'
            : ""
        }
      </section>
      ${chunks
        .map((chunk) => {
          const startNumber = questionNumber + 1;
          questionNumber += chunk.items.length;
          const endNumber = questionNumber;
          const stimulusMarkup = chunk.stimulusGroup
            ? `
              <section class="print-stimulus">
                <div class="print-stimulus-header">
                  <div class="print-stimulus-title">${escapeHtml(chunk.stimulusGroup.label)}</div>
                  <div class="print-stimulus-note">Questions ${startNumber}-${endNumber} use this passage set.</div>
                </div>
                ${
                  chunk.stimulusGroup.page_images?.length
                    ? `
                      <div class="print-stimulus-gallery">
                        ${(chunk.stimulusGroup.page_images || [])
                          .map(
                            (imagePath, imageIndex) => `
                              <img
                                class="print-stimulus-image"
                                src="${escapeHtml(resolveCollectionAssetPath(imagePath, collection))}"
                                alt="${escapeHtml(chunk.stimulusGroup.label)} page ${imageIndex + 1}"
                                loading="eager"
                                decoding="sync"
                                fetchpriority="high"
                              />
                            `
                          )
                          .join("")}
                      </div>
                    `
                    : `
                      <div class="print-stimulus-missing">
                        Passage image missing for ${escapeHtml(chunk.stimulusGroup.label)}. Do not use this packet until the source passage is restored.
                      </div>
                    `
                }
              </section>
            `
            : "";

          let localQuestionNumber = startNumber;
          const questionMarkup = chunk.items
            .map((item) => {
              const currentNumber = localQuestionNumber;
              localQuestionNumber += 1;
              return buildStudentQuestionMarkup(item, currentNumber, collection);
            })
            .join("");

          return `${stimulusMarkup}${questionMarkup}`;
        })
        .join("")}
    </div>
  `;
}

function buildAnswerKeyMarkup(selectedItems) {
  const testTitle = buildPacketTitle();
  return `
    <div class="print-document print-document-key">
      <section class="print-cover print-cover-key">
        <p class="print-eyebrow">Teacher Answer Key</p>
        <h1>${escapeHtml(testTitle)}</h1>
        <div class="print-cover-lines">
          <div><strong>Teacher / Class:</strong> ${escapeHtml(state.packet.teacher || "Not provided")}</div>
          <div><strong>Questions:</strong> ${selectedItems.length}</div>
        </div>
      </section>
      <section class="answer-key-list">
        ${selectedItems
          .map(
            (item, index) => `
              <article class="answer-key-row">
                <div class="answer-key-row-main">
                  <div class="answer-key-number">Q${index + 1}</div>
                  <div>
                    <div class="answer-key-stem">${escapeHtml(getQuestionDisplayTitle(item))}</div>
                    <div class="answer-key-meta">
                      TEKS ${escapeHtml(item.metadata.standard)} | ${item.metadata.year} | ${escapeHtml(item.metadata.item_type)}${
                        item.stimulus?.label ? ` | ${escapeHtml(item.stimulus.label)}` : ""
                      }
                    </div>
                  </div>
                </div>
                <div class="answer-key-answer">
                  <strong>Answer:</strong> ${escapeHtml(renderAnswer(item))}<br />
                  <strong>State % correct:</strong> ${item.metadata.difficulty?.percent_correct ?? "n/a"}<br />
                  <strong>Difficulty:</strong> ${escapeHtml(item.metadata.difficulty?.label || "unknown")}
                </div>
              </article>
            `
          )
          .join("")}
      </section>
    </div>
  `;
}

function buildPrintableMarkup(mode, selectedItems) {
  return mode === "student" ? buildStudentPrintMarkup(selectedItems) : buildAnswerKeyMarkup(selectedItems);
}

function isRenderableImage(image) {
  return Boolean(image?.complete && image.naturalWidth > 0 && image.naturalHeight > 0);
}

function repairPrintableImageFailures(mode) {
  if (mode !== "student") {
    return;
  }

  const exportSource = getPdfExportSource();

  exportSource.querySelectorAll(".print-question[data-item-id]").forEach((section) => {
    const image = section.querySelector(".print-question-image");
    if (!image || isRenderableImage(image)) {
      return;
    }

    const item = state.itemsById.get(section.dataset.itemId || "");
    const questionNumber = Number(section.dataset.questionNumber || 0);
    if (!item || !questionNumber) {
      image.replaceWith(document.createTextNode("Question image unavailable for export."));
      return;
    }

    section.outerHTML = buildStudentQuestionOcrMarkup(item, questionNumber, {
      fallbackNotice: "Source image unavailable for PDF export. Showing OCR text instead.",
    });
  });

  exportSource.querySelectorAll(".print-stimulus").forEach((section) => {
    const images = [...section.querySelectorAll(".print-stimulus-image")];
    if (!images.length || images.every(isRenderableImage)) {
      return;
    }

    const gallery = section.querySelector(".print-stimulus-gallery");
    if (!gallery) {
      return;
    }

    gallery.outerHTML = `
      <div class="print-stimulus-missing">
        Passage image could not be loaded for PDF export. Questions will still print, but restore the source passage before using this packet.
      </div>
    `;
  });
}

function mountPrintWorkspace(mode, selectedItems, options = {}) {
  state.printMode = mode;
  elements.printWorkspace.innerHTML = buildPrintableMarkup(mode, selectedItems);
  elements.printWorkspace.setAttribute("aria-hidden", "false");
  document.body.classList.toggle("is-printing-student", mode === "student");
  document.body.classList.toggle("is-printing-answer-key", mode === "answer-key");

  if (options.exportingPdf || options.preparingPrint) {
    if (options.exportingPdf) {
      elements.printWorkspace.dataset.exporting = "true";
    }
    if (options.preparingPrint) {
      elements.printWorkspace.dataset.preparingPrint = "true";
    }
    Object.assign(elements.printWorkspace.style, {
      display: "block",
      position: "fixed",
      left: "-200vw",
      top: "0",
      width: "8.5in",
      padding: "0.45in 0.55in",
      background: "#fff",
      zIndex: "-1",
    });
  }
}

function sanitizeFilename(value) {
  const normalized = String(value || "")
    .replace(/[<>:"/\\|?*\u0000-\u001f]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  return normalized || "STAAR Packet";
}

function buildPdfFilename(mode) {
  const suffix = mode === "student" ? "Student Test" : "Answer Key";
  return `${sanitizeFilename(buildPacketTitle())} - ${suffix}.pdf`;
}

function buildPdfExportOptions(mode) {
  const exportScale = Math.max(1.5, Math.min(window.devicePixelRatio || 1, 2));
  return {
    filename: buildPdfFilename(mode),
    margin: 0,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: {
      scale: exportScale,
      useCORS: true,
      backgroundColor: "#ffffff",
      scrollX: 0,
      scrollY: 0,
    },
    jsPDF: {
      unit: "in",
      format: "letter",
      orientation: "portrait",
    },
    pagebreak: {
      mode: ["css", "legacy"],
    },
  };
}

async function buildPdfBytes(mode, exportSource) {
  const worker = window.html2pdf().set(buildPdfExportOptions(mode)).from(exportSource);
  await worker.toPdf();
  const pdf = await worker.get("pdf");
  return new Uint8Array(pdf.output("arraybuffer"));
}

async function trySavePdfWithDesktopDialog(mode, exportSource) {
  const isTauriDesktop = window.staarDesktopBridge?.isTauriDesktop;
  const savePdfWithDialog = window.staarDesktopBridge?.savePdfWithDialog;
  if (typeof isTauriDesktop !== "function" || !isTauriDesktop() || typeof savePdfWithDialog !== "function") {
    return false;
  }
  const pdfBytes = await buildPdfBytes(mode, exportSource);
  const savedPath = await savePdfWithDialog(buildPdfFilename(mode), pdfBytes);
  return savedPath !== undefined;
}

function waitForImageLoad(image) {
  const waitForEvent = new Promise((resolve) => {
    if (image.complete) {
      resolve();
      return;
    }
    const finish = () => resolve();
    image.addEventListener("load", finish, { once: true });
    image.addEventListener("error", finish, { once: true });
  });

  const waitForDecode =
    typeof image.decode === "function"
      ? image.decode().catch(() => {})
      : Promise.resolve();

  const timeout = new Promise((resolve) => {
    window.setTimeout(resolve, 10000);
  });

  return Promise.race([Promise.all([waitForEvent, waitForDecode]), timeout]);
}

async function waitForPrintableContent(container) {
  const images = [...container.querySelectorAll("img")];
  await Promise.all(images.map(waitForImageLoad));
  if (document.fonts?.ready) {
    try {
      await document.fonts.ready;
    } catch (error) {
      // Font readiness should not block printing forever.
    }
  }
  await new Promise((resolve) => {
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        window.setTimeout(resolve, 120);
      });
    });
  });
}

function cleanupPrintWorkspace() {
  elements.printWorkspace.innerHTML = "";
  elements.printWorkspace.setAttribute("aria-hidden", "true");
  elements.printWorkspace.removeAttribute("data-exporting");
  elements.printWorkspace.removeAttribute("data-preparing-print");
  elements.printWorkspace.removeAttribute("style");
  document.body.classList.remove("is-printing-student", "is-printing-answer-key");
  state.printMode = "";
}

function releasePrintWorkspaceForPrint() {
  elements.printWorkspace.removeAttribute("data-preparing-print");
  elements.printWorkspace.removeAttribute("style");
}

function getPdfExportSource() {
  return elements.printWorkspace.firstElementChild || elements.printWorkspace;
}

async function preparePrint(mode) {
  const selectedItems = getSelectedItems();
  if (!selectedItems.length) {
    window.alert("Select at least one problem before printing.");
    return;
  }
  if (state.pdfExportMode || state.printPreparingMode) {
    return;
  }

  state.printPreparingMode = mode;
  renderBuilder();

  try {
    mountPrintWorkspace(mode, selectedItems, { preparingPrint: true });
    await waitForPrintableContent(elements.printWorkspace);
    repairPrintableImageFailures(mode);
    releasePrintWorkspaceForPrint();
    await new Promise((resolve) => {
      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(resolve);
      });
    });
    window.print();
  } catch (error) {
    cleanupPrintWorkspace();
    state.printPreparingMode = "";
    renderBuilder();
    window.alert(`Unable to prepare print preview. ${error.message || "Please try again."}`);
  }
}

async function downloadPdf(mode) {
  const selectedItems = getSelectedItems();
  if (!selectedItems.length) {
    window.alert("Select at least one problem before downloading a PDF.");
    return;
  }
  if (state.pdfExportMode) {
    return;
  }
  if (typeof window.html2pdf !== "function") {
    window.alert("The PDF export library did not load. Refresh the page and try again.");
    return;
  }

  state.pdfExportMode = mode;
  renderBuilder();

  try {
    mountPrintWorkspace(mode, selectedItems, { exportingPdf: true });
    await waitForPrintableContent(elements.printWorkspace);
    repairPrintableImageFailures(mode);
    const exportSource = getPdfExportSource();
    if (await trySavePdfWithDesktopDialog(mode, exportSource)) {
      return;
    }

    await window.html2pdf().set(buildPdfExportOptions(mode)).from(exportSource).save();
  } catch (error) {
    window.alert(`Unable to download PDF. ${error.message || "Please try again."}`);
  } finally {
    cleanupPrintWorkspace();
    state.pdfExportMode = "";
    renderBuilder();
  }
}

async function init() {
  try {
    setStartupStatus("Loading saved teacher settings and recent selections.");
    readStoredBuilder();
    setStartupStatus("Loading the bundled collections index.");
    const response = await fetch("../collections/index.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    state.collectionIndex = await response.json();
    state.collections = state.collectionIndex.collections || [];
    state.activeCollectionId =
      state.collections.find((collection) => collection.id === state.activeCollectionId)?.id ||
      state.collectionIndex.default_collection_id ||
      state.collections[0]?.id ||
      "";
    if (!state.activeCollectionId) {
      throw new Error("No collections found in collections/index.json.");
    }
    attachEvents();
    installCollectionOptions();
    const initialCollection = state.collections.find((collection) => collection.id === state.activeCollectionId);
    setStartupStatus(`Opening ${initialCollection?.label || "the selected collection"} and preparing print tools.`);
    await switchCollection(state.activeCollectionId);
  } catch (error) {
    elements.resultsSummary.textContent = "Catalog failed to load.";
    elements.results.innerHTML = `<div class="empty-state">Unable to load collections/index.json. ${escapeHtml(error.message)}</div>`;
  } finally {
    await releaseDesktopStartupGate();
  }
}

init();
