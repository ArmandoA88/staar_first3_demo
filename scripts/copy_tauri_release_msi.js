const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const tauriTargetRoot = path.join(root, "src-tauri", "target");
const destinationMsi = path.join(root, "STAARProblemBrowser-windows Installer.msi");

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

const installerCandidates = collectBundleFiles(tauriTargetRoot, "msi", ".msi");

const latestInstaller = installerCandidates[0];

if (!latestInstaller) {
  console.error(`No Tauri MSI installer found under ${tauriTargetRoot}`);
  process.exit(1);
}

fs.copyFileSync(latestInstaller.fullPath, destinationMsi);

const staleCabFiles = fs
  .readdirSync(root, { withFileTypes: true })
  .filter((entry) => entry.isFile() && /^staar\d+\.cab$/i.test(entry.name))
  .map((entry) => path.join(root, entry.name));

for (const cabPath of staleCabFiles) {
  fs.unlinkSync(cabPath);
}

console.log(`Copied Tauri MSI installer to ${destinationMsi}`);
if (staleCabFiles.length) {
  console.log(`Removed ${staleCabFiles.length} stale CAB file(s) from ${root}`);
}
