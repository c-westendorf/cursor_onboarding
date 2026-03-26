// Pattern: Security (UserPromptSubmit hook) | Principle: P7 | Tool: Claude Code CLI
//
// This hook runs before Claude sees each user message (UserPromptSubmit lifecycle event).
// It blocks prompts that contain credential patterns — Claude never sees the secret.
// Exit code 2 = block the prompt; exit code 0 = allow it through.
//
// Register in ~/.claude/settings.json:
//   "hooks": {
//     "UserPromptSubmit": [{ "command": "node ~/.claude/hooks/secret-scan.js" }]
//   }
//
// Claude Code CLI only — UserPromptSubmit hooks are not available in VS Code extension.

const SECRET_PATTERNS = [
  // API keys
  { pattern: /sk-[a-zA-Z0-9]{20,}/, label: 'OpenAI API key' },
  { pattern: /AKIA[0-9A-Z]{16}/, label: 'AWS access key ID' },
  { pattern: /ghp_[a-zA-Z0-9]{36}/, label: 'GitHub personal access token' },
  { pattern: /gho_[a-zA-Z0-9]{36}/, label: 'GitHub OAuth token' },
  { pattern: /xoxb-[0-9a-zA-Z-]{50,}/, label: 'Slack bot token' },
  { pattern: /AIza[0-9A-Za-z\\-_]{35}/, label: 'Google API key' },

  // Credentials in code-like patterns
  { pattern: /password\s*[:=]\s*["'][^"']{4,}["']/i, label: 'Inline password' },
  { pattern: /api_key\s*[:=]\s*["'][^"']{8,}["']/i, label: 'Inline API key' },
  { pattern: /secret\s*[:=]\s*["'][^"']{8,}["']/i, label: 'Inline secret' },

  // Private keys
  { pattern: /-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----/, label: 'Private key' },
];

let input = '';
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const event = JSON.parse(input);
    const prompt = event.prompt || '';

    for (const { pattern, label } of SECRET_PATTERNS) {
      if (pattern.test(prompt)) {
        // Print to stderr — Claude Code CLI shows this to the user
        process.stderr.write(
          `\n⚠️  Possible secret detected: ${label}\n` +
          `Remove it from your message and use a file reference or env var instead.\n\n`
        );
        process.exit(2); // Block the prompt
      }
    }
  } catch (err) {
    // Parsing failed — don't block, just warn
    process.stderr.write(`secret-scan warning: ${err.message}\n`);
  }

  // exit 0 = prompt passes, Claude sees it
  process.exit(0);
});
