// Pattern: Memory Persistence (Stop hook) | Principle: P2 | Tool: Claude Code CLI
//
// This hook runs when Claude finishes a session (Stop lifecycle event).
// It saves session state to ~/.claude/sessions/ so it can be loaded next time.
//
// Register in ~/.claude/settings.json:
//   "hooks": { "Stop": [{ "command": "node ~/.claude/hooks/session-end.js" }] }
//
// Claude Code CLI only — lifecycle events are not available in VS Code extension.

const fs = require('fs');
const path = require('path');

const SESSIONS_DIR = path.join(process.env.HOME, '.claude', 'sessions');

let input = '';
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const session = JSON.parse(input);
    const sessionId = `session-${Date.now()}`;

    fs.mkdirSync(SESSIONS_DIR, { recursive: true });

    // Save the full session transcript
    const sessionFile = path.join(SESSIONS_DIR, `${sessionId}.json`);
    fs.writeFileSync(sessionFile, JSON.stringify({
      id: sessionId,
      timestamp: new Date().toISOString(),
      project: process.cwd(),
      ...session
    }, null, 2));

    // Update the "latest" pointer so session-start.js can find it quickly
    const latestFile = path.join(SESSIONS_DIR, 'latest.json');
    fs.writeFileSync(latestFile, JSON.stringify({ sessionId, file: sessionFile }, null, 2));

    // Optional: append a one-line summary to the patterns journal
    const patternsFile = path.join(process.env.HOME, '.claude', 'patterns.md');
    const dateStr = new Date().toISOString().slice(0, 10);
    const summary = `- ${dateStr}: Session in ${path.basename(process.cwd())} — review ${sessionId}.json for patterns\n`;
    fs.appendFileSync(patternsFile, summary);

  } catch (err) {
    // Non-zero exit would show an error — soft fail is better for a persistence hook
    process.stderr.write(`session-end hook warning: ${err.message}\n`);
  }
  // exit 0 = Claude proceeds normally (session is already ending)
  process.exit(0);
});
