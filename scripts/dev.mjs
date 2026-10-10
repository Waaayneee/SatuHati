// Starts KawTeam in one window: the backend (FastAPI, port 8000) and the frontend (Next.js, port 3000).
// Run `npm run dev` in the project folder or in frontend/ (or double-click start.cmd). Ctrl+C stops both.

import { spawn, spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import net from "node:net";
import path from "node:path";
import readline from "node:readline";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const backendDir = path.join(root, "backend");
const frontendDir = path.join(root, "frontend");
const isWindows = process.platform === "win32";
const python = path.join(backendDir, ".venv", isWindows ? "Scripts" : "bin", isWindows ? "python.exe" : "python");
const nextBin = path.join(frontendDir, "node_modules", "next", "dist", "bin", "next");
const API_PORT = 8000;
const WEB_PORT = 3000;

const RESET = "\x1b[0m";
const COLORS = { api: "\x1b[36m", web: "\x1b[32m", kawteam: "\x1b[33m", error: "\x1b[31m" };

function say(text, tag = "kawteam") {
  console.log(`${COLORS[tag]}[${tag}]${RESET} ${text}`);
}

function fail(text) {
  say(text, "error");
  process.exit(1);
}

/** True when something already accepts connections on the port (IPv4 or IPv6 loopback). */
function portBusy(port) {
  const probe = (host) =>
    new Promise((resolve) => {
      const socket = net.connect({ port, host });
      socket.setTimeout(800);
      socket.once("connect", () => {
        socket.destroy();
        resolve(true);
      });
      socket.once("timeout", () => {
        socket.destroy();
        resolve(false);
      });
      socket.once("error", () => resolve(false));
    });
  return Promise.all([probe("127.0.0.1"), probe("::1")]).then(([v4, v6]) => v4 || v6);
}

const children = [];
let stopping = false;

function killTree(child) {
  if (child.exitCode !== null || child.signalCode !== null) return;
  if (isWindows) {
    // uvicorn --reload and next dev both start worker processes; /T takes the whole tree down.
    spawnSync("taskkill", ["/pid", String(child.pid), "/T", "/F"], { stdio: "ignore" });
  } else {
    try {
      process.kill(-child.pid, "SIGTERM");
    } catch {
      child.kill("SIGTERM");
    }
  }
}

function stopAll(code) {
  if (stopping) return;
  stopping = true;
  children.forEach(killTree);
  process.exit(code);
}

function start(tag, command, args, cwd, env = {}) {
  const child = spawn(command, args, {
    cwd,
    env: { ...process.env, ...env },
    stdio: ["ignore", "pipe", "pipe"],
    detached: !isWindows,
    windowsHide: true,
  });
  for (const stream of [child.stdout, child.stderr]) {
    readline.createInterface({ input: stream }).on("line", (line) => say(line, tag));
  }
  child.on("error", (error) => {
    say(`could not start: ${error.message}`, "error");
    stopAll(1);
  });
  child.on("exit", (code) => {
    if (stopping) return;
    say(`${tag === "api" ? "Backend" : "Frontend"} stopped (exit code ${code}). Stopping KawTeam.`, "error");
    stopAll(code || 1);
  });
  children.push(child);
  return child;
}

async function reportDatabase() {
  // /health tries the database itself, so this waits for the backend and then tells the truth about it.
  for (let i = 0; i < 60 && !stopping; i++) {
    try {
      const health = await (await fetch(`http://127.0.0.1:${API_PORT}/health`)).json();
      if (health.database === "ok") {
        say("Database connected.");
      } else {
        say("Can't reach the database. This network blocks port 5432.", "error");
        say("The app opens but shows that message until you switch to a phone hotspot and press Try again.", "error");
      }
      return;
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
  }
}

if (!existsSync(python)) {
  fail("backend/.venv is missing. Run once: cd backend; py -3.12 -m venv .venv; .\\.venv\\Scripts\\pip install -r requirements.txt");
}
if (!existsSync(path.join(backendDir, ".env"))) fail("backend/.env is missing. Copy backend/.env.example and fill it in.");
if (!existsSync(nextBin)) fail("Frontend packages are missing. Run once: cd frontend; npm install");

for (const [port, what] of [
  [API_PORT, "backend"],
  [WEB_PORT, "frontend"],
]) {
  if (await portBusy(port)) {
    fail(`Port ${port} is already in use, probably by a ${what} you started earlier. Close that window (or press Ctrl+C in it) and run this again.`);
  }
}

process.on("SIGINT", () => stopAll(0));
process.on("SIGTERM", () => stopAll(0));
process.on("exit", () => children.forEach(killTree));

say("Starting KawTeam. Ctrl+C stops everything.");
start("api", python, ["-m", "uvicorn", "app.main:app", "--reload", "--port", String(API_PORT)], backendDir, {
  PYTHONUNBUFFERED: "1",
});

// The frontend starts only once the backend accepts connections, so the page never loads
// before the API exists (that is what shows up as "Failed to fetch").
let backendUp = false;
for (let i = 0; i < 120 && !stopping; i++) {
  if (await portBusy(API_PORT)) {
    backendUp = true;
    break;
  }
  await new Promise((resolve) => setTimeout(resolve, 500));
}
if (!backendUp) {
  if (!stopping) {
    say(`The backend did not start on port ${API_PORT} within 60 seconds. See the [api] lines above.`, "error");
    stopAll(1);
  }
} else {
  start("web", process.execPath, [nextBin, "dev", "--port", String(WEB_PORT)], frontendDir);
  say(`Open http://localhost:${WEB_PORT} once [web] says Ready.`);
  reportDatabase();
}
