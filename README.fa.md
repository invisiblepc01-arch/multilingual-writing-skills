# ساخت فایل‌های DOCX فارسی و انگلیسی

[English README](README.md) · [راهنمای نصب فارسی](INSTALLATION.fa.md) ·
[English installation guide](INSTALLATION.md)

`build-bilingual-docx` یک Skill متن‌باز برای تولید، اصلاح و کنترل فایل‌های
Microsoft Word شامل متن فارسی راست‌به‌چپ، انگلیسی چپ‌به‌راست و محتوای ترکیبی
است.

## قابلیت‌ها

- تثبیت جهت RTL پاراگراف‌های فارسی؛
- حفظ جهت LTR عبارت‌های انگلیسی، کدها، URLها و مسیرها؛
- اصلاح تیترهای شماره‌دار فارسی؛
- اصلاح فهرست‌های شماره‌ای و گلوله‌ای RTL؛
- قواعد تخصصی فهرست مطالب فارسی؛
- کنترل هدر، فوتر، جدول و Story Partهای مستقل Word؛
- ممیزی مستقیم OOXML؛
- تولید سند آزمایشی دوزبانه؛
- کنترل سازگاری با Word 2016 تا Word 2024.

## نصب سریع

مخزن را Clone یا به‌صورت ZIP دریافت و استخراج کنید. پوشه نهایی را در مسیر شخصی
Skills قرار دهید:

```text
Windows:
C:\Users\<USER>\.agents\skills\build-bilingual-docx

macOS/Linux:
$HOME/.agents/skills/build-bilingual-docx
```

فایل زیر باید مستقیماً وجود داشته باشد:

```text
build-bilingual-docx/SKILL.md
```

اگر Skill نمایش داده نشد، Codex را کاملاً ببندید و دوباره اجرا کنید. راهنمای
کامل در [INSTALLATION.fa.md](INSTALLATION.fa.md) قرار دارد.

## استفاده

فراخوانی صریح:

```text
$build-bilingual-docx
از این متن یک فایل Word فارسی استاندارد با تیترهای شماره‌دار، فهرست مطالب RTL
و هدر راست‌چین بساز.
```

فراخوانی ضمنی نیز به‌صورت پیش‌فرض فعال است؛ بنابراین درخواست عادی تولید یا
اصلاح DOCX فارسی باید این Skill را فعال کند.

## ابزارهای همراه

نصب وابستگی‌ها:

```powershell
python -m pip install -r requirements.txt
```

ساخت سند آزمایشی:

```powershell
python scripts\make_bidi_fixture.py fixture_raw.docx
```

اصلاح جهت‌ها:

```powershell
python scripts\harden_docx_bidi.py fixture_raw.docx fixture_hardened.docx --mode auto
```

ممیزی:

```powershell
python scripts\audit_docx_bidi.py fixture_hardened.docx --json fixture_audit.json
```

نتیجه مطلوب شامل `"passed": true` و آرایه خالی `errors` است.

## محدودیت مهم

ممیزی XML جایگزین کنترل تصویری نیست. فقط زمانی می‌توان خروجی را
«کنترل‌شده در Word 2024» نامید که نسخه نهایی واقعاً با Word 2024 باز یا رندر
شده و همه صفحات آن بررسی شده باشند.

## مشارکت

Issue و Pull Request پذیرفته می‌شود. برای گزارش خطا، نسخه Word، سیستم‌عامل،
فونت‌های نصب‌شده و یک نمونه غیرمحرمانه ارائه کنید.

## مجوز

این پروژه با مجوز MIT منتشر شده است.
