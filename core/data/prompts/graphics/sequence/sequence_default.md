---
id: sequence_default
format: sequence
version: 1.0.0
created: 2025-12-07T00:00:00
updated: 2025-12-07T00:00:00
author: uDOS Core Team
usage_count: 0
success_rate: 0.0
tags: [default, sequence, interaction, flow]
---

# Prompt: Sequence Diagram Generation

## Purpose
Generate sequence diagrams showing interactions between actors and systems using js-sequence-diagrams syntax.

## Input Variables
- {{input}}: Description of the interaction/process
- {{style}}: Diagram style (simple/hand/napkin)
- {{complexity}}: Level of detail (simple/detailed/technical)

## System Prompt
You are an expert sequence diagram creator. Generate a clear interaction diagram based on:

Input: {{input}}
Style: {{style}}
Complexity: {{complexity}}

Requirements:
- Use js-sequence-diagrams syntax
- Format: Actor->Object: Message
- Use --> for return messages (dashed arrows)
- Add notes with: Note left/right of Actor: Text
- Keep participant names concise (< 12 chars)
- Show clear message flow
- Include error paths if relevant

Syntax Elements:
- Solid arrow: Actor->Object: Message
- Dashed arrow: Object-->Actor: Response
- Note: Note right of Actor: Comment
- Participants auto-detected from usage

## Output Format
Plain text js-sequence-diagrams syntax. No code blocks. Start immediately with diagram syntax.

## Examples
### Example 1: Login Flow
Input: "user login process"
Output:
```
User->Frontend: Enter credentials
Frontend->API: POST /login
API->Database: Validate user
Database-->API: User found
API->Auth: Generate token
Auth-->API: JWT token
API-->Frontend: 200 OK + token
Frontend-->User: Login successful
Note right of User: Redirected to dashboard
```

### Example 2: Error Handling
Input: "API request with error handling"
Output:
```
Client->API: GET /data
API->Cache: Check cache
Cache-->API: Cache miss
API->Database: Query data
Database-->API: Connection timeout
API->Logger: Log error
Logger-->API: Logged
API-->Client: 500 Server Error
Note left of Client: Retry with backoff
Client->API: GET /data (retry)
API->Database: Query data
Database-->API: Data rows
API-->Client: 200 OK + data
```

### Example 3: Multi-System Interaction
Input: "payment processing flow"
Output:
```
User->Frontend: Submit payment
Frontend->API: POST /payment
API->Validator: Validate amount
Validator-->API: Valid
API->PaymentGW: Process payment
PaymentGW->Bank: Authorize
Bank-->PaymentGW: Approved
PaymentGW-->API: Transaction ID
API->Database: Save transaction
Database-->API: Saved
API->Email: Send receipt
Email-->API: Queued
API-->Frontend: 201 Created
Frontend-->User: Payment successful
Note right of User: Receipt sent to email
```

### Example 4: Asynchronous Process
Input: "background job processing"
Output:
```
User->API: Upload file
API->Storage: Save file
Storage-->API: File ID
API->Queue: Enqueue job
Queue-->API: Job queued
API-->User: 202 Accepted
Note right of User: Processing asynchronously
Queue->Worker: Dequeue job
Worker->Storage: Fetch file
Storage-->Worker: File data
Worker->Processor: Process
Processor-->Worker: Results
Worker->Database: Save results
Database-->Worker: Saved
Worker->Notification: Notify user
Notification->User: Processing complete
```

## Notes
- Keep participant names short and clear
- Use descriptive message labels
- Show both success and error paths
- Include relevant notes for context
- Avoid overly complex diagrams (< 15 interactions)
- Test syntax with js-sequence-diagrams parser
