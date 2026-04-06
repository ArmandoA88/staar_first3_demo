const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const tauriTargetRoot = path.join(root, "src-tauri", "target");
const tauriConfigPath = path.join(root, "src-tauri", "tauri.conf.json");

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

if (!fs.existsSync(tauriTargetRoot)) {
  console.error(`Tauri target directory not found: ${tauriTargetRoot}`);
  process.exit(1);
}

const tauriConfig = JSON.parse(fs.readFileSync(tauriConfigPath, "utf8"));
const productName = tauriConfig.productName || "STAAR Problem Browser";
const version = tauriConfig.version || "0.0.0";
const destinationDmg = path.join(root, `${productName}_${version}_macOS.dmg`);

const installerCandidates = collectBundleFiles(tauriTargetRoot, "dmg", ".dmg");
const latestInstaller = installerCandidates[0];

if (!latestInstaller) {
  console.error(`No Tauri DMG installer found under ${tauriTargetRoot}`);
  process.exit(1);
}

fs.copyFileSync(latestInstaller.fullPath, destinationDmg);
console.log(`Copied Tauri DMG installer to ${destinationDmg}`);
