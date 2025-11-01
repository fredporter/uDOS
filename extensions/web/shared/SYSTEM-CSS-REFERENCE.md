# system.css Quick Reference for uDOS

Quick guide for using system.css components in uDOS web extensions.

## CDN Link

```html
<link rel="stylesheet" href="../shared/system.css">
```

## Basic Window Structure

```html
<div class="window">
  <!-- Title Bar -->
  <div class="title-bar">
    <button aria-label="Close" class="close"></button>
    <h1 class="title">Window Title</h1>
    <button aria-label="Resize" class="resize"></button>
  </div>

  <!-- Separator Line -->
  <div class="separator"></div>

  <!-- Details/Status Bar (optional) -->
  <div class="details-bar">
    <span>Left info</span>
    <span>Right info</span>
  </div>
  <div class="separator"></div>

  <!-- Main Content -->
  <div class="window-pane">
    Your content here
  </div>
</div>
```

## Buttons

```html
<!-- Standard Button -->
<button class="btn">Click Me</button>

<!-- Default Button (with darker border) -->
<button class="btn-default">Default Action</button>

<!-- Disabled Button -->
<button class="btn" disabled>Disabled</button>

<!-- Button in active/pressed state (CSS only, for demos) -->
<button class="btn" style="background: #000; color: #fff;">Active</button>
```

## Form Elements

### Text Input
```html
<input type="text" placeholder="Enter text">
<input type="email" placeholder="Email">
<input type="password" placeholder="Password">
```

### Select Dropdown
```html
<select>
  <option>Option 1</option>
  <option>Option 2</option>
  <option>Option 3</option>
</select>
```

### Checkboxes
```html
<input type="checkbox" id="check1">
<label for="check1">Option 1</label>

<input type="checkbox" id="check2" checked>
<label for="check2">Option 2 (checked)</label>
```

### Radio Buttons
```html
<input type="radio" id="radio1" name="group1">
<label for="radio1">Choice 1</label>

<input type="radio" id="radio2" name="group1" checked>
<label for="radio2">Choice 2 (selected)</label>
```

### Field Rows
```html
<div class="field-row">
  <label for="input1">Label:</label>
  <input type="text" id="input1">
</div>

<div class="field-row">
  <label for="input2">Another:</label>
  <input type="text" id="input2">
</div>
```

## Dialogs

### Standard Dialog
```html
<div class="standard-dialog">
  <h2>Dialog Title</h2>
  <p>Dialog content goes here.</p>
  <button class="btn">OK</button>
</div>
```

### Modeless Dialog
```html
<div class="modeless-dialog">
  <section class="field-row">
    <label for="find">Find:</label>
    <input id="find" type="text">
  </section>
  <section class="field-row" style="justify-content: flex-end">
    <button class="btn">Cancel</button>
    <button class="btn">Find</button>
  </section>
</div>
```

### Modal Dialog (Double Border)
```html
<div class="outer-border">
  <div class="inner-border">
    <div class="modal-dialog">
      <h2>Modal Title</h2>
      <div class="modal-contents">
        <p>Modal content</p>
      </div>
      <section class="field-row" style="justify-content: flex-end">
        <button class="btn">Cancel</button>
        <button class="btn-default">OK</button>
      </section>
    </div>
  </div>
</div>
```

### Alert Box
```html
<div class="outer-border">
  <div class="inner-border">
    <div class="alert-box">
      <div class="alert-contents">
        <p>This is an alert message.</p>
      </div>
      <section class="field-row" style="justify-content: flex-end">
        <button class="btn">OK</button>
      </section>
    </div>
  </div>
</div>
```

## Menu Bar

```html
<ul role="menu-bar">
  <li role="menu-item">
    File
    <ul role="menu">
      <li role="menu-item"><button>New</button></li>
      <li role="menu-item"><button>Open</button></li>
      <li role="menu-item" class="divider"></li>
      <li role="menu-item"><button>Save</button></li>
    </ul>
  </li>
  <li role="menu-item">
    Edit
    <ul role="menu">
      <li role="menu-item"><button>Copy</button></li>
      <li role="menu-item"><button>Paste</button></li>
    </ul>
  </li>
  <li role="menu-item" aria-haspopup="false">
    <a href="#">Help</a>
  </li>
</ul>
```

## Typography

### Fonts
- **Chicago_12** - Title bars, headings, UI labels (14-18px)
- **Monaco** - Monospace for code (12-14px)
- **Geneva_9** - Small UI text (9-11px)

### Headings
```html
<h1>Chicago font, 1em</h1>
<h2>Chicago font, 2em</h2>
```

## Colors

system.css is **monochrome only**:
- Background: `#ffffff` (white)
- Foreground: `#000000` (black)
- Shading: Bitmap patterns (no grays)

Active/selected states invert (white on black).

## Custom Styling Tips

### Overriding Defaults
```css
/* Keep system.css rules, add your own */
.window {
  max-width: 1200px;
  margin: 20px auto;
}

.window-pane {
  max-height: 80vh;
  overflow-y: auto;
}
```

### Adding Borders
```css
.my-section {
  border: 1.5px solid #000;
  padding: 10px;
  background: #fff;
}
```

### Spacing
```css
.field-row + .field-row {
  margin-top: 6px;
}

.btn {
  margin-right: 5px;
}
```

## Common Patterns

### Sidebar Layout
```html
<div class="window-pane">
  <div style="display: flex; gap: 20px;">
    <aside style="min-width: 250px;">
      <!-- Sidebar content -->
    </aside>
    <main style="flex: 1;">
      <!-- Main content -->
    </main>
  </div>
</div>
```

### Status Footer
```html
<div class="separator"></div>
<div class="details-bar" style="font-size: 11px;">
  <kbd>Ctrl+S</kbd> Save • <kbd>Ctrl+O</kbd> Open
</div>
```

### Sections with Headers
```html
<div style="border: 1.5px solid #000; padding: 10px; margin-bottom: 15px;">
  <h3 style="margin: 0 0 10px 0; font-family: Chicago_12; font-size: 14px;">
    Section Title
  </h3>
  <p>Content here</p>
</div>
```

## Accessibility

- Use `aria-label` on close/resize buttons
- Use `aria-haspopup` on menu items
- Ensure proper focus states
- Maintain keyboard navigation

## Browser Notes

- **Scrollbars:** Custom bitmap scrollbars work in Chrome/Edge only
- **Font Loading:** May take moment to load Chicago/Monaco fonts
- **Monochrome:** Some browsers may apply default link colors (override as needed)

## Resources

- **Documentation:** https://sakofchit.github.io/system.css/
- **GitHub:** https://github.com/sakofchit/system.css
- **CDN:** https://unpkg.com/@sakun/system.css

---

*This reference is part of the uDOS v1.3 documentation.*
