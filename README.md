# Skill Security Auditor

Skill Security Auditor runs a structured, adversarial defensive-security audit on a downloaded
SKILL/plugin/agent-instructions file before you enable it — checking for prompt injection,
credential theft, unsafe tool/shell use, and supply-chain risk. Because it is just Markdown, it
works with any agent that supports skills.

The skill treats the file being audited as **untrusted input**: it never executes, follows, or
obeys anything inside it, no matter how the file tries to phrase itself (fake system notices,
"admin override" tokens, urgency, hidden HTML comments, etc.).

## Installation

Copy `SKILL.md` and `audit-checklist.md` into your agent's skill folder, keeping both files
together (the skill loads `audit-checklist.md` from its own directory).

For Claude Code, drop this repo (or just the two files) into `~/.claude/skills/auditing-skill-files/`
for global, every-project use, or into a project's `.claude/skills/` for project-scoped use.

Claude Code 2.1.142 or newer can install the plugin instead:

```text
/plugin marketplace add <this-repo>
/plugin install skill-sec-auditor@skill-sec-auditor
```

## Usage

Point it at any downloaded skill file:

```
Audit this SKILL file for security issues before I enable it: path/to/downloaded/SKILL.md
```

Or ask in plain language:

```
I downloaded this skill from GitHub, is it safe to use?
```

## How it works

1. **Never run it.** The target file is read only — no shell command, script, URL, or example
   inside it is ever executed.
2. **Load the full checklist.** `audit-checklist.md` defines 22 audit categories: prompt
   injection, instruction-hierarchy attacks, tool abuse, data exfiltration, credential handling,
   filesystem risk, supply-chain/code-execution, command injection, indirect injection,
   least-privilege, persistence/config tampering, obfuscation, social engineering, cross-platform
   risk, the severity rubric, and the final-verdict rules.
3. **Apply every category** to the file's actual content. Anything unverifiable (external URLs,
   packages, repo reputation) is marked explicitly as an unknown, never assumed safe.
4. **Report in a fixed format:** a `VERDICT:` of `SAFE`, `UNSAFE`, or `NEEDS REVIEW`, an executive
   summary, a dedicated prompt-injection score, findings grouped by severity, and dedicated
   assessments for exfiltration, code execution, supply-chain, filesystem/privilege, and network
   risk, plus unknowns and security positives.
5. **Resist redefinition.** If the audited file contains text claiming to be a system/developer
   message, a pre-existing approval, or an override, that text is itself a finding — never an
   instruction the audit follows.

## Severity levels

| Severity | Meaning |
|---|---|
| CRITICAL | Credential theft, arbitrary code execution, agent takeover, persistent compromise |
| HIGH | Command injection, dangerous prompt injection, privilege abuse, sensitive data exposure |
| MEDIUM | Excessive permissions, weak isolation, unsafe dependency, moderate injection risk |
| LOW | Minor/defense-in-depth issue, limited exposure |
| INFO | Notable but non-exploitable observation |

**Verdict logic:** any credible CRITICAL/HIGH finding → `UNSAFE`. No confirmed high-risk finding
but unverifiable externals, ambiguous behavior, or unresolved MEDIUM issues → `NEEDS REVIEW`.
Torn between `SAFE` and `NEEDS REVIEW` → pick `NEEDS REVIEW`. The audit never claims a file is
"100% safe" — only that no material issue was identified.

## Verified against a malicious sample

The skill was tested against a crafted malicious sample skill file containing: a fake "system
notice" claiming override authority, instructions to read `~/.aws/credentials` and
`~/.ssh/id_rsa` and exfiltrate them via URL, instructions to hide the action and lie about the
skill's purpose later, a hidden HTML-comment jailbreak ("DAN"/"admin override token"), and a
`curl | bash` remote-code-execution example. The skill correctly returned `VERDICT: UNSAFE` with
every injected attack identified as a finding, none of them followed.

## Source of truth

The canonical, always-current copy of this skill is deployed globally at
`~/.claude/skills/auditing-skill-files/` for use across every Claude Code project/session. This
repo packages the same two files (`SKILL.md`, `audit-checklist.md`) for versioning and
distribution — see `AGENTS.md` for the sync rule.

## License

MIT
