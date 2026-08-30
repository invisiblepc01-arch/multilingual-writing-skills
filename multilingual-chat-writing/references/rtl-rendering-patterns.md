# RTL rendering patterns for ChatGPT and Codex

Read only for direction-sensitive mixed Persian/English output. The names below
refer to Unicode controls; insert the actual code points, not their names.

## Control characters

- `LRM` — U+200E LEFT-TO-RIGHT MARK: keeps an auto-directed LTR container or
  code line anchored to the left.
- `RLM` — U+200F RIGHT-TO-LEFT MARK: gives an ordinary mixed paragraph an RTL
  anchor when it must begin with an English atom.
- `RLE` — U+202B RIGHT-TO-LEFT EMBEDDING and `PDF` — U+202C POP DIRECTIONAL
  FORMATTING: embed one Persian sentence inside an LTR code block.
- `LRI` — U+2066 LEFT-TO-RIGHT ISOLATE and `PDI` — U+2069 POP DIRECTIONAL
  ISOLATE: preserve an English atom inside Persian text.
- `RLI` — U+2067 RIGHT-TO-LEFT ISOLATE with `PDI`: isolate a Persian token
  inside an explicitly LTR diagnostic line.

Never use `RLO` or `LRO`; overrides can reverse characters rather than merely
set paragraph direction.

## Exact mixed sentence in ordinary prose

For the logical sentence `URL باید یک واحد LTR باشد.`:

```text
RLM + LRI + URL + PDI + " باید یک واحد " + LRI + LTR + PDI + " باشد."
```

Keep it in an ordinary paragraph. If adding a visible anchor is acceptable,
`قاعدهٔ اول: URL باید یک واحد LTR باشد.` is more portable.

## Persian sentence in a left-aligned code block

Use this logical construction:

```text
LRM + RLE + LRI + URL + PDI + " باید یک واحد " + LRI + LTR + PDI + " باشد." + PDF
```

The outer `LRM` preserves the left position of an auto-directed code line; the
embedded sentence still reads RTL. Pure URLs, commands, formulas, and source
code do not need the Persian embedding.

## Arrow chains

For an RTL Persian explanation, use an ordinary paragraph whose semantic order
is first to last:

```text
URL ← باید ← یک ← واحد ← LTR ← باشد
```

The first item must render at the right. Isolate `URL` and `LTR` with
`LRI`/`PDI`. Do not put this explanatory chain in an LTR code block merely for
styling; doing so moves the first item to the left.

For a completed process branch, omit a trailing arrow:

```text
بررسی موجودی ← ایجاد Out of Stock ← اطلاع‌رسانی به کاربر
```

For a real decision, keep the shared path separate and label every branch:

```text
ثبت سفارش ← ارسال به Order Service ← بررسی موجودی ←

موجودی کافی: بررسی موجودی ← رزرو کالا ← ارسال به Payment Service

موجودی ناکافی: بررسی موجودی ← ایجاد Out of Stock ← اطلاع‌رسانی به کاربر
```

If both branches later merge, name the merge stage explicitly on both branch
lines or add `ادغام مسیرها: ...`. For a retry, write the return action in words
while retaining `←`; never reverse the arrow to depict the loop.

## Markdown lists

Avoid Markdown bullets when the host places Persian list content in a
left-aligned list container. Use separate paragraphs:

```text
قاعدهٔ اول: ...

قاعدهٔ دوم: ...
```

This visible Persian anchor is more portable than invisible controls.

## Persian and mixed tables

For a five-column Persian table, the intended display order is:

```text
شمارهٔ ردیف | مرحله | وضعیت فارسی | وضعیت انگلیسی | خروجی
```

If Markdown is used, source order may need to be the reverse. Markdown alone
does not guarantee that `th` and `td` share alignment in every host. For exact
alignment, create a controlled render with:

- table direction `rtl`;
- fixed column order and widths;
- identical alignment for every header/data pair;
- isolated `ltr` spans for English values;
- screenshot inspection before delivery.

Do not paste the controlling HTML into chat when the host escapes HTML. Display
the verified image and provide a copyable vertical text alternative if needed.

## Visual QA

Check the actual ChatGPT/Codex rendering whenever the user reports a visual
defect. Compare screenshots at normal zoom. Treat source order, paragraph
direction, container alignment, and LTR atom isolation as separate variables;
change only the variable demonstrated to be wrong.
