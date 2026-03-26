// Pattern: Memory Persistence (SessionStart hook) | Principle: P2 | Tool: Claude Code CLI
//
// This hook runs when Claude starts a new session (SessionStart lifecycle event).
// It reads the last session state and injects a summary into Claude's context.
//
// Register in ~/.claude/settings.json:
//   "hooks": { "SessionStart": [{ "command": "node ~/.claude/hooks/session-start.js" }] }
//
// Claude Code CLI only — lifecycle events are not available in VS Code extension.

const fs = require('fs');
const path = require('path');

const SESSIONS_DIR = path.join(process.env.HOME, '.claude', 'sessions');
const LATEST_FILE = path.join(SESSIONS_DIR, 'latest.json');

function loadLatestSession() {
  if (!fs.existsSync(LATEST_FILE)) return null;
  try {
    const { file } = JSON.parse(fs.readFileSync(LATEST_FILE, 'utf8'));
    if (!fs.existsSync(file)) return null;
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return null;
  }
}

const session = loadLatestSession();

if (session) {
  // Print a context summary to stdout — Claude Code CLI injects this into context
  const age = Math.round((Date.now() - new Date(session.timestamp).getTime()) / 60000);
  const ageStr = age < 60 ? `${age}m ago` : `${Math.round(age / 60)}h ago`;

  console.log(`[Session context from ${ageStr} in ${path.basename(session.project || '.')}]`);

  if (session.summary) {
    console.log(`Last session: ${session.summary}`);
  }

  // If there's a patterns file, mention it
  const patternsFile = path.join(process.env.HOME, '.claude', 'patterns.md');
  if (fs.existsSync(patternsFile)) {
    const lines = fs.readFileSync(patternsFile, 'utf8').split('\n').filter(Boolean);
    const recent = lines.slice(-3);
    if (recent.length > 0) {
      console.log(`Recent patterns: ${recent.join(' | ')}`);
    }
  }
}

// exit 0 = Claude proceeds normally
process.exit(0);
