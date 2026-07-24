# راهنمای نصب و انتقال Skill تخصصی تولید DOCX فارسی و انگلیسی

این راهنما نحوه دریافت و نصب Skill روی رایانه‌ای دیگر را توضیح می‌دهد:

```text
build-bilingual-docx-skill.zip
```

نام Skill پس از نصب:

```text
build-bilingual-docx
```

این Skill برای ساخت، اصلاح و کنترل فایل‌های Microsoft Word با متن فارسی
راست‌به‌چپ، انگلیسی چپ‌به‌راست و متن‌های ترکیبی طراحی شده است.

---

## ۱. پیش‌نیازها

برای استفاده کامل از Skill، رایانه مقصد بهتر است موارد زیر را داشته باشد:

1. برنامه ChatGPT Desktop/Codex، Codex CLI یا افزونه Codex برای محیط توسعه؛
2. دسترسی کاربر به پوشه شخصی خود؛
3. Python نسخه 3.10 یا جدیدتر برای اجرای اسکریپت‌های همراه Skill؛
4. بسته‌های Python زیر:

```text
python-docx
lxml
```

5. Microsoft Word 2016 یا جدیدتر، ترجیحاً Word 2024، برای کنترل نهایی نمایش؛
6. فونت‌های فارسی مورد استفاده در سند، مانند B Nazanin، B Titr یا فونت انتخابی
   سازمان.

نبود Python مانع خواندن دستورکار `SKILL.md` نمی‌شود، اما اسکریپت‌های اصلاح و
ممیزی خودکار اجرا نخواهند شد.

---

## ۲. دریافت پروژه

می‌توانید مخزن را از GitHub به‌صورت ZIP دانلود کنید یا آن را Clone کنید:

```text
git clone https://github.com/invisiblepc01-arch/build-bilingual-docx.git
```

در روش ZIP، از صفحه مخزن گزینه **Code → Download ZIP** را انتخاب و فایل را
استخراج کنید. نام ZIP و مقدار SHA-256 بسته به Commit یا Release تغییر می‌کند؛
برای کنترل اصالت، فایل را فقط از صفحه رسمی همین مخزن دریافت کنید.

---

## ۳. ساختار صحیح پس از استخراج

فایل ZIP را Extract کنید. نتیجه باید دقیقاً یک پوشه به نام زیر باشد:

```text
build-bilingual-docx
```

درون آن باید حداقل این ساختار وجود داشته باشد:

```text
build-bilingual-docx/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── ooxml-bidi.md
│   ├── portability.md
│   ├── qa-matrix.md
│   └── toc-and-numbering.md
└── scripts/
    ├── audit_docx_bidi.py
    ├── harden_docx_bidi.py
    └── make_bidi_fixture.py
```

خطای متداول، ایجاد یک پوشه اضافی است:

```text
build-bilingual-docx/build-bilingual-docx/SKILL.md
```

این ساختار مناسب نیست. فایل `SKILL.md` باید مستقیماً در پوشه اصلی Skill باشد.

---

## ۴. نصب روی Windows برای استفاده شخصی در Codex

### روش پیشنهادی مطابق ساختار جدید Codex

پوشه شخصی Skills را بسازید:

```text
C:\Users\<USER-NAME>\.agents\skills
```

سپس کل پوشه `build-bilingual-docx` را در آن کپی کنید. مسیر نهایی باید این باشد:

```text
C:\Users\<USER-NAME>\.agents\skills\build-bilingual-docx\SKILL.md
```

روش PowerShell:

```powershell
$source = "C:\Path\build-bilingual-docx"
$destinationRoot = Join-Path $env:USERPROFILE ".agents\skills"
New-Item -ItemType Directory -Force -Path $destinationRoot | Out-Null
Copy-Item -LiteralPath $source -Destination $destinationRoot -Recurse
```

### مسیر سازگار با بعضی نسخه‌های Codex Desktop

اگر برنامه شما Skill را از مسیر بالا شناسایی نکرد، مسیر زیر را نیز امتحان کنید:

```text
C:\Users\<USER-NAME>\.codex\skills\build-bilingual-docx\SKILL.md
```

روش PowerShell:

```powershell
$source = "C:\Path\build-bilingual-docx"
$destinationRoot = Join-Path $env:USERPROFILE ".codex\skills"
New-Item -ItemType Directory -Force -Path $destinationRoot | Out-Null
Copy-Item -LiteralPath $source -Destination $destinationRoot -Recurse
```

از نصب هم‌زمان دو نسخه با نام یکسان در `.agents\skills` و `.codex\skills`
خودداری کنید؛ وجود دو نسخه می‌تواند باعث نمایش Skill تکراری یا استفاده از نسخه
نامشخص شود.

---

## ۵. نصب روی macOS یا Linux

فایل ZIP را استخراج کنید و پوشه Skill را در مسیر شخصی زیر قرار دهید:

```text
$HOME/.agents/skills/build-bilingual-docx/SKILL.md
```

نمونه فرمان:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R "/path/to/build-bilingual-docx" "$HOME/.agents/skills/"
```

برای نسخه‌هایی که هنوز از مسیر قدیمی Codex استفاده می‌کنند، مسیر جایگزین:

```text
$HOME/.codex/skills/build-bilingual-docx/SKILL.md
```

فقط یکی از دو مسیر را انتخاب کنید.

---

## ۶. راه‌اندازی مجدد و شناسایی Skill

پس از کپی:

1. تمام پنجره‌های ChatGPT Desktop/Codex را ببندید؛
2. در Task Manager یا Activity Monitor مطمئن شوید برنامه کاملاً بسته شده است؛
3. برنامه را دوباره اجرا کنید؛
4. یک Task جدید باز کنید؛
5. در ChatGPT Desktop بخش **Skills** را از نوار کناری بررسی کنید؛
6. در Codex CLI یا افزونه IDE، فرمان `/skills` را اجرا کنید یا علامت `$` را
   تایپ کنید.

باید نام زیر دیده شود:

```text
build-bilingual-docx
```

نام نمایشی ممکن است چنین باشد:

```text
Persian and English DOCX Engineering
```

Codex تغییرات Skill را معمولاً خودکار تشخیص می‌دهد؛ اگر ظاهر نشد، برنامه را
مجدداً راه‌اندازی کنید.

---

## ۷. آزمایش فراخوانی صریح

برای نخستین آزمایش، Skill را صریح فراخوانی کنید:

```text
$build-bilingual-docx
از متن فارسی پیوست‌شده یک فایل DOCX استاندارد با تیترهای شماره‌دار، فهرست مطالب،
هدر راست‌چین و کنترل کامل RTL بساز.
```

در ChatGPT Desktop ممکن است بتوانید با `@` نیز Skill را از فهرست انتخاب کنید.

پس از اطمینان از نصب، درخواست عادی زیر نیز باید Skill را به‌صورت ضمنی فعال کند:

```text
از این متن یک فایل Word فارسی استاندارد بساز.
```

فراخوانی ضمنی بر اساس بخش `description` در ابتدای `SKILL.md` انجام می‌شود.

---

## ۸. کنترل نصب با آزمون همراه Skill

در Terminal یا PowerShell وارد پوشه Skill شوید.

### ساخت سند آزمایشی

```powershell
python ".\scripts\make_bidi_fixture.py" ".\fixture_raw.docx"
```

### اصلاح و تثبیت RTL/LTR

```powershell
python ".\scripts\harden_docx_bidi.py" `
  ".\fixture_raw.docx" `
  ".\fixture_hardened.docx" `
  --mode auto
```

### ممیزی نهایی

```powershell
python ".\scripts\audit_docx_bidi.py" `
  ".\fixture_hardened.docx" `
  --json ".\fixture_audit.json"
```

نتیجه مطلوب:

```json
{
  "passed": true,
  "errors": []
}
```

سپس `fixture_hardened.docx` را در Microsoft Word باز کنید و موارد زیر را
بررسی کنید:

- تیتر و شماره آن در سمت راست باشد؛
- متن فارسی RTL و راست‌چین باشد؛
- عبارت‌های انگلیسی وارونه نشده باشند؛
- شماره‌های فهرست در سمت راست قرار گرفته باشند؛
- هدر فارسی از سمت راست نمایش داده شود؛
- جدول و فوتر به‌درستی نمایش داده شوند.

---

## ۹. نصب کتابخانه‌های Python

اگر خطای `ModuleNotFoundError` دریافت شد:

```powershell
python -m pip install python-docx lxml
```

در macOS/Linux:

```bash
python3 -m pip install python-docx lxml
```

در رایانه سازمانی ممکن است نصب بسته نیازمند مجوز مدیر سیستم یا استفاده از
محیط مجازی باشد:

```powershell
python -m venv ".venv"
.\.venv\Scripts\Activate.ps1
python -m pip install python-docx lxml
```

---

## ۱۰. رفع خطاهای متداول

### Skill در فهرست دیده نمی‌شود

1. وجود مستقیم فایل `SKILL.md` را بررسی کنید؛
2. پوشه اضافی تو در تو را حذف کنید؛
3. نام پوشه را `build-bilingual-docx` نگه دارید؛
4. برنامه را کاملاً ببندید و باز کنید؛
5. مسیر `.agents\skills` و در صورت نیاز مسیر سازگار `.codex\skills` را کنترل
   کنید؛
6. بررسی کنید Skill در `config.toml` غیرفعال نشده باشد.

### Skill دوبار دیده می‌شود

دو نسخه هم‌نام در مسیرهای مختلف نصب شده‌اند. یکی را نگه دارید و دیگری را از
مسیر Skills خارج کنید؛ سپس Codex را دوباره اجرا کنید.

### Skill فقط با `$build-bilingual-docx` اجرا می‌شود

فایل زیر را باز کنید:

```text
agents/openai.yaml
```

اگر این مقدار وجود داشت:

```yaml
policy:
  allow_implicit_invocation: false
```

آن را به `true` تغییر دهید یا بخش `policy` را حذف کنید. مقدار پیش‌فرض فراخوانی
ضمنی `true` است.

### فایل Word هنوز در رایانه مقصد متفاوت نمایش داده می‌شود

این مشکل معمولاً از نصب نبودن فونت، نسخه متفاوت Word، تنظیمات زبان Office،
به‌روزرسانی فهرست مطالب یا جایگزینی خودکار فونت ایجاد می‌شود. فونت‌ها را نصب
کنید و سند نهایی را در همان نسخه Word مقصد کنترل کنید.

---

## ۱۱. استفاده در سایر موتورهای AI

این Skill بر مبنای ساختار باز Agent Skills ساخته شده است. برای موتور AI دیگری
که نصب مستقیم Skill را پشتیبانی نمی‌کند:

1. ZIP را استخراج کنید؛
2. فایل `SKILL.md` را به‌عنوان دستورکار دائمی یا System/Project Instruction
   بارگذاری کنید؛
3. پوشه‌های `references` و `scripts` را در اختیار Agent قرار دهید؛
4. به Agent اجازه خواندن فایل‌ها و اجرای Python بدهید؛
5. از Agent بخواهید قبل از تولید DOCX، `SKILL.md` و مرجع مرتبط را بخواند؛
6. اسکریپت ممیزی را پس از تولید اجرا کند؛
7. خروجی را در Microsoft Word مقصد باز و کنترل بصری کند.

موتوری که امکان اجرای فایل، خواندن منابع یا مشاهده خروجی Word ندارد، نمی‌تواند
به‌طور معتبر صحت کامل فایل DOCX را تضمین کند.

---

## ۱۲. به‌روزرسانی Skill در آینده

برای جایگزینی نسخه قدیمی:

1. از پوشه نصب‌شده نسخه پشتیبان بگیرید؛
2. Codex را ببندید؛
3. پوشه قدیمی `build-bilingual-docx` را با پوشه جدید جایگزین کنید؛
4. از ایجاد پوشه تو در تو جلوگیری کنید؛
5. Codex را اجرا و آزمون بخش ۸ را تکرار کنید.

هیچ‌گاه پوشه جدید را روی نسخه قدیمی Merge نکنید، مگر اینکه دقیقاً بدانید کدام
فایل‌ها باید حفظ شوند؛ فایل‌های قدیمی اضافی می‌توانند رفتار Skill را مبهم کنند.

---

## ۱۳. حذف یا غیرفعال‌کردن

برای حذف، Codex را ببندید و پوشه زیر را از محل نصب خارج کنید:

```text
build-bilingual-docx
```

برای غیرفعال‌کردن بدون حذف، در فایل زیر:

```text
~/.codex/config.toml
```

این تنظیم را اضافه کنید:

```toml
[[skills.config]]
path = "/full/path/to/build-bilingual-docx/SKILL.md"
enabled = false
```

پس از تغییر `config.toml`، Codex را راه‌اندازی مجدد کنید.

---

## ۱۴. منبع رسمی

راهنمای رسمی ساختار، محل بارگذاری، فراخوانی صریح/ضمنی و راه‌اندازی مجدد Skills:

```text
https://learn.chatgpt.com/docs/build-skills
```

توجه: Skill محلی به‌طور تضمینی از طریق حساب OpenAI میان همه رایانه‌ها همگام
نمی‌شود. روی هر رایانه باید پوشه Skill یک‌بار نصب شود، مگر اینکه Skill در قالب
Plugin قابل‌نصب منتشر شده باشد.
