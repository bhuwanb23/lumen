import { spawn } from "node:child_process";
import { cp, mkdir, rm } from "node:fs/promises";
import { dirname, join } from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const projectRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const standaloneRoot = join(projectRoot, ".next", "standalone");
const standaloneNext = join(standaloneRoot, ".next");
const builtStatic = join(projectRoot, ".next", "static");
const standaloneStatic = join(standaloneNext, "static");

await mkdir(standaloneNext, { recursive: true });
await rm(standaloneStatic, { recursive: true, force: true });
await cp(builtStatic, standaloneStatic, { recursive: true });

const publicAssets = join(projectRoot, "public");
try {
  await cp(publicAssets, join(standaloneRoot, "public"), { recursive: true });
} catch (error) {
  if (!(error instanceof Error && "code" in error && error.code === "ENOENT")) throw error;
}

const server = spawn(process.execPath, ["server.js"], {
  cwd: standaloneRoot,
  env: process.env,
  stdio: "inherit",
});

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => server.kill(signal));
}
server.on("exit", (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  else process.exitCode = code ?? 1;
});
