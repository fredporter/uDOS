# POKE System Integration Guide

The uDOS Dashboard now includes comprehensive memory monitoring and manipulation through the POKE system.

## Features

### Memory Monitor Interface
- Real-time memory visualization
- Interactive memory cell grid
- Live value updates
- Memory watching capabilities

### POKE Operations
- Direct memory manipulation
- Memory value monitoring
- Address watching
- Value change notifications

## Usage

### Opening the Memory Monitor
1. Press `Cmd/Ctrl + K` to open Command Palette
2. Type "memory" to find memory-related commands
3. Select "Show Memory Monitor"

### Basic Operations

#### POKE (Write Memory)
```javascript
// Through Dashboard API
dashboardAPI.poke.poke(address, value);

// Example: Write value 42 to address $2000
dashboardAPI.poke.poke(0x2000, 42);
```

#### PEEK (Read Memory)
```javascript
// Through Dashboard API
const value = await dashboardAPI.poke.peek(address);

// Example: Read value from address $2000
const value = await dashboardAPI.poke.peek(0x2000);
```

### Memory Watching

#### Set up a Watch
```javascript
// Watch an address with custom options
const cleanup = dashboardAPI.poke.watchAddress(
    address,
    (data) => {
        console.log(`Value changed: ${data.value}`);
    },
    {
        threshold: 1,    // Minimum change to trigger
        interval: 1000   // Check every 1000ms
    }
);

// Later: Remove the watch
cleanup();
```

## Technical Details

### Memory Map
- 64K address space ($0000-$FFFF)
- 8-bit values ($00-$FF)
- Real-time updates via WebSocket

### WebSocket Events
- `memory_update`: Fired when memory values change
- `watch_trigger`: Fired when watched values change

### REST API Endpoints
- GET `/api/poke/memory/<address>`: PEEK operation
- POST `/api/poke/memory/<address>/<value>`: POKE operation

## Integration Examples

### Monitor Specific Memory Range
```javascript
// Watch a range of memory addresses
function watchMemoryRange(start, end) {
    for (let addr = start; addr <= end; addr++) {
        dashboardAPI.poke.watchAddress(
            addr,
            (data) => console.log(`Address $${addr.toString(16)}: ${data.value}`)
        );
    }
}

// Example: Watch first 256 bytes
watchMemoryRange(0x0000, 0x00FF);
```

### Create Custom Memory Display
```javascript
// Example: Create a custom memory view
class CustomMemoryView {
    constructor(container) {
        this.container = container;
        this.setup();
    }

    setup() {
        // Subscribe to memory updates
        dashboardAPI.poke.subscribe((data) => {
            if (data.type === 'update') {
                this.updateDisplay(data);
            }
        });
    }

    updateDisplay(data) {
        // Custom display logic
    }
}
```

## Theme Integration

The memory monitor automatically adapts to the current dashboard theme:
- Retro-style memory grid
- Theme-appropriate colors
- Consistent typography
- Animated updates
