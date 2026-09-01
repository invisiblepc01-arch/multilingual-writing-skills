# Microsoft Word round-trip

Word is both the target renderer and a mutating editor. Updating fields or
saving through desktop Word can remove direct `w:rFonts`, `w:lang`, `w:rtl`, or
`w:bCs` properties even when the document still looks correct on that machine.

Use this order when Word fidelity is a release requirement:

1. Author the DOCX and run the paragraph-level bidi audit.
2. Open a working copy in the named Word version, update fields/TOC, repaginate,
   save, and close it.
3. Run `harden_docx_bidi.py` on Word's saved copy.
4. Run both paragraph- and run-level audits on the hardened file. Add
   `--require-toc` or `--require-page-fields` only when those features are part
   of the document contract.
5. Reopen the hardened file read-only in Word. Do not save it again. Export PDF
   from that read-only session and inspect every page.
6. If another Word save is necessary, repeat hardening and both audits.

Treat a repair prompt, page-count drift, missing field, changed TOC leader,
unexpected blank page, font substitution, or run-audit failure as a release
failure. The final evidence must correspond to the exact DOCX delivered, not an
earlier working copy.
