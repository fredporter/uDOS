# uDOS No‑Travel Input --- Sticker Kit & Roadmap v0.1

*A universal, no‑travel, chorded input model using only regular
alphanumeric keys. Cross‑compatible with compact and extended keyboards
(arrow cluster + numpad). Includes printable ASCII sticker sheets and a
development roadmap. All diagrams are ASCII for portability.*

------------------------------------------------------------------------

## 0) TL;DR

-   **Hands stay put** on 3 tracked columns per hand; **Left pinkie =
    Fn**, **Right pinkie = Option**.
-   **Core symbols**: arrows **↑ ↓ ← →** and action buttons **□ △ ✕ ○**.
-   Lives entirely in the **alphanumeric block**; **no system keys
    required**.
-   On full‑size boards, **duplicate overlays** optionally cover the
    arrow cluster and numpad.

------------------------------------------------------------------------

## 1) Anchor Recap (Regular Keys Only)

-   **Left hand columns** anchored near: `3` (outer), `q` (mid), `c`
    (inner).\
-   **Right hand columns** anchored near: `u` (inner), `n` (mid), `0`
    (outer).\
-   **Pinkies**: `4` = **Fn** (left), `[` = **Option** (right).\
-   Any nearby physical key **snaps to nearest column** on that side
    (proximity rule). Middle + ring fingers operate as a single column
    per side.

```{=html}
<!-- -->
```
    Number row:  ...  [ 3 ]  [ 4/Fn ]                  ... [ U ] [ 0 ] [ [/Option ]
    Top row:     ...      [ Q ]                                  ...
    Home row:    ...                                   ...       [ N ]
    Bottom row:  ...      [ C ]                                  ...

------------------------------------------------------------------------

## 2) Base Navigation Cluster (Inside Alphanumeric Block)

                    △   (UP on U)
                    ↑
       □ (on 3)   ← (on Q)   → (on 0)   ○ (on [)
                    ↓
                   ✕   (DOWN on N)

-   **□** = STOP / BACK / UNDO
-   **○** = GO / ENTER / ACCEPT
-   **Arrows** = pure navigation.

> This cluster also **duplicates cleanly** onto extended keyboards
> (arrow block + numpad) --- see §5.

------------------------------------------------------------------------

## 3) Layers (No System Keys)

-   **Fn (hold `4`)** → alternative navigation using **regular keys**
    only.\
-   **Option (hold `[` )** → text‑editing combos (Shift/Control
    semantics) **emulated in software**, but still mapped to regular
    keys for legends.

### 3.1 Fn Layer (Left Pinkie held)

*Use as Page/Home navigation without using hardware system keys.*

      Fn+U  = PgUp (legend "PgUp")
      Fn+N  = PgDn (legend "PgDn")
      Fn+Q  = Home (legend "Home")
      Fn+0  = End  (legend "End")
      Fn+3  = Esc  (legend "Esc")
      Fn+[  = Tab  (legend "Tab")

### 3.2 Option Layer (Right Pinkie held)

*Text editing and selection shortcuts, expressed as legends on regular
keys.*

      Opt+U  = Shift+Up   (legend "Sh+Up")
      Opt+N  = Shift+Down (legend "Sh+Dn")
      Opt+Q  = Ctrl+Left  (legend "Ctl←")
      Opt+0  = Ctrl+Right (legend "Ctl→")
      Opt+3  = Undo       (legend "Undo")
      Opt+[  = Enter      (legend "Enter")

> **Note**: We are **not printing system keys** on caps; we only place
> textual legends (e.g., "Sh+Up") on regular keys. Implementation will
> generate the system chords.

------------------------------------------------------------------------

## 4) Printable Sticker Sheets (Monospace ASCII)

**Print tips:** - Use a monospace font (e.g., Menlo, Consolas, Monaco)
at 10--12 pt. - Print at 100% scale; test‑fit one box on a spare keycap
before printing the full sheet. - Two variants provided: **Unicode**
(with arrows) and **Pure ASCII** fallback.

### 4.1 Base Layer --- Unicode Sheet

    ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
    │  △  │ │  ✕  │ │  □  │ │  ○  │ │  ←  │ │  →  │ │  ↑  │ │  ↓  │
    └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘

    Placement (alphanumeric block):  U=△, N=✕, 3=□, [=○, Q=←, 0=→, (optional ↑/↓ duplicates unused in core block)

### 4.2 Fn Layer --- Unicode Sheet

    ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
    │PgUp │ │PgDn │ │Home │ │ End │ │ Esc │ │ Tab │
    └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘
     Legends: place on U, N, Q, 0, 3, [ respectively (used while holding Fn=4)

### 4.3 Option Layer --- Unicode Sheet

    ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
    │Sh+Up │ │Sh+Dn │ │Ctl←  │ │Ctl→  │ │Undo  │ │Enter │
    └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘
     Legends: place on U, N, Q, 0, 3, [ respectively (used while holding Option=[)

### 4.4 Pinkie Stickers (Optional)

    ┌──────┐   ┌────────┐
    │  Fn  │   │ Option │
    │  4   │   │   [    │
    └──────┘   └────────┘

### 4.5 Pure ASCII Fallback Sheets

*Base*

    +-----+ +-----+ +-----+ +-----+ +-----+ +-----+
    |  ^  | |  v  | |  [] | |  () | |  <  | |  >  |
    +-----+ +-----+ +-----+ +-----+ +-----+ +-----+
     ^=UP  v=DOWN  []=STOP  ()=GO  <=LEFT  >=RIGHT

*Fn*

    +-----+ +-----+ +-----+ +-----+ +-----+ +-----+
    |PgUp | |PgDn | |Home | | End | | Esc | | Tab |
    +-----+ +-----+ +-----+ +-----+ +-----+ +-----+

*Option*

    +------+ +------+ +------+ +------+ +------+ +------+
    |Sh+Up | |Sh+Dn | |Ctl<- | |Ctl-> | |Undo  | |Enter |
    +------+ +------+ +------+ +------+ +------+ +------+
