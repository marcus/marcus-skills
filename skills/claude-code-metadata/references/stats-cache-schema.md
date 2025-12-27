# Stats Cache Complete Schema Reference

Location: `~/.claude/stats-cache.json`

## Full Schema

```typescript
interface StatsCache {
  version: 1;
  lastComputedDate: string;  // "YYYY-MM-DD"

  // Aggregate counts
  totalSessions: number;
  totalMessages: number;
  firstSessionDate: string;  // ISO 8601

  // Daily activity breakdown
  dailyActivity: DailyActivity[];

  // Token usage by model per day
  dailyModelTokens: DailyModelTokens[];

  // Cumulative model usage
  modelUsage: Record<string, ModelUsage>;

  // Session activity by hour (0-23)
  hourCounts: Record<string, number>;

  // Longest session metadata
  longestSession: {
    sessionId: string;
    duration: number;      // milliseconds
    messageCount: number;
    timestamp: string;     // ISO 8601
  };
}

interface DailyActivity {
  date: string;           // "YYYY-MM-DD"
  messageCount: number;
  sessionCount: number;
  toolCallCount: number;
}

interface DailyModelTokens {
  date: string;           // "YYYY-MM-DD"
  tokensByModel: Record<string, number>;
}

interface ModelUsage {
  inputTokens: number;
  outputTokens: number;
  cacheReadInputTokens: number;
  cacheCreationInputTokens: number;
  webSearchRequests: number;
  costUSD: number;        // Usually 0 (not calculated)
  contextWindow: number;  // Usually 0
}
```

## Model Identifiers

Common model IDs found in `tokensByModel` and `modelUsage`:

| Model ID | Display Name |
|----------|--------------|
| `claude-opus-4-5-20251101` | Claude Opus 4.5 |
| `claude-sonnet-4-5-20250929` | Claude Sonnet 4.5 |
| `claude-haiku-4-5-20251001` | Claude Haiku 4.5 |

## Calculating Metrics

### Total Tokens for a Day
```javascript
const dayData = dailyActivity.find(d => d.date === "2025-12-24");
const tokenData = dailyModelTokens.find(d => d.date === "2025-12-24");
const totalTokens = Object.values(tokenData.tokensByModel).reduce((a, b) => a + b, 0);
```

### Cache Efficiency
```javascript
const model = modelUsage["claude-opus-4-5-20251101"];
const efficiency = model.cacheReadInputTokens /
  (model.cacheReadInputTokens + model.inputTokens + model.cacheCreationInputTokens);
```

### Peak Usage Hours
```javascript
const peakHour = Object.entries(hourCounts)
  .sort((a, b) => b[1] - a[1])[0];
// Returns ["18", 94] for 6 PM with 94 sessions
```

### Average Messages per Session
```javascript
const avgMessages = totalMessages / totalSessions;
```

## Notes

- `costUSD` is typically 0; Claude Code doesn't calculate costs locally
- `contextWindow` is typically 0; not tracked in this cache
- `hourCounts` keys are strings of hour numbers (0-23)
- `lastComputedDate` indicates freshness of cached data
- This cache is regenerated periodically, not on every session
