const { spawnSync } = require("node:child_process");

const userArgs = process.argv.slice(2);
if (!userArgs.length) {
  console.error("Usage: node scripts/run_python.js <script> [args...]");
  process.exit(1);
}

const candidates =
  process.platform === "win32"
    ? [
        { command: "python", prefixArgs: [] },
        { command: "py", prefixArgs: ["-3"] },
      ]
    : [
        { command: "python3", prefixArgs: [] },
        { command: "python", prefixArgs: [] },
      ];

for (const candidate of candidates) {
  const result = spawnSync(candidate.command, [...candidate.prefixArgs, ...userArgs], {
    stdio: "inherit",
    shell: false,
  });

  if (result.error && result.error.code === "ENOENT") {
    continue;
  }

  if (result.error) {
    console.error(result.error.message);
    process.exit(1);
  }

  process.exit(result.status ?? 0);
}

console.error("Unable to find a Python interpreter. Install Python 3 or adjust scripts/run_python.js.");
process.exit(1);
