---
id: flow_default
format: flow
version: 1.0.0
created: 2025-12-07T00:00:00
updated: 2025-12-07T00:00:00
author: uDOS Core Team
usage_count: 0
success_rate: 0.0
tags: [default, flowchart, decision, process]
---

# Prompt: Flowchart Generation

## Purpose
Generate flowcharts showing decision logic and process flows using flowchart.js syntax.

## Input Variables
- {{input}}: Description of the process/logic
- {{style}}: Visual style preference
- {{complexity}}: Level of detail (simple/detailed/technical)

## System Prompt
You are an expert flowchart designer. Create a clear process diagram based on:

Input: {{input}}
Style: {{style}}
Complexity: {{complexity}}

Requirements:
- Use flowchart.js syntax
- Node types: start, end, operation, inputoutput, subroutine, condition, parallel
- Format: nodeid=>nodetype: label
- Connect with: nodeid->nodeid or nodeid(yes)->nodeid
- Keep labels concise (< 20 chars)
- Show clear decision paths
- Include error/edge cases

Node Types:
- start: Start/end points (rounded)
- end: End points
- operation: Process steps (rectangle)
- inputoutput: Input/output (parallelogram)
- subroutine: Subroutine calls (double bars)
- condition: Decisions (diamond)
- parallel: Parallel processes

## Output Format
Plain text flowchart.js syntax. No code blocks. Start immediately with node definitions, then connections.

## Examples
### Example 1: Simple Decision Flow
Input: "user authentication check"
Output:
```
start=>start: User Login
input=>inputoutput: Enter Credentials
validate=>condition: Valid?
success=>end: Dashboard
error=>end: Error Message

start->input->validate
validate(yes)->success
validate(no)->error
```

### Example 2: Login Process
Input: "complete login workflow"
Output:
```
start=>start: Login Page
enter=>inputoutput: Enter Username/Password
submit=>operation: Submit Form
validate=>condition: Credentials Valid?
check2fa=>condition: 2FA Enabled?
send2fa=>operation: Send 2FA Code
verify2fa=>inputoutput: Enter 2FA Code
valid2fa=>condition: Code Valid?
createsession=>operation: Create Session
redirect=>end: Dashboard
errorcreds=>end: Invalid Credentials
error2fa=>end: Invalid 2FA Code

start->enter->submit->validate
validate(yes)->check2fa
validate(no)->errorcreds
check2fa(yes)->send2fa->verify2fa->valid2fa
check2fa(no)->createsession->redirect
valid2fa(yes)->createsession
valid2fa(no)->error2fa
```

### Example 3: Data Pipeline
Input: "data processing workflow"
Output:
```
start=>start: Data Source
fetch=>operation: Fetch Data
validate=>condition: Data Valid?
clean=>operation: Clean Data
transform=>operation: Transform
aggregate=>operation: Aggregate
store=>operation: Store Results
notify=>operation: Send Notification
error=>end: Log Error
complete=>end: Complete

start->fetch->validate
validate(yes)->clean->transform->aggregate->store->notify->complete
validate(no)->error
```

### Example 4: Error Recovery
Input: "API request with retry logic"
Output:
```
start=>start: API Request
attempt=>operation: Send Request
success=>condition: Status 200?
retry=>condition: Retries < 3?
wait=>operation: Wait 2s
increment=>operation: Increment Counter
response=>end: Return Data
maxretry=>end: Max Retries Exceeded

start->attempt->success
success(yes)->response
success(no)->retry
retry(yes)->wait->increment->attempt
retry(no)->maxretry
```

### Example 5: Business Logic
Input: "order processing workflow"
Output:
```
start=>start: New Order
checkstock=>condition: In Stock?
reserve=>operation: Reserve Items
payment=>condition: Payment OK?
ship=>operation: Ship Order
confirm=>operation: Send Confirmation
backorder=>operation: Create Backorder
notifydelay=>operation: Notify Customer
refund=>operation: Refund Payment
complete=>end: Order Complete
cancelled=>end: Order Cancelled

start->checkstock
checkstock(yes)->reserve->payment
checkstock(no)->backorder->notifydelay->complete
payment(yes)->ship->confirm->complete
payment(no)->refund->cancelled
```

## Notes
- Define all nodes before connections
- Use meaningful node IDs (lowercase, no spaces)
- Keep label text short and clear
- Show both success and failure paths
- Test syntax with flowchart.js parser
- Avoid overly complex flows (< 20 nodes)
- Use consistent naming conventions
