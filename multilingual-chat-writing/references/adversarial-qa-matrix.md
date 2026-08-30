# Adversarial QA matrix for mixed Persian chat rendering

Use this matrix after changing the Skill or investigating a reported visual
defect. Judge the rendered screenshot, not the Markdown source or DOM.

## Viewports and pass rule

Test at about 900 px, 360 px, and a boundary width that wraps immediately next
to the most sensitive LTR atom, at 100% zoom. Test light mode and, before a
public release, dark mode. A case passes only when semantic order is obvious to
a human reader, Persian remains RTL, each LTR atom remains internally LTR, and
changing width changes only wrapping—not reading order.

## M01 — Persian list containers

Use this exact raw Markdown as the negative-control fixture:

```markdown
- نتیجهٔ اول: نسخهٔ نصب‌شده با نسخهٔ مخزن کاری یکسان است.
- نتیجهٔ دوم: مراحل اعتبارسنجی
  1. تولید `DOCX` با `python-docx`
  2. رندر با `LibreOffice`
     - مقایسهٔ تصویری `page-1.png` در عرض باریک انجام می‌شود.
- وضعیت آزمون‌ها: نتیجه در `Runtime` فعلی قابل تأیید نیست.
```

Force narrow wrapping and record whether the host leaves any marker on the
left. The mitigation fixture must send the byte-for-byte same content through
the Skill. Unless the host's right-side markers have already been visually
verified, the Skill must convert it to separate Persian paragraphs with
visible labels. Emitting an unverified Markdown list is FAIL. If bullets were
explicitly required, every marker must render at the right of its own item and
nesting must progress from the right.

## M02 — Multiple LTR atoms and wrapping

Test this exact sentence without changing its words or punctuation:

```text
آزمون‌های فعلی طراحی مناسبی دارند، اما اجرا نشدند؛ زیرا python-docx، lxml و pytest در Runtime فعلی نصب نیستند.
```

The package names and `Runtime` must stay LTR and in their semantic positions;
`نصب نیستند.` must remain the sentence-final phrase at every width. The Persian
comma, conjunction, semicolon, and full stop must stay attached correctly.

## M03 — LTR atom before a Persian final verb

Test these exact sentences:

```text
این گزارش در Runtime فعلی اجرا نمی‌شود.
بنابراین فعلاً هیچ ادعایی دربارهٔ صحت کامل تولید یا رندر Word نمی‌کنم.
```

`Runtime` must stay between `در` and `فعلی`; `Word` must stay between `رندر`
and `نمی‌کنم`. Force wrapping next to both atoms. Any movement of the Persian
tail or final verb is FAIL.

## M04 — Inline code boundaries

Test a Persian paragraph containing `pytest -q`, `tests/test_rtl.py`,
`RTL_MODE=strict`, and `Runtime 3.12`. Slashes, equals signs, dots, spaces, and
atom order must remain exact. Inline-code backgrounds must not change the base
direction of the paragraph.

## M05 — Mixed heading

Test `نتیجهٔ آزمون RTL/LTR در Runtime فعلی` as a heading. Both LTR atoms must
remain exact and in place; heading weight and size must not alter reading order.

## M06 — Code block

Test one pure LTR code line followed by a Persian-dominant line containing
`Runtime`, `python-docx`, `lxml`, and `pytest`. The code line stays left-aligned.
The Persian line uses the `LRM + RLE/PDF + LRI/PDI` construction from
`rtl-rendering-patterns.md`; no control character may display visibly.

## M07 — URL, date, and filename

Test a URL containing `?lang=fa&mode=strict#tables`, Solar Hijri date
`۱۴۰۵/۰۶/۱۵`, and filename `daily-report-1405-06-15.pdf`. Each must keep its
exact internal order; adjacent Persian words and punctuation must not enter or
reorder it.

## M08 — Inline and block formulas

Test inline formula `f(x) = (x^2 + 1) / (2*x)` inside Persian prose. It must be
one internally LTR atom and adjacent Persian words must retain semantic order.
Separately test block formula `P(A|B) = P(B|A) * P(A) / P(B)` as an LTR,
left-aligned container. Operators, parentheses, and operands must remain exact
at normal and narrow widths; it is FAIL if the block becomes right-aligned or
is treated as an inline atom.

## M09 — Persian/mixed table

Test a table whose intended right-to-left display order is `ردیف`, `ابزار`,
`نتیجه`. Row numbers must be exactly under `ردیف`, tool names under `ابزار`,
and Persian statuses under `نتیجه`. Header/data alignment must match. Markdown
alone is not a pixel-accurate pass path; use the controlled visual workflow.

## M10 — Process and branch regression

Test the validated shared path and branches from `rtl-rendering-patterns.md`.
The first stage must be rightmost, completed branches must not have a trailing
arrow, and the insufficient-stock arrow must appear between `Out of Stock` and
`اطلاع‌رسانی به کاربر`.

The insufficient-stock line must read in semantic order as `بررسی موجودی`,
`ایجاد Out of Stock`, then `اطلاع‌رسانی به کاربر`; no arrow may trail the
completed line. Keep the canonical unquoted `Payment Service` source unchanged.
Separately test the exact quotation fixture `ارسال به “Payment Service” انجام
شد.`; it must display one opening and one closing quotation mark around the LTR
atom without changing the sentence's semantic order.

## M11 — LTR-leading Persian sentence

Test the exact sentence `URL باید یک واحد LTR باشد.` in ordinary prose and in a
left-aligned code block. The ordinary paragraph must use the validated
`RLM + LRI/PDI` pattern and read with `URL` first. The code block must remain
left-aligned while using `LRM + RLE/PDF + LRI/PDI`; semantic word order must be
identical. Also render the explanatory chain
`URL ← باید ← یک ← واحد ← LTR ← باشد` as an ordinary RTL paragraph whose first
item is rightmost.

## M12 — Combined container and wrapping regression

Start with a mixed heading, then supply a raw nested Markdown list containing
these two exact sentences with LTR terms represented as inline-code atoms:

```text
آزمون‌های فعلی طراحی مناسبی دارند، اما اجرا نشدند؛ زیرا python-docx، lxml و pytest در Runtime فعلی نصب نیستند.
بنابراین فعلاً هیچ ادعایی دربارهٔ صحت کامل تولید یا رندر Word نمی‌کنم.
```

Force a boundary wrap next to `Runtime` and `Word`. The Skill must output a
mixed heading plus labeled Persian paragraphs—not an unverified nested
Markdown list. Both sentences must preserve their exact logical wording and
punctuation at normal, narrow, and boundary widths.

## M13 — Cross-skill invocation boundary

Run a DOCX, code, data, and skill-development task whose visible progress and
final messages are Persian. This Skill must govern every visible message while
performing no file, artifact, or domain action. A primary-skill-only response
that emits a left-side Persian Markdown list is FAIL.

## Release decision

Have two independent reviewers inspect the normal, narrow, and boundary-width
screenshots. Any disagreement about reading order, marker position, nesting,
punctuation, or header/cell ownership is FAIL. Prefer a vertical labeled text
structure over a renderer-dependent construct whenever a case remains
ambiguous.
