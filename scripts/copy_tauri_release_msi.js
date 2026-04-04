const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const msiDirectory = path.join(root, "src-tauri", "target", "release", "bundle", "msi");
const destinationMsi = path.join(root, "STAARProblemBrowser-Tauri-Installer.msi");

if (!fs.existsSync(msiDirectory)) {
  console.error(`Tauri MSI bundle directory not found: ${msiDirectory}`);
  process.exit(1);
}

const installerCandidates = fs
  .readdirSync(msiDirectory)
  .filter((fileName) => fileName.toLowerCase().endsWith(".msi"))
  .map((fileName) => {
    const fullPath = path.join(msiDirectory, fileName);
    return {
      fullPath,
      stats: fs.statSync(fullPath),
    };
  })
  .sort((left, right) => right.stats.mtimeMs - left.stats.mtimeMs);

const latestInstaller = installerCandidates[0];

if (!latestInstaller) {
  console.error(`No Tauri MSI installer found in ${msiDirectory}`);
  process.exit(1);
}

fs.copyFileSync(latestInstaller.fullPath, destinationMsi);
console.log(`Copied Tauri MSI installer to ${destinationMsi}`);
