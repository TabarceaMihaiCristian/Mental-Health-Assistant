import console from "node:console";
import { spawnSync } from "node:child_process";
import process from "node:process";
import { cleanupPlaywrightData } from "./cleanup-playwright-data.mjs";

const npxExecutable = process.platform === "win32" ? "npx.cmd" : "npx";
const playwrightArgs = ["playwright", "test", ...process.argv.slice(2)];
const playwrightResult = spawnSync(npxExecutable, playwrightArgs, {
  cwd: process.cwd(),
  stdio: "inherit",
});

if (typeof playwrightResult.status === "number" && playwrightResult.status !== 0) {
  process.exit(playwrightResult.status);
}

if (playwrightResult.error) {
  console.error(playwrightResult.error.message);
  process.exit(1);
}

try {
  const output = cleanupPlaywrightData();
  if (output) {
    console.log(output);
  }
} catch (error) {
  console.error("Playwright tests passed, but cleanup failed.");
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
