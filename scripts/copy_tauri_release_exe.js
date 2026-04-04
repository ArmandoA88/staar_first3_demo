const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const sourceExe = path.join(root, "src-tauri", "target", "release", "staar_problem_browser.exe");
const destinationExe = path.join(root, "STAARProblemBrowser-Tauri.exe");

if (!fs.existsSync(sourceExe)) {
  console.error(`Tauri release executable not found: ${sourceExe}`);
  process.exit(1);
}

fs.copyFileSync(sourceExe, destinationExe);
console.log(`Copied Tauri executable to ${destinationExe}`);
