# Sequence Diagrams Guide (v1.2.15)

Complete reference for js-sequence-diagrams in uDOS.

---

## Overview

Sequence diagrams visualize message flows between actors/systems over time using js-sequence-diagrams syntax. Ideal for documenting workflows, API interactions, and step-by-step processes in survival guides.

### Key Features

- **Native Markdown**: Pure text format (no API required)
- **Message Flows**: Actor-to-object interactions
- **Time-Ordered**: Chronological sequence
- **SVG Output**: Rendered via Node.js service
- **Size Limit**: 5KB source text, ~50KB SVG output

---

## Basic Syntax

### Actors and Objects

Define participants:
```
User->System: Message
Actor->Object: Message description
```

**Naming Rules**:
- Maximum 12 characters
- Use CamelCase or underscores
- Start with letter

**Examples**:
```
User->Server: Login request
Server->Database: Query user
Database->Server: Return data
Server->User: Login success
```

### Message Types

**Solid Arrow** (synchronous):
```
Actor->Object: Message
```

**Dashed Arrow** (async response):
```
Actor-->Object: Async response
```

**Note Annotations**:
```
Note left of Actor: Note text
Note right of Actor: Note text
Note over Actor: Spanning note
Note over Actor,Object: Multi-actor note
```

---

## Available Templates

### 1. Login Flow (`login_flow.seq`)

**Use Case**: User authentication process

**Example**:
```
User->App: Enter credentials
App->API: POST /auth/login
API->Database: Validate user
Database-->API: User data
API-->App: Auth token
App-->User: Success message
```

**Variations**:
- 2FA authentication
- OAuth flow
- Password reset

### 2. Error Handling (`error_handling.seq`)

**Use Case**: Error recovery workflows

**Example**:
```
Client->Server: Request data
Server->Database: Query
Database-->Server: Connection error
Server->Fallback: Use cache
Fallback-->Server: Cached data
Server-->Client: Response (cached)
Note over Server: Retry scheduled
```

**Patterns**:
- Retry logic
- Fallback strategies
- Error propagation

### 3. Multi-System (`multi_system.seq`)

**Use Case**: Complex system interactions

**Example**:
```
Frontend->API: Create order
API->Inventory: Check stock
Inventory-->API: Stock confirmed
API->Payment: Process payment
Payment-->API: Payment success
API->Email: Send confirmation
Email-->API: Email sent
API-->Frontend: Order created
```

**Use Cases**:
- Microservices communication
- Third-party integrations
- Distributed systems

### 4. Async Process (`async_process.seq`)

**Use Case**: Background job workflows

**Example**:
```
User->App: Upload file
App->Queue: Add job
App-->User: Upload accepted
Note over Queue: Processing...
Queue->Worker: Process job
Worker->Storage: Save result
Storage-->Worker: Saved
Worker-->Queue: Job complete
Queue->App: Notify completion
App->User: Email notification
```

**Patterns**:
- Job queues
- Background processing
- Webhook callbacks

### 5. Survival Guide (`survival_guide.seq`)

**Use Case**: Step-by-step survival procedures

**Example**:
```
Person->Environment: Assess situation
Person->Resources: Gather materials
Resources-->Person: Materials found
Person->Fire: Build fire pit
Person->Fire: Prepare tinder
Person->Fire: Light fire
Fire-->Person: Fire established
Note over Person: Shelter next
```

**Use Cases**:
- Water purification steps
- Shelter building sequence
- First aid procedures

---

## Command Usage

### Generate Diagram

```bash
# From template
MAKE --format sequence --template login_flow --source "User authentication"

# Custom sequence
MAKE --format sequence --source "
User->System: Request
System->Database: Query
Database-->System: Data
System-->User: Response
"

# From file
MAKE --format sequence --source "$(cat flow.seq)"
```

### Output

```bash
--output memory/drafts/svg/login_flow.svg
```

---

## Best Practices

### 1. Keep It Simple

✅ **Good** (clear flow):
```
User->API: Request
API->DB: Query
DB-->API: Data
API-->User: Response
```

❌ **Too Complex** (hard to follow):
```
User->Gateway->LB->API1->Cache->API2->DB1->DB2->...
```

**Solution**: Split into multiple diagrams

### 2. Descriptive Messages

✅ **Good** (actionable):
```
User->System: Click "Submit" button
System->API: POST /orders with payload
API->Database: INSERT order record
```

❌ **Vague**:
```
User->System: Action
System->API: Call
API->Database: Operation
```

### 3. Use Notes for Context

```
User->App: Upload photo
Note over App: Validate size and format
App->Storage: Save to S3
Note over Storage: Auto-scaling enabled
Storage-->App: URL returned
```

### 4. Consistent Naming

Use consistent actor names throughout:

✅ **Good**:
```
User->Frontend: ...
Frontend->Backend: ...
Backend->User: ...
```

❌ **Inconsistent**:
```
Person->UI: ...
FrontEnd->API: ...
api->person: ...
```

### 5. Limit Participants

Keep to 5-7 actors maximum:

✅ **Good**: User, App, API, Database, Email
❌ **Too Many**: User, Frontend, Gateway, LoadBalancer, API1, API2, Cache, DB1, DB2, Queue, Worker, Email, SMS, Logger...

**Solution**: Group related systems

---

## Common Patterns

### Request-Response

```
Client->Server: Request
Server-->Client: Response
```

### Error Recovery

```
Client->Server: Request
Server->Service: Call API
Service-->Server: Error 500
Server->Cache: Check cache
Cache-->Server: Cached data
Server-->Client: Response (cached)
```

### Background Job

```
User->App: Submit job
App->Queue: Enqueue
App-->User: Job ID
Note over Queue: Processing
Queue->Worker: Dequeue job
Worker->Database: Save results
Worker-->Queue: Job complete
Queue->App: Webhook callback
App->User: Email notification
```

### Multi-Step Workflow

```
User->System: Step 1
System-->User: Result 1
Note over User: Review
User->System: Step 2
System-->User: Result 2
Note over User: Confirm
User->System: Step 3 (final)
System-->User: Complete
```

---

## Sizing Guidelines

### Limits

- **Source**: 5KB maximum
- **Participants**: 7 maximum recommended
- **Messages**: 20-30 maximum recommended
- **SVG Output**: ~50KB typical

### Example Sizes

- Simple login: 10 messages (~300 bytes)
- Error handling: 15 messages (~450 bytes)
- Multi-system: 20 messages (~600 bytes)

---

## Survival Guide Examples

### Water Purification

```
Person->Container: Collect water
Note over Container: Allow sediment to settle (30 min)
Person->Cloth: Pre-filter
Cloth-->Person: Filtered water
Person->BoilingPot: Boil water
Note over BoilingPot: Rolling boil 1-3 minutes
BoilingPot-->Person: Purified water
Person->Storage: Store in clean container
Note over Person: Safe to drink
```

### Fire Starting

```
Person->Location: Choose site
Note over Location: Flat, dry, sheltered
Person->Materials: Gather tinder
Person->Materials: Gather kindling
Person->Materials: Gather fuel wood
Person->FirePit: Clear area
Person->FirePit: Build tinder nest
Person->Ignition: Create spark
Ignition-->FirePit: Tinder ignites
Note over FirePit: Add kindling gradually
FirePit->Person: Established fire
```

### Shelter Building

```
Person->Environment: Assess conditions
Note over Environment: Wind direction, rain, hazards
Person->Location: Choose site
Person->Materials: Gather poles
Person->Materials: Gather covering
Person->Frame: Build A-frame
Person->Frame: Add crossbeams
Person->Frame: Layer branches
Person->Frame: Add insulation
Note over Frame: Test stability
Frame->Person: Shelter complete
```

---

## Troubleshooting

### Syntax Errors

**Problem**: Diagram fails to render

**Solutions**:
1. Check arrow syntax (-> or -->)
2. Verify actor names (no spaces, <12 chars)
3. Ensure messages quoted if special chars
4. Check for missing colons

### Overlapping Messages

**Problem**: Text overlaps on diagram

**Solutions**:
1. Shorten actor names
2. Reduce message text length
3. Split into multiple diagrams

### Missing Actors

**Problem**: Actor doesn't appear

**Solution**: Actor must send/receive at least one message

---

## Themes

js-sequence-diagrams supports 2 themes:

### Simple (Default)

```bash
MAKE --format sequence --theme simple --source "flow"
```

Clean, minimalist style with straight lines.

### Hand-Drawn

```bash
MAKE --format sequence --theme hand --source "flow"
```

Sketch-style with hand-drawn appearance.

---

## Admin Prompt Management

### View Prompts (DEV MODE)

```bash
CONFIG SET dev_mode true
PROMPT LIST sequence
PROMPT SHOW sequence_default
```

### Test Prompts

```bash
PROMPT TEST sequence_default "user login workflow"
```

### Edit Prompts

```bash
PROMPT EDIT sequence_default
```

Prompts use YAML frontmatter:
```yaml
---
id: sequence_default
format: sequence
version: 1.0.0
---

Generate sequence diagram for: {{input}}
...
```

---

## Related Documentation

- [Graphics System](Graphics-System.md) - Overall architecture
- [Flowchart Guide](Flowchart-Guide.md) - Decision flow alternative
- [Command Reference](Command-Reference.md) - MAKE command

---

**See Also**: `MAKE --help sequence`, `MAKE --list sequence`, js-sequence-diagrams: https://bramp.github.io/js-sequence-diagrams/
