# Flowchart Guide (v1.2.15)

Complete reference for flowchart.js diagrams in uDOS.

---

## Overview

Flowcharts visualize decision logic and process flows using flowchart.js syntax. Native Markdown format ideal for documenting algorithms, decision trees, and survival procedures.

### Key Features

- **Native Markdown**: Pure text format (no API required)
- **Decision Logic**: Conditional branching
- **Process Flows**: Step-by-step procedures
- **SVG Output**: Rendered via Node.js service
- **Size Limit**: 5KB source text, ~50KB SVG output

---

## Basic Syntax

### Node Definition

Format: `nodeid=>nodetype: label text`

**Node Types**:
- `start` - Start/end oval
- `end` - End oval
- `operation` - Process rectangle
- `inputoutput` - I/O parallelogram
- `subroutine` - Subroutine double-sided rectangle
- `condition` - Decision diamond
- `parallel` - Parallel process

**Examples**:
```
st=>start: Start
op1=>operation: Process data
cond=>condition: Is valid?
e=>end: End
```

### Connections

Format: `nodeid->nodeid` or `nodeid(path)->nodeid`

**Simple Connection**:
```
st->op1->e
```

**Conditional** (yes/no paths):
```
cond(yes)->op1
cond(no)->e
```

**Labeled Paths**:
```
cond(yes, right)->op1
cond(no, left)->e
```

---

## Available Templates

### 1. Simple Decision (`simple_decision.flow`)

**Use Case**: Basic yes/no decisions

**Example**:
```
st=>start: Start
check=>condition: Check condition?
action=>operation: Take action
skip=>operation: Skip action
e=>end: End

st->check
check(yes)->action->e
check(no)->skip->e
```

**Use Cases**:
- Safety checks
- Resource availability
- Environment assessment

### 2. Login Process (`login_process.flow`)

**Use Case**: User authentication flow

**Example**:
```
st=>start: User arrives
input=>inputoutput: Enter credentials
validate=>condition: Valid?
auth=>operation: Create session
error=>operation: Show error
success=>end: Logged in
retry=>condition: Retry?

st->input->validate
validate(yes)->auth->success
validate(no)->error->retry
retry(yes)->input
retry(no)->st
```

**Patterns**:
- Retry logic
- Error handling
- Session management

### 3. Data Pipeline (`data_pipeline.flow`)

**Use Case**: Data processing workflows

**Example**:
```
st=>start: Receive data
validate=>condition: Valid format?
clean=>operation: Clean data
transform=>operation: Transform
load=>operation: Load to database
error=>operation: Log error
notify=>operation: Send notification
e=>end: Complete

st->validate
validate(yes)->clean->transform->load->notify->e
validate(no)->error->notify->e
```

**Use Cases**:
- ETL processes
- Data validation
- Import workflows

### 4. Error Recovery (`error_recovery.flow`)

**Use Case**: Failure handling and recovery

**Example**:
```
st=>start: Start operation
op=>operation: Execute
check=>condition: Success?
retry=>condition: Retry count < 3?
increment=>operation: Increment counter
fallback=>operation: Use fallback
log=>operation: Log error
success=>end: Success
fail=>end: Failed

st->op->check
check(yes)->success
check(no)->retry
retry(yes)->increment->op
retry(no)->fallback->log->fail
```

**Patterns**:
- Retry with backoff
- Circuit breakers
- Fallback strategies

### 5. Business Logic (`business_logic.flow`)

**Use Case**: Complex decision workflows

**Example**:
```
st=>start: New order
inventory=>condition: Stock available?
payment=>condition: Payment valid?
reserve=>operation: Reserve items
process=>operation: Process payment
ship=>operation: Ship order
backorder=>operation: Create backorder
refund=>operation: Refund payment
notify=>operation: Notify customer
complete=>end: Complete
cancel=>end: Canceled

st->inventory
inventory(yes)->payment
inventory(no)->backorder->notify->complete
payment(yes)->reserve->process->ship->notify->complete
payment(no)->refund->notify->cancel
```

**Use Cases**:
- Order processing
- Approval workflows
- Multi-step validation

---

## Command Usage

### Generate Flowchart

```bash
# From template
MAKE --format flow --template simple_decision --source "Safety check"

# Custom flowchart
MAKE --format flow --source "
st=>start: Start
op=>operation: Process
e=>end: End
st->op->e
"

# From file
MAKE --format flow --source "$(cat process.flow)"
```

### Output

```bash
--output memory/drafts/svg/decision_flow.svg
```

---

## Best Practices

### 1. Clear Node Labels

✅ **Good** (actionable):
```
check=>condition: Temperature > 60°F?
boil=>operation: Boil water for 1 minute
filter=>operation: Use cloth filter
```

❌ **Vague**:
```
check=>condition: OK?
do1=>operation: Do stuff
do2=>operation: Other thing
```

### 2. Consistent Flow Direction

✅ **Good** (top-to-bottom or left-to-right):
```
st->check->process->end
```

❌ **Confusing** (mixed directions):
```
st->check
check->up
up->left
left->right->end
```

### 3. Limit Complexity

Keep to 10-15 nodes maximum:

✅ **Good**: Start → 3-4 decisions → 5-6 operations → End
❌ **Too Complex**: 30+ nodes with tangled connections

**Solution**: Split into sub-processes using `subroutine` nodes

### 4. Descriptive Conditions

✅ **Good**:
```
temp=>condition: Water temperature ≥ 212°F?
time=>condition: Boiled for ≥ 1 minute?
```

❌ **Unclear**:
```
c1=>condition: Check 1?
c2=>condition: Check 2?
```

### 5. Use Subroutines

Break complex flows into sub-processes:
```
st=>start: Start
prep=>subroutine: Prepare materials
build=>subroutine: Build structure
test=>subroutine: Test stability
e=>end: Complete

st->prep->build->test->e
```

---

## Common Patterns

### Simple Linear

```
st=>start: Start
op1=>operation: Step 1
op2=>operation: Step 2
op3=>operation: Step 3
e=>end: End

st->op1->op2->op3->e
```

### Binary Decision

```
st=>start: Start
check=>condition: Condition?
yes_path=>operation: Yes action
no_path=>operation: No action
e=>end: End

st->check
check(yes)->yes_path->e
check(no)->no_path->e
```

### Multiple Conditions

```
st=>start: Start
c1=>condition: Check 1?
c2=>condition: Check 2?
a1=>operation: Action 1
a2=>operation: Action 2
a3=>operation: Action 3
e=>end: End

st->c1
c1(yes)->c2
c1(no)->a3->e
c2(yes)->a1->e
c2(no)->a2->e
```

### Loop

```
st=>start: Start
op=>operation: Process item
check=>condition: More items?
e=>end: End

st->op->check
check(yes)->op
check(no)->e
```

### Error Handling

```
st=>start: Start
op=>operation: Try operation
check=>condition: Success?
retry=>condition: Can retry?
success=>end: Success
fail=>end: Failed

st->op->check
check(yes)->success
check(no)->retry
retry(yes)->op
retry(no)->fail
```

---

## Sizing Guidelines

### Limits

- **Source**: 5KB maximum
- **Nodes**: 15 maximum recommended
- **Depth**: 5 levels recommended
- **SVG Output**: ~50KB typical

### Example Sizes

- Simple decision: 5 nodes (~200 bytes)
- Login process: 10 nodes (~400 bytes)
- Business logic: 15 nodes (~600 bytes)

---

## Survival Guide Examples

### Water Safety Check

```
st=>start: Find water source
assess=>condition: Water clear?
filter=>operation: Filter through cloth
boil=>condition: Fire available?
boil_water=>operation: Boil 1-3 minutes
chemical=>operation: Use purification tablets
safe=>end: Safe to drink
wait=>operation: Wait 30 minutes

st->assess
assess(yes)->boil
assess(no)->filter->boil
boil(yes)->boil_water->safe
boil(no)->chemical->wait->safe
```

### Fire Starting Decision

```
st=>start: Need fire
conditions=>condition: Dry conditions?
materials=>condition: Materials available?
gather=>operation: Gather tinder/kindling
shelter=>operation: Find dry materials
ignite=>condition: Ignition source?
friction=>operation: Friction method
lighter=>operation: Use lighter/matches
success=>condition: Fire lit?
retry=>operation: Adjust technique
complete=>end: Fire established

st->conditions
conditions(yes)->materials
conditions(no)->shelter->materials
materials(yes)->ignite
materials(no)->gather->ignite
ignite(yes)->lighter->success
ignite(no)->friction->success
success(yes)->complete
success(no)->retry->ignite
```

### Shelter Building

```
st=>start: Need shelter
location=>condition: Safe location?
search=>operation: Find better site
assess=>condition: Materials available?
gather=>operation: Gather materials
type=>condition: Weather conditions?
lean_to=>operation: Build lean-to
a_frame=>operation: Build A-frame
test=>condition: Stable?
reinforce=>operation: Reinforce structure
complete=>end: Shelter ready

st->location
location(yes)->assess
location(no)->search->assess
assess(yes)->type
assess(no)->gather->type
type(yes, right)->a_frame->test
type(no, left)->lean_to->test
test(yes)->complete
test(no)->reinforce->test
```

---

## Troubleshooting

### Syntax Errors

**Problem**: Diagram fails to render

**Solutions**:
1. Check node definitions (nodeid=>type: label)
2. Verify connections (nodeid->nodeid)
3. Ensure all referenced nodes are defined
4. Check for typos in node IDs

### Arrows Not Connecting

**Problem**: Connections missing or broken

**Solutions**:
1. Verify node IDs match exactly
2. Check for extra spaces
3. Ensure conditions use (yes/no) syntax

### Layout Issues

**Problem**: Overlapping nodes or awkward layout

**Solutions**:
1. Simplify flowchart (reduce nodes)
2. Use direction hints: (yes, right) or (no, left)
3. Reorder node definitions

### Condition Paths

**Problem**: Conditions need more than yes/no

**Solution**: Use multiple condition nodes:
```
c1=>condition: Check type?
c2=>condition: Check subtype?

c1(yes)->c2
c1(no)->end
c2(yes)->action1
c2(no)->action2
```

---

## Advanced Techniques

### Parallel Paths

```
st=>start: Start
split=>parallel: Split
op1=>operation: Process A
op2=>operation: Process B
join=>parallel: Join
e=>end: End

st->split
split(path1)->op1->join
split(path2)->op2->join
join->e
```

### Subroutine Calls

```
st=>start: Start
sub1=>subroutine: Data validation
sub2=>subroutine: Business logic
sub3=>subroutine: Save results
e=>end: End

st->sub1->sub2->sub3->e
```

### Multi-Exit Conditions

```
check=>condition: Status?
status_a=>operation: Handle A
status_b=>operation: Handle B
status_c=>operation: Handle C

check(a)->status_a
check(b)->status_b
check(c)->status_c
```

---

## Admin Prompt Management

### View Prompts (DEV MODE)

```bash
CONFIG SET dev_mode true
PROMPT LIST flow
PROMPT SHOW flow_default
```

### Test Prompts

```bash
PROMPT TEST flow_default "water purification decision tree"
```

### Edit Prompts

```bash
PROMPT EDIT flow_default
```

Prompts use YAML frontmatter:
```yaml
---
id: flow_default
format: flow
version: 1.0.0
---

Generate flowchart for: {{input}}
...
```

---

## Related Documentation

- [Graphics System](Graphics-System.md) - Overall architecture
- [Sequence Diagrams Guide](Sequence-Diagrams-Guide.md) - Time-based alternative
- [Command Reference](Command-Reference.md) - MAKE command

---

**See Also**: `MAKE --help flow`, `MAKE --list flow`, flowchart.js: http://flowchart.js.org/
