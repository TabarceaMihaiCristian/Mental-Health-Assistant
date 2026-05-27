import console from "node:console";
import { spawnSync } from "node:child_process";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const frontendRoot = path.resolve(scriptDir, "..");
const repoRoot = path.resolve(frontendRoot, "..");
const backendRoot = path.join(repoRoot, "backend");

function formatFailure(command, result) {
  return (
    result.stderr?.trim()
    || result.stdout?.trim()
    || result.error?.message
    || `Command failed: ${command.join(" ")}`
  );
}

function run(command, options) {
  return spawnSync(command[0], command.slice(1), {
    cwd: options.cwd,
    encoding: "utf-8",
    stdio: options.stdio ?? "pipe",
  });
}

export function cleanupPlaywrightData() {
  const dockerCommand = ["docker", "compose", "exec", "-T", "backend", "python", "-m", "app.scripts.cleanup_playwright_data"];
  const dockerResult = run(dockerCommand, { cwd: repoRoot });
  if (dockerResult.status === 0) {
    return dockerResult.stdout?.trim() ?? "";
  }

  const windowsPython = path.join(backendRoot, ".venv", "Scripts", "python.exe");
  const unixPython = path.join(backendRoot, ".venv", "bin", "python");
  const configuredPython = process.env.PW_BACKEND_PYTHON?.trim();
  const defaultPython = process.platform === "win32" ? windowsPython : unixPython;
  const localCommand = [configuredPython || defaultPython, "-m", "app.scripts.cleanup_playwright_data"];
  const localResult = run(localCommand, { cwd: backendRoot });
  if (localResult.status === 0) {
    return localResult.stdout?.trim() ?? "";
  }

  const fallbackPython = process.platform === "win32" ? "python" : "python3";
  const fallbackCommand = [fallbackPython, "-m", "app.scripts.cleanup_playwright_data"];
  const fallbackResult = run(fallbackCommand, { cwd: backendRoot });
  if (fallbackResult.status === 0) {
    return fallbackResult.stdout?.trim() ?? "";
  }

  throw new Error(
    [
      `Docker cleanup failed: ${formatFailure(dockerCommand, dockerResult)}`,
      `Local cleanup failed: ${formatFailure(localCommand, localResult)}`,
      `Fallback cleanup failed: ${formatFailure(fallbackCommand, fallbackResult)}`,
    ].join("\n"),
  );
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const output = cleanupPlaywrightData();
    if (output) {
      console.log(output);
    }
  } catch (error) {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  }
}
