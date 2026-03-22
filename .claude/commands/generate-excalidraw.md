---
description: Generate an Excalidraw architecture diagram from a Terraform module
---

You are generating an Excalidraw (`.excalidraw`) architecture diagram for a Terraform module.
The diagram should visualize the AWS resources the module creates and their relationships.

## Your Task

1. **Analyze the Terraform module:**
   - Read `main.tf`, `variables.tf`, `outputs.tf`, and any other `.tf` files.
   - Identify all AWS resources, modules, and their relationships.
   - Group resources logically (e.g., VPC, subnets, ASGs, supporting services).

2. **Generate a valid `.excalidraw` JSON file** at `docs/assets/architecture.excalidraw`.

3. **Update `docs/index.md`** to reference the diagram if not already present:
   ```markdown
   ![Architecture](assets/architecture.png)
   ```
   Note: The user will export the `.excalidraw` to PNG separately.

## Excalidraw File Format

The file MUST be valid JSON with this top-level structure:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://app.excalidraw.com",
  "elements": [...],
  "appState": {
    "gridSize": 20,
    "gridStep": 5,
    "gridModeEnabled": false,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```

## Element Properties

CRITICAL: Every element MUST include ALL required properties.
Missing properties cause rendering failures (text shows "undefined", elements
become invisible, text gets squeezed to zero height).

### Common properties (ALL element types)

Every element (text, rectangle, ellipse, arrow, line) MUST have:

```json
{
  "id": "unique_id",
  "type": "rectangle",
  "x": 100,
  "y": 200,
  "width": 180,
  "height": 50,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#e7f5ff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "angle": 0,
  "seed": 1001,
  "version": 1,
  "isDeleted": false,
  "boundElements": [],
  "link": null,
  "locked": false,
  "groupIds": [],
  "frameId": null,
  "roundness": null,
  "index": "a0"
}
```

### Text elements

Text elements MUST additionally have these properties or they will render as "undefined":

```json
{
  "type": "text",
  "text": "My Label",
  "originalText": "My Label",
  "fontSize": 16,
  "fontFamily": 1,
  "textAlign": "center",
  "verticalAlign": "top",
  "baseline": 14,
  "lineHeight": 1.25,
  "containerId": null,
  "autoResize": true,
  "height": 20
}
```

**Height calculation:** `height = fontSize * lineHeight * lineCount`
where `lineCount = text.count('\n') + 1`.

**Baseline approximation:** `baseline = fontSize * 0.88` (rounded to int).

**Width approximation:** `width = fontSize * 0.62 * maxLineLength`
where `maxLineLength` is the character count of the longest line.

NEVER set `height` to `null` - this causes text to collapse to zero height.

### Rectangle elements

For rectangles with rounded corners, use:
```json
"roundness": { "type": 3 }
```

For sharp corners: `"roundness": null`

### Arrow elements

```json
{
  "type": "arrow",
  "points": [[0, 0], [0, 100]],
  "startBinding": {
    "elementId": "source_element_id",
    "focus": 0,
    "gap": 5,
    "fixedPoint": null
  },
  "endBinding": {
    "elementId": "target_element_id",
    "focus": 0,
    "gap": 5,
    "fixedPoint": null
  },
  "startArrowhead": null,
  "endArrowhead": "arrow",
  "elbowed": false
}
```

The `points` array is relative to the arrow's `(x, y)` position.
For a vertical arrow from (100, 200) to (100, 350):
`x=100, y=200, points=[[0,0],[0,150]]`.

### Line elements (non-arrow connections)

```json
{
  "type": "line",
  "points": [[0, 0], [200, 0]],
  "startBinding": null,
  "endBinding": null,
  "startArrowhead": null,
  "endArrowhead": null
}
```

### Container-bound text

When placing text inside a shape (rectangle/ellipse), you must set up a two-way binding:

1. On the container (rectangle): add the text element to `boundElements`:
   ```json
   "boundElements": [{"id": "text_element_id", "type": "text"}]
   ```

2. On the text element: set `containerId`:
   ```json
   "containerId": "rectangle_id"
   ```

Bound text elements can have empty `text` and `originalText` (`""`) -
the Excalidraw editor uses these as placeholders.

Also add arrow bindings to `boundElements` when arrows connect to a shape:
```json
"boundElements": [
  {"id": "arrow_1", "type": "arrow"},
  {"id": "label_text", "type": "text"}
]
```

## Layout Guidelines

### Recommended layout (top-to-bottom flow)

```
Row 1 (y~60):   Clients (ellipse)
Row 2 (y~146):  DNS / Route53 (rectangle)
Row 3 (y~239):  VPC frame (large rectangle containing):
  Row 3a (y~280):  ALBs (rectangles)
  Row 3b (y~370):  ASG frames (rectangles containing):
    Row 3c (y~410):  Instance nodes (small rectangles)
Row 4 (y~710):  Supporting services (S3, Secrets, CloudWatch, Lambda)
```

### Color palette (use Excalidraw's default palette)

| Resource Type | Background Color | Example |
|---------------|-----------------|---------|
| VPC / Network | `#ebfbee` (light green) | VPC frame |
| Compute (ASG) | `#e7f5ff` (light blue) | ASG frames |
| Load Balancers | `#fff4e6` (light orange) | ALBs |
| Master nodes | `#fff4e6` (light orange) | Master instances |
| Data nodes | `#d0ebff` (blue) | Data instances |
| DNS | `#e5dbff` (light purple) | Route53 |
| Storage | `#ebfbee` (light green) | S3 |
| Security | `#ffe3e3` (light red) | Secrets Manager |
| Monitoring | `#e5dbff` (light purple) | CloudWatch |
| Serverless | `#fff4e6` (light orange) | Lambda |
| Clients | `#e9ecef` (light gray) | User ellipse |

### Spacing

- Horizontal spacing between sibling elements: 20-30px
- Vertical spacing between rows: 40-60px
- Padding inside frames: 18-20px
- Element widths: 80px (nodes), 160-180px (services/ALBs), 320px (ASG frames)
- Element heights: 50px (services/ALBs), 60px (nodes), 200px (ASG frames)

### Font sizes

| Element | Font Size |
|---------|-----------|
| Title | 28 |
| Main labels (ALB, services) | 16 |
| ASG frame labels | 14 |
| Node labels | 13 |
| Role descriptions, edge labels | 12 |
| Protocol annotations | 11 |
| DNS names | 10 |

### Element IDs

Use descriptive snake_case IDs for hand-placed elements (e.g., `master_alb`, `data1_label`,
`arrow_dns_master_alb`). Auto-generated container-bound text can use random IDs.

### Seed values

Each element needs a unique `seed` (integer) for Excalidraw's hand-drawn rendering.
Use incrementing values (100, 101, 102, ...) or any unique integers.

### Index values

Each element needs a unique `index` string for ordering. Use a simple scheme:
`"a0"`, `"a1"`, `"a2"`, ..., `"a9"`, `"aA"`, `"aB"`, ... up to `"az"`,
then `"b0"`, `"b1"`, etc.

## Generating the file

Use Python to generate the JSON. Write a script that:

1. Defines helper functions for creating elements with all required properties.
2. Builds the element list based on the module's resources.
3. Writes valid JSON with `indent=2` and a trailing newline.

Example helper:

```python
import json
import time

seed_counter = 100
index_counter = 0

def next_seed():
    global seed_counter
    seed_counter += 1
    return seed_counter

def next_index():
    global index_counter
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    prefix = chr(ord('a') + index_counter // len(chars))
    suffix = chars[index_counter % len(chars)]
    index_counter += 1
    return f"{prefix}{suffix}"

def make_text(id, x, y, text, font_size=16, color="#1e1e1e",
              text_align="center", container_id=None):
    line_count = text.count('\n') + 1
    max_line_len = max(len(line) for line in text.split('\n'))
    return {
        "id": id,
        "type": "text",
        "x": x, "y": y,
        "width": font_size * 0.62 * max_line_len,
        "height": font_size * 1.25 * line_count,
        "text": text,
        "originalText": text,
        "fontSize": font_size,
        "fontFamily": 1,
        "textAlign": text_align,
        "verticalAlign": "top",
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "angle": 0,
        "seed": next_seed(),
        "version": 1,
        "isDeleted": False,
        "boundElements": [],
        "link": None,
        "locked": False,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "containerId": container_id,
        "autoResize": True,
        "lineHeight": 1.25,
        "baseline": int(font_size * 0.88),
        "index": next_index(),
        "updated": int(time.time() * 1000),
        "versionNonce": next_seed(),
    }

def make_rect(id, x, y, w, h, bg="#e7f5ff", stroke_width=2,
              bound_elements=None):
    return {
        "id": id,
        "type": "rectangle",
        "x": x, "y": y,
        "width": w, "height": h,
        "strokeColor": "#1e1e1e",
        "backgroundColor": bg,
        "fillStyle": "solid",
        "strokeWidth": stroke_width,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "angle": 0,
        "seed": next_seed(),
        "version": 1,
        "isDeleted": False,
        "boundElements": bound_elements or [],
        "link": None,
        "locked": False,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "index": next_index(),
        "updated": int(time.time() * 1000),
        "versionNonce": next_seed(),
    }

def make_arrow(id, x, y, points, start_id=None, end_id=None,
               style="solid", color="#1e1e1e"):
    return {
        "id": id,
        "type": "arrow",
        "x": x, "y": y,
        "width": abs(points[-1][0] - points[0][0]),
        "height": abs(points[-1][1] - points[0][1]),
        "strokeColor": color,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "strokeStyle": style,
        "roughness": 1,
        "opacity": 100,
        "angle": 0,
        "seed": next_seed(),
        "version": 1,
        "isDeleted": False,
        "boundElements": [],
        "link": None,
        "locked": False,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "index": next_index(),
        "points": points,
        "startBinding": {
            "elementId": start_id, "focus": 0,
            "gap": 5, "fixedPoint": None
        } if start_id else None,
        "endBinding": {
            "elementId": end_id, "focus": 0,
            "gap": 5, "fixedPoint": None
        } if end_id else None,
        "startArrowhead": None,
        "endArrowhead": "arrow",
        "elbowed": False,
        "updated": int(time.time() * 1000),
        "versionNonce": next_seed(),
    }
```

## Verification

After generating the file, verify:
1. All text elements have `originalText` set (not missing).
2. No text elements have `height: null`.
3. All elements have `strokeStyle`, `frameId`, `roundness`, and `index`.
4. Container-bound text elements have matching `containerId` / `boundElements`.
5. The JSON is valid and parseable.

Run a verification script:
```python
import json
with open('docs/assets/architecture.excalidraw', 'r') as f:
    data = json.load(f)
errors = []
for el in data['elements']:
    if el['type'] == 'text':
        if 'originalText' not in el:
            errors.append(f"{el['id']}: missing originalText")
        if el.get('height') is None:
            errors.append(f"{el['id']}: height is null")
        if 'lineHeight' not in el:
            errors.append(f"{el['id']}: missing lineHeight")
    if 'strokeStyle' not in el:
        errors.append(f"{el['id']}: missing strokeStyle")
    if 'frameId' not in el:
        errors.append(f"{el['id']}: missing frameId")
    if 'index' not in el:
        errors.append(f"{el['id']}: missing index")
if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  {e}")
else:
    print(f"OK: {len(data['elements'])} elements, all valid")
```
