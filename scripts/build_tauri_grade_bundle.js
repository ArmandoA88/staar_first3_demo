const childProcess = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const tauriTargetRoot = path.join(root, "src-tauri", "target");
const buildConfigRoot = path.join(root, "build", "tauri", "configs");
const baseConfigPath = path.join(root, "src-tauri", "tauri.conf.json");
const platformConfigPaths = {
  windows: path.join(root, "src-tauri", "tauri.windows.msi.root.conf.json"),
  macos: path.join(root, "src-tauri", "tauri.macos.conf.json"),
};

function parseArgs(argv) {
  const parsed = { _: [] };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) {
      parsed._.push(token);
      continue;
    }

    const key = token.slice(2);
    const next = argv[index + 1];
    if (!next || next.startsWith("--")) {
      parsed[key] = true;
      continue;
    }

    parsed[key] = next;
    index += 1;
  }

  return parsed;
}

function parseBuildScopes(args) {
  if (args.grade) {
    return [normalizeBuildScope(args.grade)];
  }

  if (args.grades) {
    return String(args.grades)
      .split(",")
      .map((value) => normalizeBuildScope(value.trim()));
  }

  if (process.env.npm_config_grade && process.env.npm_config_grade !== "true") {
    return [normalizeBuildScope(process.env.npm_config_grade)];
  }

  if (process.env.npm_config_grades && process.env.npm_config_grades !== "true") {
    return String(process.env.npm_config_grades)
      .split(",")
      .map((value) => normalizeBuildScope(value.trim()));
  }

  if (args._.length === 1) {
    return [normalizeBuildScope(args._[0])];
  }

  throw new Error("Pass --grade <number|all> or --grades <comma-separated list>.");
}

function normalizeBuildScope(value) {
  const normalized = String(value).trim().toLowerCase();
  if (["all", "all-grades", "combined", "full"].includes(normalized)) {
    return {
      kind: "all",
      value: null,
      slug: "all-grades",
      label: "All Grades",
    };
  }

  const numeric = Number.parseInt(String(value), 10);
  if (!Number.isInteger(numeric) || numeric <= 0) {
    throw new Error(`Invalid grade: ${value}`);
  }

  return {
    kind: "grade",
    value: numeric,
    slug: `grade-${numeric}`,
    label: `Grade ${numeric}`,
  };
}

function deepMerge(baseValue, overrideValue) {
  if (Array.isArray(baseValue) || Array.isArray(overrideValue)) {
    return overrideValue !== undefined ? overrideValue : baseValue;
  }

  if (!isPlainObject(baseValue) || !isPlainObject(overrideValue)) {
    return overrideValue !== undefined ? overrideValue : baseValue;
  }

  const merged = { ...baseValue };
  for (const [key, value] of Object.entries(overrideValue)) {
    merged[key] = deepMerge(baseValue[key], value);
  }
  return merged;
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function loadJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function createVariantMetadata(baseConfig, scope) {
  const version = baseConfig.version || "0.0.0";
  const productName = `STAAR Problem Browser ${scope.label}`;
  const identifierSuffix = scope.kind === "grade" ? `grade${scope.value}` : "allgrades";
  return {
    scope,
    grade: scope.value,
    gradeSlug: scope.slug,
    version,
    productName,
    identifier: `com.staarproblembrowser.desktop.${identifierSuffix}`,
    windowsOutputName: `${productName}_${version}_windows.msi`,
    macosOutputName: `${productName}_${version}_macOS.dmg`,
  };
}

function createVariantConfig(platform, scope) {
  const baseConfig = loadJson(baseConfigPath);
  const platformConfigPath = platformConfigPaths[platform];
  if (!platformConfigPath) {
    throw new Error(`Unsupported platform: ${platform}`);
  }

  const platformConfig = loadJson(platformConfigPath);
  const mergedConfig = deepMerge(baseConfig, platformConfig);
  const variant = createVariantMetadata(baseConfig, scope);

  mergedConfig.productName = variant.productName;
  mergedConfig.identifier = variant.identifier;
  if (Array.isArray(mergedConfig.app?.windows)) {
    mergedConfig.app.windows = mergedConfig.app.windows.map((windowConfig) => ({
      ...windowConfig,
      title: variant.productName,
    }));
  }

  mergedConfig.bundle = {
    ...(mergedConfig.bundle || {}),
    shortDescription:
      scope.kind === "grade"
        ? `Grade ${scope.value} desktop edition of the STAAR Problem Browser.`
        : "All-grades desktop edition of the STAAR Problem Browser.",
    longDescription:
      scope.kind === "grade"
        ? `Desktop packaging for the STAAR Problem Browser grade ${scope.value} edition, including the bundled grade ${scope.value} collections, question images, and printable packet workflows.`
        : "Desktop packaging for the STAAR Problem Browser all-grades edition, including the bundled released-question collections, question images, and printable packet workflows.",
  };

  fs.mkdirSync(buildConfigRoot, { recursive: true });
  const configPath = path.join(buildConfigRoot, `tauri.${variant.gradeSlug}.${platform}.json`);
  fs.writeFileSync(configPath, `${JSON.stringify(mergedConfig, null, 2)}\n`, "utf8");
  return { configPath, variant };
}

function runTauriBuild(platform, configPath, scope) {
  const tauriCliScriptPath = path.join(root, "node_modules", "@tauri-apps", "cli", "tauri.js");
  const args = [tauriCliScriptPath, "build", "--config", configPath];

  if (platform === "windows") {
    args.push("--bundles", "msi");
  } else if (platform === "macos") {
    args.push("--target", "universal-apple-darwin", "--bundles", "dmg");
  }

  const buildEnv = { ...process.env };
  if (scope.kind === "grade") {
    buildEnv.STAAR_BUILD_GRADE = String(scope.value);
  } else {
    delete buildEnv.STAAR_BUILD_GRADE;
  }

  const result = childProcess.spawnSync(process.execPath, args, {
    cwd: root,
    stdio: "inherit",
    env: buildEnv,
  });

  if (result.status !== 0) {
    if (result.error) {
      throw result.error;
    }
    const scopeLabel = scope.kind === "grade" ? `grade ${scope.value}` : "all grades";
    throw new Error(`Tauri build failed for ${scopeLabel} on ${platform}.`);
  }
}

function collectBundleFiles(startDirectory, bundleSegment, extension) {
  const matches = [];
  const queue = [startDirectory];

  while (queue.length) {
    const current = queue.pop();
    const entries = fs.readdirSync(current, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        queue.push(fullPath);
        continue;
      }

      if (
        entry.isFile() &&
        entry.name.toLowerCase().endsWith(extension) &&
        fullPath.toLowerCase().includes(`${path.sep}bundle${path.sep}${bundleSegment}${path.sep}`)
      ) {
        matches.push({
          fullPath,
          stats: fs.statSync(fullPath),
        });
      }
    }
  }

  return matches.sort((left, right) => right.stats.mtimeMs - left.stats.mtimeMs);
}

function removeStaleCabFiles() {
  const staleCabFiles = fs
    .readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isFile() && /^staar\d+\.cab$/i.test(entry.name))
    .map((entry) => path.join(root, entry.name));

  for (const cabPath of staleCabFiles) {
    fs.unlinkSync(cabPath);
  }
}

function copyInstallerToRoot(platform, variant) {
  if (!fs.existsSync(tauriTargetRoot)) {
    throw new Error(`Tauri target directory not found: ${tauriTargetRoot}`);
  }

  const bundleSegment = platform === "windows" ? "msi" : "dmg";
  const extension = platform === "windows" ? ".msi" : ".dmg";
  const outputName = platform === "windows" ? variant.windowsOutputName : variant.macosOutputName;
  const installerCandidates = collectBundleFiles(tauriTargetRoot, bundleSegment, extension);
  const latestInstaller = installerCandidates[0];

  if (!latestInstaller) {
    throw new Error(`No ${extension} bundle found under ${tauriTargetRoot}`);
  }

  const destinationPath = path.join(root, outputName);
  fs.copyFileSync(latestInstaller.fullPath, destinationPath);
  if (platform === "windows") {
    removeStaleCabFiles();
  }
  console.log(`Copied ${platform} installer to ${destinationPath}`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const platform = args.platform;

  if (!platform || !["windows", "macos"].includes(platform)) {
    throw new Error("Pass --platform windows or --platform macos.");
  }

  const scopes = parseBuildScopes(args);
  for (const scope of scopes) {
    const { configPath, variant } = createVariantConfig(platform, scope);
    console.log(`Building ${variant.productName} for ${platform} using ${configPath}`);
    runTauriBuild(platform, configPath, scope);
    copyInstallerToRoot(platform, variant);
  }
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
