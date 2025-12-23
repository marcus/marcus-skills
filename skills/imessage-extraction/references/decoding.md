# attributedBody Decoding Reference

The `attributedBody` field in the iMessage database contains NSAttributedString data encoded using NSKeyedArchiver (binary plist format). This reference covers multiple decoding methods.

## Method 1: PyObjC (Recommended)

Most reliable method. Requires `pip install pyobjc-framework-Cocoa`.

```python
try:
    from Foundation import NSData, NSKeyedUnarchiver
    PYOBJC_AVAILABLE = True
except ImportError:
    PYOBJC_AVAILABLE = False

def decode_attributed_body(data):
    """Decode NSAttributedString from attributedBody blob."""
    if not data:
        return None

    try:
        if PYOBJC_AVAILABLE:
            ns_data = NSData.dataWithBytes_length_(data, len(data))
            unarchiver = NSKeyedUnarchiver.alloc().initForReadingWithData_(ns_data)
            unarchiver.setRequiresSecureCoding_(False)
            attributed_string = unarchiver.decodeObjectForKey_("root")

            if attributed_string and hasattr(attributed_string, 'string'):
                text = str(attributed_string.string())
                if text and len(text) > 0:
                    return text
    except Exception:
        pass

    # Fall through to manual parsing if PyObjC fails
    return manual_decode(data)
```

## Method 2: Manual Binary Parsing

When PyObjC is unavailable, extract text by searching for known markers.

```python
import struct

def manual_decode(data):
    """Extract text from attributedBody without PyObjC."""
    if not data:
        return None

    text = None

    # Try NSString marker
    if b'NSString' in data:
        idx = data.find(b'NSString') + 8
        if idx < len(data):
            end_idx = data.find(b'\x00', idx)
            if end_idx > idx:
                text = data[idx:end_idx].decode('utf-8', errors='ignore')

    # Try streamtyped marker (newer format)
    if not text and b'streamtyped' in data:
        idx = data.find(b'streamtyped') + 11
        if idx < len(data):
            try:
                length = struct.unpack('>I', data[idx:idx+4])[0]
                if 0 < length < 100000:
                    text = data[idx+4:idx+4+length].decode('utf-8', errors='ignore')
            except:
                pass

    # Try direct UTF-8 extraction
    if not text:
        offset = 50  # Skip binary header
        if len(data) > offset:
            potential_text = data[offset:].decode('utf-8', errors='ignore')
            cleaned = ''.join(c for c in potential_text if c.isprintable() or c in '\n\r\t')
            if len(cleaned) > 0 and len(cleaned) < len(data):
                text = cleaned.strip()

    return text if text and len(text) > 0 else '[binary data]'
```

## Method 3: Combined Decoder

Complete decoder with all fallback methods:

```python
import struct
import re

try:
    from Foundation import NSData, NSKeyedUnarchiver
    PYOBJC_AVAILABLE = True
except ImportError:
    PYOBJC_AVAILABLE = False

def decode_attributed_body(data):
    """
    Decode NSAttributedString from attributedBody blob.
    Returns plain text string or marker if decoding fails.
    """
    if not data:
        return None

    text = None

    # Method 1: PyObjC
    if PYOBJC_AVAILABLE:
        try:
            ns_data = NSData.dataWithBytes_length_(data, len(data))
            unarchiver = NSKeyedUnarchiver.alloc().initForReadingWithData_(ns_data)
            unarchiver.setRequiresSecureCoding_(False)
            obj = unarchiver.decodeObjectForKey_("root")
            if obj and hasattr(obj, 'string'):
                text = str(obj.string())
                if text:
                    return text
        except:
            pass

    # Method 2: NSString marker
    if b'NSString' in data:
        idx = data.find(b'NSString') + 8
        if idx < len(data):
            end_idx = data.find(b'\x00', idx)
            if end_idx > idx:
                text = data[idx:end_idx].decode('utf-8', errors='ignore')
                if text:
                    return text

    # Method 3: streamtyped marker
    if b'streamtyped' in data:
        idx = data.find(b'streamtyped') + 11
        if idx < len(data):
            try:
                length = struct.unpack('>I', data[idx:idx+4])[0]
                if 0 < length < 100000:
                    text = data[idx+4:idx+4+length].decode('utf-8', errors='ignore')
                    if text:
                        return text
            except:
                pass

    # Method 4: Direct UTF-8 extraction
    offset = 50
    if len(data) > offset:
        potential = data[offset:].decode('utf-8', errors='ignore')
        cleaned = ''.join(c for c in potential if c.isprintable() or c in '\n\r\t')
        if cleaned:
            return cleaned.strip()

    return '[binary data]'
```

## Cleaning Decoded Text

After decoding, clean common artifacts:

```python
import re

def clean_message_text(text):
    """Remove decoding artifacts from message text."""
    if not text or text in ['[binary data]', '[no text]']:
        return text

    # Object replacement character -> [image]
    text = text.replace('\ufffc', '[image]')

    # Remove non-printable chars (keep newlines/tabs)
    text = ''.join(c for c in text if c.isprintable() or c in '\n\r\t')

    # Remove leading format codes
    text = re.sub(r'^\+[A-Za-z0-9]', '', text)
    text = re.sub(r'^[\+\*\!\.\,\;\#\%\`\~\^\&\@\$]+', '', text)

    # Remove trailing NS* artifacts
    text = re.sub(r'iI[A-Z]*NSDictionary$', '', text)
    text = re.sub(r'iI[^\w\s]+$', '', text)
    text = re.sub(r'[ij]I$', '', text)
    text = re.sub(r'NSDictionary$', '', text)

    # Remove trailing special chars
    text = re.sub(r'[\+\`\~]$', '', text)

    # Collapse multiple spaces
    text = re.sub(r'  +', ' ', text)

    return text.strip()
```

## Common Artifact Patterns

| Pattern | Source | Removal |
|---------|--------|---------|
| `\ufffc` | Object replacement (image marker) | Replace with `[image]` |
| `+X` at start | Format code leakage | `re.sub(r'^\+[A-Za-z0-9]', '')` |
| `iINSDictionary` | Trailing NS artifacts | `re.sub(r'iI.*NSDictionary$', '')` |
| `7which...` | Leading digit artifact | `re.sub(r'^[0-9](?=[a-zA-Z])', '')` |
| `Tand...` | Leading uppercase artifact | `re.sub(r'^[A-Z](?=(?:and\|the\|...)\\b)', '')` |

## Testing Decode Quality

```python
def test_decode_quality(db_path, chat_id, sample_size=100):
    """Check decode success rate for a conversation."""
    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.text, m.attributedBody
        FROM message m
        JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
        WHERE cmj.chat_id = ?
        LIMIT ?
    """, (chat_id, sample_size))

    stats = {'text_only': 0, 'attributed': 0, 'decoded': 0, 'failed': 0}

    for text, attributed in cursor.fetchall():
        if text:
            stats['text_only'] += 1
        elif attributed:
            stats['attributed'] += 1
            decoded = decode_attributed_body(attributed)
            if decoded and decoded != '[binary data]':
                stats['decoded'] += 1
            else:
                stats['failed'] += 1

    conn.close()

    total = stats['text_only'] + stats['attributed']
    success = stats['text_only'] + stats['decoded']
    print(f"Decode rate: {success}/{total} ({100*success/total:.1f}%)")
    return stats
```
