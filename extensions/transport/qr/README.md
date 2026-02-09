# uDOS QR Transport

**Alpha v1.0.1.0+**

Visual data transfer via QR codes for uDOS offline mesh communication.

---

## 🎯 Purpose

QR Transport enables **visual data relay** between uDOS devices without Bluetooth, NFC, or network connectivity. Ideal for:

- **Air-gapped transfers** - Move data between isolated networks
- **Device pairing** - Exchange handshake codes visually
- **Command relay** - Send uDOS commands via camera
- **Public displays** - Share data on screens/paper for multi-device pickup

---

## 📦 Components

| Component | File | Purpose |
|-----------|------|---------|
| **QRPacket** | `packet.py` | Packet format with chunking and CRC32 validation |
| **QREncoder** | `encoder.py` | Generate QR codes from data/commands |
| **QRDecoder** | `decoder.py` | Scan and decode QR codes (requires zbar) |

---

## 🔒 Transport Policy

**Realm:** PRIVATE_SAFE  
**Data Allowed:** Yes (with packet size limits)  
**Commands Allowed:** Yes (device pairing, data transfer)  
**Roles:** `device_owner`, `paired_device`, `mobile_console`  
**Exposure Tier:** PRIVATE_SAFE (never exposed to public networks)

---

## 📋 Packet Format

All QR codes contain JSON packets with this structure:

```json
{
  "v": "1.0.1.0",
  "type": "data",
  "id": "abc123",
  "chunk": 1,
  "total": 3,
  "data": "SGVsbG8sIHVET1MhCg==",
  "crc": 3008344432,
  "meta": {}
}
```

### Packet Types

| Type | Purpose | Metadata |
|------|---------|----------|
| `data` | Raw data transfer | `size`, `encoding` |
| `command` | uDOS command | `command`, `params` |
| `file` | File transfer | `filename`, `mime_type` |
| `handshake` | Device pairing | `device_id`, `device_name` |
| `ack` | Acknowledgment | `packet_id`, `success` |
| `error` | Error message | `error_type`, `message` |

### Features

- **Automatic chunking** - Splits large data into 256-byte chunks (max 2KB per QR)
- **CRC32 validation** - Detects corruption/tampering
- **Base64 encoding** - Binary-safe data transfer
- **Multi-chunk assembly** - Reconstructs data from multiple QR codes
- **Missing chunk detection** - Identifies incomplete transfers

---

## 🚀 Usage

### Encoding Data

```python
from extensions.transport.qr import QREncoder, PacketType

encoder = QREncoder(chunk_size=256)

# Text to QR
packets = encoder.encode_text("Hello, uDOS!")
encoder.save_packets_qr(packets, output_dir="memory/.tmp/qr")

# Command to QR
packets = encoder.encode_command("FILE", ["SHOW", "README.MD"])
encoder.print_packet_qr(packets[0])  # ASCII QR to console

# Binary data
data = b"\x00\x01\x02" * 100
packets = encoder.encode_data(data, PacketType.FILE, metadata={"filename": "test.bin"})
```

### Decoding QR Codes

```python
from extensions.transport.qr import QRDecoder

decoder = QRDecoder()

# Decode from image file
packet = decoder.decode_image("qr_abc123_chunk1of3.png")

# Verify CRC
if decoder.verify_crc(packet):
    print("✅ CRC valid")

# Assemble multi-chunk packets
qr_images = ["chunk1.png", "chunk2.png", "chunk3.png"]
data = decoder.decode_and_assemble(qr_images, verify_crc=True)
```

### Packet Assembly (Manual)

```python
from extensions.transport.qr import PacketAssembler

assembler = PacketAssembler()

# Add chunks as they arrive
for packet in received_packets:
    complete = assembler.add_chunk(packet)
    if complete:
        data = assembler.get_assembled_data(packet.packet_id)
        print(f"✅ Received {len(data)} bytes")
        break
    else:
        missing = assembler.get_missing_chunks(packet.packet_id)
        print(f"Waiting for chunks: {missing}")
```

---

## 🧪 Testing

### Test Encoder

```bash
cd extensions/transport/qr
source ../../../venv/bin/activate
python encoder.py
```

Output:
- ASCII QR codes printed to console
- PNG QR codes saved to `memory/.tmp/qr-test/`

### Test Decoder (Packet Assembly Only)

```bash
python -c "
from packet import PacketBuilder, PacketAssembler, PacketType
# ... (see encoder.py test output for full test)
"
```

### Test Full Decode (Requires zbar)

**macOS:**
```bash
brew install zbar
pip install pyzbar pillow
python decoder.py
```

**Linux:**
```bash
sudo apt-get install libzbar0
pip install pyzbar pillow
python decoder.py
```

---

## 📐 QR Code Specifications

| Parameter | Value | Notes |
|-----------|-------|-------|
| Version | Auto (1-40) | Adjusts to data size |
| Error Correction | High (H) | 30% damage tolerance |
| Chunk Size | 256 bytes | Before base64 encoding |
| Max QR Data | ~1,800 bytes | Version 40 with High EC |
| Effective Chunk | ~350 bytes | After JSON/base64 overhead |
| Box Size | 10 pixels | Configurable |
| Border | 4 boxes | QR standard |

---

## 🔗 Integration with uDOS

### Command Dispatch

```python
# In core/uDOS_commands.py
if transport == "qr_relay":
    # Validate QR transport policy
    validation = policy_validator.validate_command(
        command="QR",
        role=current_role,
        transport="qr_relay",
        realm=current_realm
    )
    
    if validation == ValidationResult.PERMITTED:
        # Route to QR handler
        return qr_handler.handle(module, params, grid, parser)
```

### Planned Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `QR SEND` | Encode data to QR | `QR SEND FILE README.MD` |
| `QR RECEIVE` | Scan QR codes | `QR RECEIVE CAMERA` |
| `QR PAIR` | Device pairing | `QR PAIR MOBILE` |
| `QR SHOW` | Display QR code | `QR SHOW HANDSHAKE` |

---

## 🛡️ Security Considerations

### Policy Enforcement

- **NEVER transmit secrets via QR** - Assumes public display
- **Realm isolation** - QR codes only within private realm
- **CRC validation required** - Detect tampering/corruption
- **Chunk limits** - Prevent memory exhaustion attacks
- **No automatic execution** - Commands require explicit acceptance

### Attack Surface

| Threat | Mitigation |
|--------|------------|
| QR tampering | CRC32 validation |
| Chunk injection | Packet ID validation |
| Large payloads | Max chunk size (256 bytes) |
| Command injection | Policy validator before execution |
| Replay attacks | Optional timestamp in metadata |

---

## 📊 Performance

### Throughput

- **Single QR:** 36 bytes (text) → 149 bytes (JSON) → ~2 seconds scan time
- **Multi-chunk:** 1500 bytes → 3 QR codes → ~6-10 seconds total
- **Effective rate:** 150-250 bytes/second (human-paced)

### Comparison to Other Transports

| Transport | Rate | Range | Notes |
|-----------|------|-------|-------|
| **QR Relay** | 150-250 B/s | Visual (10m+) | Human-paced, public display |
| **Audio Relay** | 100-200 B/s | Acoustic (20m) | Ambient noise issues |
| **NFC** | 424 KB/s | Contact (10cm) | Fast but requires proximity |
| **Bluetooth** | 1-3 MB/s | 10-100m | Best for large transfers |
| **MeshCore** | Variable | Network | Multi-hop routing |

---

## 📚 Dependencies

### Required

- `qrcode[pil]` - QR code generation (Python)
- `pillow` - Image processing

### Optional

- `pyzbar` - QR code scanning (Python)
- `libzbar` - System library for pyzbar (macOS: `brew install zbar`, Linux: `apt install libzbar0`)

### Fallback

Without `pyzbar`, decoder can still:
- Assemble pre-decoded packets
- Validate CRC checksums
- Track missing chunks

Users can decode QR codes with:
- External camera app → copy JSON → paste to uDOS
- Third-party QR scanner → file import

---

## 🗺️ Roadmap

### v1.0.1.1 - QR Transport (Current)

- [x] Packet format with chunking
- [x] CRC32 validation
- [x] QR encoder (PNG + ASCII)
- [x] Packet assembler (no camera required)
- [ ] QR decoder (camera integration)
- [ ] Integration with command dispatch
- [ ] uDOS commands (QR SEND/RECEIVE/PAIR)

### v1.0.1.2 - Enhancements

- [ ] Animated QR codes (multiple frames)
- [ ] Error correction codes (Reed-Solomon)
- [ ] Compression (gzip before encoding)
- [ ] Signature verification (optional metadata)

---

## 📖 Examples

### Example 1: Device Pairing

**Device A (generates handshake):**
```python
from extensions.transport.qr import QREncoder

encoder = QREncoder()
packets = encoder.encode_command(
    "PAIR",
    ["ACCEPT", "device-laptop-001"],
    metadata={"device_name": "Fred's Laptop"}
)
encoder.print_packet_qr(packets[0])  # Show QR on screen
```

**Device B (scans QR):**
```python
from extensions.transport.qr import QRDecoder

decoder = QRDecoder()
packet = decoder.decode_image("camera_capture.png")

if packet.packet_type == PacketType.COMMAND:
    import json
    cmd_data = json.loads(base64.b64decode(packet.data))
    print(f"Pair request from: {cmd_data['metadata']['device_name']}")
    # Execute pairing...
```

### Example 2: File Transfer

**Sender:**
```python
encoder = QREncoder(chunk_size=256)

with open("README.MD", "rb") as f:
    file_data = f.read()

packets = encoder.encode_data(
    file_data,
    PacketType.FILE,
    metadata={"filename": "README.MD", "mime_type": "text/markdown"}
)

encoder.save_packets_qr(packets, "memory/.tmp/qr-transfer")
print(f"Created {len(packets)} QR codes in memory/.tmp/qr-transfer/")
```

**Receiver:**
```python
decoder = QRDecoder()

# Scan all QR codes
qr_images = sorted(Path("scanned-qr/").glob("*.png"))
file_data = decoder.decode_and_assemble(qr_images, verify_crc=True)

if file_data:
    # Get metadata from first packet
    first_packet = decoder.decode_image(qr_images[0])
    filename = first_packet.metadata.get("filename", "received_file")
    
    with open(f"memory/downloads/{filename}", "wb") as f:
        f.write(file_data)
    
    print(f"✅ Received {filename} ({len(file_data)} bytes)")
```

---

## 🏷️ Logging Tags

Use these tags in logs for QR transport operations:

- `[QR]` - General QR transport activity
- `[QR-ENC]` - Encoding operations
- `[QR-DEC]` - Decoding operations
- `[QR-SCAN]` - Camera scanning
- `[QR-ASM]` - Packet assembly

Example:
```python
logger.info("[QR-ENC] Encoded 1500 bytes into 3 QR codes (packet: abc123)")
logger.info("[QR-ASM] Assembled 3/3 chunks for packet abc123")
```

---

## 🧩 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     uDOS Command Layer                      │
│              (QR SEND, QR RECEIVE, QR PAIR)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Transport Policy Layer                     │
│             (Validator, Audit Logger, Roles)                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    QR Transport Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  QRPacket    │  │  QREncoder   │  │  QRDecoder   │      │
│  │  (format)    │  │  (generate)  │  │  (scan)      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │   Physical Layer         │
              │  (Camera, Display, PNG)  │
              └──────────────────────────┘
```

---

**Last Updated:** 2026-01-04  
**Version:** Alpha v1.0.1.0  
**Status:** ✅ Encoder complete, 🔄 Decoder (packet assembly only)

