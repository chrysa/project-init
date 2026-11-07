#!/usr/bin/env node
"use strict";

// PostToolUse hook: after Claude edits a .py file, auto-run `ruff check --fix`
// and `ruff format` on that file so lint issues are caught immediately instead
// of at CI. Read-only fast-fail: never blocks the tool result, only surfaces
// stderr as additionalContext if something is off.

const { execFileSync } = require("node:child_process");
const path = require("node:path");

function readStdin() {
  const chunks = [];
  try {
    const fd = 0;
    const buf = Buffer.alloc(65536);
    let bytes;
    // eslint-disable-next-line no-cond-assign
    while ((bytes = require("node:fs").readSync(fd, buf, 0, buf.length)) > 0) {
      chunks.push(Buffer.from(buf.subarray(0, bytes)));
    }
  } catch {
    // stdin closed/empty
  }
  return Buffer.concat(chunks).toString("utf8");
}

function main() {
  let input;
  try {
    input = JSON.parse(readStdin() || "{}");
  } catch {
    return;
  }

  const toolInput = input.tool_input || {};
  const filePath = toolInput.file_path || toolInput.path;
  if (!filePath || !filePath.endsWith(".py")) {
    return;
  }
  if (filePath.includes(`${path.sep}.claude${path.sep}`)) {
    return;
  }

  try {
    execFileSync("ruff", ["check", "--fix", filePath], { stdio: "ignore" });
    execFileSync("ruff", ["format", filePath], { stdio: "ignore" });
  } catch {
    // ruff not installed or lint failure left in place — CI still catches it
  }
}

main();
