// Pattern: Memory Persistence (PreCompact hook) | Principle: P2 | Tool: Claude Code CLI
//
// This hook runs just before Claude compacts its context (PreCompact lifecycle event).
// It saves a snapshot of the current context so valuable information isn't lost.
//
// Register in ~/.claude/settings.json:
//   "hooks": { "PreCompact": [{ "command": "node ~/.claude/hooks/pre-compact.js" }] }
//
// Claude Code CLI only — lifecycle events are not available in VS Code extension.

const fs = require('fs');
const path = require('path');

const SESSIONS_DIR = path.join(process.env.HOME, '.claude', 'sessions');

let input = '';
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const context = JSON.parse(input);
    fs.mkdirSync(SESSIONS_DIR, { recursive: true });

    // Save a pre-compaction snapshot — useful for debugging context loss
    const snapshotFile = path.join(SESSIONS_DIR, `pre-compact-${Date.now()}.json`);
    fs.writeFileSync(snapshotFile, JSON.stringify({
      timestamp: new Date().toISOString(),
      project: process.cwd(),
      tokenCount: context.token_count,
      snapshot: context
    }, null, 2));

    // Keep only the 5 most recent snapshots to avoid disk bloat
    const snapshots = fs.readdirSync(SESSIONS_DIR)
      .filter(f => f.startsWith('pre-compact-'))
      .sort()
      .reverse();

    snapshots.slice(5).forEach(f => {
      fs.unlinkSync(path.join(SESSIONS_DIR, f));
    });

  } catch (err) {
    process.stderr.write(`pre-compact hook warning: ${err.message}\n`);
  }

  // exit 0 = Claude proceeds with compaction normally
  process.exit(0);
});
