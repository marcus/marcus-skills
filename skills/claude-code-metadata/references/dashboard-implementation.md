# Dashboard Implementation Guide

Guidance for building a Claude Code usage dashboard.

## Data Sources

### Quick Stats (stats-cache.json)
Best for: Overview metrics, charts, trends
- Pre-aggregated daily/hourly data
- No parsing overhead
- Updated periodically

### Session Files (projects/*/*.jsonl)
Best for: Deep analysis, session details
- Full conversation history
- Per-message token usage
- Tool call details

### History Index (history.jsonl)
Best for: Session list, search, recent activity
- Session metadata only
- Lightweight parsing
- Timestamp + preview

## Dashboard Widgets

### 1. Usage Overview

Source: `stats-cache.json`

```
Total Sessions: 766
Total Messages: 58,731
Active Since: Nov 12, 2025
```

### 2. Token Consumption Chart

Source: `dailyModelTokens` array

```
Data: tokensByModel per day
Chart: Stacked bar or area chart
Models: color-coded by model name
```

### 3. Model Distribution Pie

Source: `modelUsage` object

Calculate total output tokens per model:
```javascript
const modelTotals = Object.entries(modelUsage).map(([model, usage]) => ({
  model,
  tokens: usage.inputTokens + usage.outputTokens
}));
```

### 4. Activity Heatmap

Source: `hourCounts` object

```
X-axis: Hours (0-23)
Y-axis: Days of week (from dailyActivity dates)
Color: Session count intensity
```

### 5. Recent Sessions List

Source: `history.jsonl`

```javascript
// Parse last N lines
const sessions = parseJsonl(historyFile)
  .slice(-20)
  .reverse()
  .map(s => ({
    preview: s.display.slice(0, 100),
    project: path.basename(s.project),
    time: formatRelative(s.timestamp)
  }));
```

### 6. Session Deep Dive

Source: Session JSONL file

```javascript
// Parse specific session
const messages = parseJsonl(sessionFile);
const stats = {
  messageCount: messages.filter(m => m.type === 'assistant').length,
  totalInputTokens: sumField(messages, 'message.usage.input_tokens'),
  totalOutputTokens: sumField(messages, 'message.usage.output_tokens'),
  toolCalls: messages.filter(m => hasToolUse(m)).length,
  duration: new Date(messages.at(-1).timestamp) - new Date(messages[0].timestamp)
};
```

### 7. Cost Estimator

Calculate from token usage:
```javascript
const PRICING = {
  'claude-opus-4-5-20251101': { input: 5.00, output: 25.00 },
  'claude-sonnet-4-5-20250929': { input: 3.00, output: 15.00 },
  'claude-haiku-4-5-20251001': { input: 0.25, output: 1.25 },
};

function estimateCost(modelUsage) {
  let total = 0;
  for (const [model, usage] of Object.entries(modelUsage)) {
    const rates = PRICING[model];
    if (!rates) continue;

    // Regular tokens at full price
    const inputCost = (usage.inputTokens / 1_000_000) * rates.input;

    // Cache reads at 10% (90% discount)
    const cacheCost = (usage.cacheReadInputTokens / 1_000_000) * rates.input * 0.1;

    // Cache creation at full price
    const cacheCreateCost = (usage.cacheCreationInputTokens / 1_000_000) * rates.input;

    // Output at full price
    const outputCost = (usage.outputTokens / 1_000_000) * rates.output;

    total += inputCost + cacheCost + cacheCreateCost + outputCost;
  }
  return total;
}
```

### 8. Project Breakdown

Source: Directory listing of `projects/`

```javascript
const projects = fs.readdirSync(projectsDir)
  .filter(d => d.startsWith('-'))
  .map(d => ({
    name: d.replace(/-/g, '/').slice(1),
    sessionCount: fs.readdirSync(path.join(projectsDir, d))
      .filter(f => f.endsWith('.jsonl') && !f.startsWith('agent-'))
      .length
  }));
```

## Performance Tips

### Large File Handling

Session files can be 100+ MB. Use streaming:

```javascript
import { createReadStream } from 'fs';
import * as readline from 'readline';

async function* parseJsonlStream(filePath) {
  const rl = readline.createInterface({
    input: createReadStream(filePath),
    crlfDelay: Infinity
  });

  for await (const line of rl) {
    if (line.trim()) {
      yield JSON.parse(line);
    }
  }
}
```

### Caching Strategy

1. Cache `stats-cache.json` parsing
2. Index sessions by project for faster lookup
3. Store parsed session summaries (don't re-parse full files)
4. Use file modification time to invalidate cache

### Watch for Changes

```javascript
import { watch } from 'fs';

watch(claudeDir, { recursive: true }, (event, filename) => {
  if (filename.endsWith('.jsonl') || filename === 'stats-cache.json') {
    refreshDashboard();
  }
});
```

## Real-time Monitoring

For live session monitoring, watch the active session file:

```javascript
// Find most recent session
const latestSession = fs.readdirSync(projectDir)
  .filter(f => f.endsWith('.jsonl'))
  .map(f => ({ name: f, mtime: fs.statSync(path.join(projectDir, f)).mtime }))
  .sort((a, b) => b.mtime - a.mtime)[0];

// Tail the file
const tail = spawn('tail', ['-f', path.join(projectDir, latestSession.name)]);
tail.stdout.on('data', chunk => {
  const lines = chunk.toString().split('\n').filter(Boolean);
  lines.forEach(line => {
    const msg = JSON.parse(line);
    updateLiveView(msg);
  });
});
```

## Third-Party Integration

### ccusage

```bash
# Install
npm install -g ccusage

# Monthly report
ccusage monthly

# Live monitoring
ccusage live

# Session details
ccusage sessions --limit 10
```

### Claude Code Usage Monitor

```bash
pip install claude-monitor
claude-monitor
```
