# Core TIME Management — Temporal Conditionals for TypeScript Runtime

**Status:** Draft  
**Version:** v1.0.8.0+ (Post-Teletext Grid Runtime)  
**Created:** 2026-01-18  
**Owner:** Core Runtime Team

---

## Overview

Add time-based conditional execution to Core TypeScript runtime, enabling markdown scripts to execute based on time of day, timezone, delays, and scheduled future execution.

---

## Motivation

**Current State:**

- Core runtime has conditional execution (`if/else` blocks)
- No awareness of time, timezone, or scheduling
- Scripts execute immediately with no delay/scheduling capability

**User Need:**

````markdown
<!-- Show lunch menu only during lunch hours -->

```ts
if TIME >= 12 && TIME < 14
  panel "Lunch Menu" [lunch_options]
endif
```
````

<!-- Play audio based on user's timezone -->

```ts
if TIMEZONE == "AEST" && TIME >= 6
  audio "morning_greeting_au.mp3"
endif
```

<!-- Delay execution -->

```ts
set $reminder = "Take medication"
WAIT 5min
notify $reminder
```

<!-- Schedule for tomorrow -->

```ts
set $task = "Morning standup"
WAIT until tomorrow 9:00
notify $task
```

```

---

## Requirements

### Functional Requirements

1. **Time Conditionals** — Compare current time
   - `TIME >= 12` (24-hour format)
   - `TIME < 18`
   - `TIME == 9:30` (hour:minute)

2. **Timezone Conditionals** — Check user's timezone
   - `TIMEZONE == "AEST"`
   - `TIMEZONE == "PST"`
   - `TIMEZONE == "UTC"`

3. **Date Conditionals** — Check current date
   - `DATE == "2026-01-18"`
   - `DAY == "Monday"`
   - `MONTH == "January"`

4. **Delay Execution** — Wait before continuing
   - `WAIT 5min` (minutes)
   - `WAIT 2h` (hours)
   - `WAIT 30s` (seconds)

5. **Schedule for Future** — Delay until specific time
   - `WAIT until tomorrow` (next day same time)
   - `WAIT until tomorrow 9:00` (next day at 9am)
   - `WAIT until 2026-01-20 14:30` (absolute datetime)

### Non-Functional Requirements

1. **Offline-First** — All time operations work offline using device clock
2. **Timezone Aware** — Use device timezone, respect DST changes
3. **Persistent Scheduling** — Scheduled tasks survive app restarts
4. **Deterministic** — Same time always produces same result
5. **Testable** — Mock time for testing

---

## Architecture

### Core Components

```

┌─────────────────────────────────────────────────────┐
│ Core Runtime (TypeScript) │
├─────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────┐ │
│ │ TimeManager │ │
│ │ - getCurrentTime() → { hour, minute, sec } │ │
│ │ - getCurrentDate() → { year, month, day } │ │
│ │ - getTimezone() → string │ │
│ │ - parseTimeExpression(expr) → boolean │ │
│ │ - scheduleExecution(delay, callback) │ │
│ └─────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────┐ │
│ │ ConditionalExecutor (Enhanced) │ │
│ │ - Existing: if/else logic │ │
│ │ - New: TIME/TIMEZONE/DATE conditionals │ │
│ └─────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────┐ │
│ │ WaitExecutor (New) │ │
│ │ - WAIT 5min → setTimeout() │ │
│ │ - WAIT until tomorrow → calculate delay │ │
│ │ - Persistent scheduling (SQLite queue) │ │
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘

````

### Time Expression Grammar

```ebnf
time_conditional ::= "TIME" operator time_value
operator        ::= "==" | "!=" | "<" | "<=" | ">" | ">="
time_value      ::= hour | hour ":" minute
hour            ::= [0-23]
minute          ::= [0-59]

timezone_cond   ::= "TIMEZONE" "==" timezone_name
timezone_name   ::= quoted_string  # "AEST", "PST", "UTC", etc.

date_cond       ::= "DATE" operator date_value
date_value      ::= "YYYY-MM-DD"

day_cond        ::= "DAY" "==" day_name
day_name        ::= "Monday" | "Tuesday" | ... | "Sunday"

wait_stmt       ::= "WAIT" duration | "WAIT until" schedule_time
duration        ::= number time_unit
time_unit       ::= "s" | "sec" | "min" | "h" | "hour"
schedule_time   ::= "tomorrow" [time_value] | date_value time_value
````

---

## Implementation Plan

### Phase 1: Time Variables (Core Runtime)

**Location:** `/core/runtime/TimeManager.ts`

```typescript
export class TimeManager {
  getCurrentTime(): { hour: number; minute: number; second: number } {
    const now = new Date();
    return {
      hour: now.getHours(),
      minute: now.getMinutes(),
      second: now.getSeconds(),
    };
  }

  getCurrentDate(): { year: number; month: number; day: number } {
    const now = new Date();
    return {
      year: now.getFullYear(),
      month: now.getMonth() + 1, // 1-based
      day: now.getDate(),
    };
  }

  getTimezone(): string {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  }

  evaluateTimeCondition(expr: string): boolean {
    // Parse and evaluate: "TIME >= 12", "TIMEZONE == 'AEST'", etc.
  }
}
```

### Phase 2: Conditional Integration

**Location:** `/core/runtime/ConditionalExecutor.ts`

Enhance existing `if` block parsing:

```typescript
// Before (existing)
if $user.age >= 18
  panel "Adult Content"
endif

// After (with time support)
if TIME >= 12 && $user.timezone == "AEST"
  panel "Lunch Menu (Sydney)"
endif
```

### Phase 3: WAIT Command

**Location:** `/core/runtime/WaitExecutor.ts`

```typescript
export class WaitExecutor implements BlockExecutor {
  async execute(block: WaitBlock, state: StateManager): Promise<void> {
    if (block.waitType === "duration") {
      const ms = this.parseDuration(block.duration);
      await this.delay(ms);
    } else if (block.waitType === "schedule") {
      const targetTime = this.parseSchedule(block.schedule);
      const ms = targetTime.getTime() - Date.now();
      await this.delay(ms);
    }
  }

  private parseDuration(duration: string): number {
    // "5min" → 300000ms
    // "2h" → 7200000ms
  }

  private parseSchedule(schedule: string): Date {
    // "tomorrow 9:00" → Date object
    // "2026-01-20 14:30" → Date object
  }
}
```

### Phase 4: Persistent Scheduling (SQLite)

**Location:** `/core/runtime/ScheduleQueue.ts`

For `WAIT until` commands that span app restarts:

```typescript
// SQLite schema
CREATE TABLE scheduled_executions (
  id INTEGER PRIMARY KEY,
  script_path TEXT NOT NULL,
  block_id TEXT NOT NULL,
  execute_at INTEGER NOT NULL,  -- Unix timestamp
  state_snapshot TEXT,           -- JSON serialized state
  status TEXT DEFAULT 'pending'  -- pending, executed, cancelled
);

export class ScheduleQueue {
  async scheduleExecution(
    scriptPath: string,
    blockId: string,
    executeAt: Date,
    state: StateManager
  ): Promise<void> {
    // Insert into SQLite
    // Set up timer or cron to check periodically
  }

  async checkPendingExecutions(): Promise<void> {
    // Check for executions whose time has arrived
    // Resume script execution from that block
  }
}
```

---

## Usage Examples

### Example 1: Time-Based Content

````markdown
# Morning/Afternoon/Evening Greeting

```ts
state
  $greeting = ""
endstate

if TIME >= 5 && TIME < 12
  set $greeting = "Good morning! ☀️"
elsif TIME >= 12 && TIME < 18
  set $greeting = "Good afternoon! 🌤️"
else
  set $greeting = "Good evening! 🌙"
endif

panel "Greeting" [$greeting]
```
````

````

### Example 2: Timezone-Specific Content

```markdown
# Regional News

```ts
if TIMEZONE == "AEST"
  panel "Sydney News" [sydney_headlines]
elsif TIMEZONE == "PST"
  panel "LA News" [la_headlines]
else
  panel "Global News" [global_headlines]
endif
````

````

### Example 3: Delayed Execution

```markdown
# Pomodoro Timer

```ts
panel "Starting focus session..." []
WAIT 25min
notify "Break time! Take 5 minutes."
WAIT 5min
notify "Back to work!"
````

````

### Example 4: Schedule for Future

```markdown
# Daily Standup Reminder

```ts
state
  $standup_time = "tomorrow 9:00"
  $reminder = "Daily standup in 5 minutes"
endstate

WAIT until tomorrow 8:55
notify $reminder
````

````

---

## Integration Points

### Core Runtime
- `TimeManager.ts` (new)
- `ConditionalExecutor.ts` (enhance)
- `WaitExecutor.ts` (new)
- `ScheduleQueue.ts` (new)

### State Manager
- Add built-in variables: `$TIME`, `$DATE`, `$TIMEZONE`, `$DAY`
- Update on each block execution

### Parser
- Extend expression parser for time conditionals
- Add `WAIT` command to block types

### Mobile Integration
- iOS/iPadOS: Use native `Date()` + `TimeZone`
- Background execution: Local notifications for scheduled tasks

---

## Testing Strategy

### Unit Tests

```typescript
describe('TimeManager', () => {
  it('should evaluate TIME >= 12 correctly', () => {
    const tm = new TimeManager({ mockTime: '13:30' });
    expect(tm.evaluateTimeCondition('TIME >= 12')).toBe(true);
  });

  it('should evaluate TIMEZONE correctly', () => {
    const tm = new TimeManager({ mockTimezone: 'AEST' });
    expect(tm.evaluateTimeCondition('TIMEZONE == "AEST"')).toBe(true);
  });

  it('should parse WAIT 5min correctly', () => {
    const we = new WaitExecutor();
    expect(we.parseDuration('5min')).toBe(300000);
  });
});
````

### Integration Tests

```typescript
describe("Time-based script execution", () => {
  it("should show content only during specified hours", async () => {
    const script = `
      if TIME >= 12 && TIME < 14
        panel "Lunch Menu" [menu]
      endif
    `;
    const runtime = new Runtime({ mockTime: "13:00" });
    const result = await runtime.execute(script);
    expect(result.panels).toHaveLength(1);
  });

  it("should delay execution for WAIT command", async () => {
    const script = `
      panel "Starting..." []
      WAIT 1s
      panel "Done!" []
    `;
    const start = Date.now();
    const runtime = new Runtime();
    await runtime.execute(script);
    const elapsed = Date.now() - start;
    expect(elapsed).toBeGreaterThanOrEqual(1000);
  });
});
```

---

## Security & Privacy

1. **No External Time Source** — Use device clock only (offline-first)
2. **No Timezone Leaking** — Timezone is local, not transmitted
3. **Scheduled Tasks Local** — All scheduling is device-local
4. **No Background Network** — WAIT commands don't require internet

---

## Performance Considerations

1. **WAIT Implementation** — Use `setTimeout()` for short delays (<1 hour)
2. **Long Delays** — Use SQLite + periodic check for `WAIT until tomorrow`
3. **Time Checks** — Cache current time for block execution (don't call `Date.now()` per line)
4. **Timezone Detection** — Cache timezone, only refresh on app launch

---

## Future Enhancements (v1.1.0+)

1. **Recurring Schedules** — `REPEAT daily 9:00`
2. **Date Math** — `WAIT until DATE + 7 days`
3. **Time Ranges** — `DURING 9:00-17:00` (business hours)
4. **Cron Syntax** — `SCHEDULE "0 9 * * 1"` (every Monday 9am)
5. **Calendar Integration** — `if CALENDAR has_event "Meeting"`

---

## Open Questions

1. Should `WAIT` block the entire script or just pause that execution path?
2. How to handle timezone changes (e.g., user travels)?
3. Should scheduled tasks survive app reinstall? (persistent storage)
4. What happens if device clock changes (manual time set)?

---

## References

- [Core Runtime Architecture](/core/README.md)
- [ConditionalExecutor](/core/runtime/ConditionalExecutor.ts)
- [StateManager](/core/runtime/StateManager.ts)
- [AGENTS.md Section 3.1](/AGENTS.md) — Core workspace boundaries

---

_Next Steps: Implement TimeManager.ts and extend ConditionalExecutor with time expression support._
