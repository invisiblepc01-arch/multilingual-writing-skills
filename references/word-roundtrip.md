# Microsoft Word round-trip

Word is both the target renderer and a mutating editor. Updating fields or
saving through desktop Word can remove direct `w:rFonts`, `w:lang`, `w:rtl`, or
`w:bCs` properties even when the document still looks correct on that machine.

Use this order when Word fidelity is a release requirement:

1. Author the DOCX and run the paragraph-level bidi audit.
2. Open a working copy in the named Word version, update fields/TOC, repaginate,
   save, and close it.
3. Run `harden_docx_bidi.py` on Word's saved copy. After the current TOC has
   been generated and saved by Word, this release-hardening step locks the outer
   TOC field and every nested field in its result. That prevents verification
   from regenerating `_Toc...` bookmarks and reformatting current TOC pages.
4. Run both paragraph- and run-level audits on the hardened file. Add
   `--require-toc` or `--require-page-fields` only when those features are part
   of the document contract.
5. Reopen the hardened file read-only in Word and export once without updating
   fields. Record page count and visible TOC/PAGE/NUMPAGES results.
6. In a separate read-only Word session, update unlocked fields only in memory,
   skip the locked current TOC, repaginate, export again, and close without
   saving. The two renders must have
   identical page counts and field results. Rasterize both PDFs at the same DPI
   and require byte-identical page images; a differing page is a release failure,
   not a warning. If any comparison differs, save an updated working copy in
   Word, harden it, and repeat from step 3.
7. Inspect every page from the exact hardened deliverable. Check physical right
   alignment, Persian/Latin boundary spacing, table column identity/order, and
   attached hamza/ezafe glyphs; XML-only checks are insufficient.
8. If another Word save is necessary, repeat hardening and both audits.

Prefer Word 2024 when installed, otherwise use the newest available Word.
LibreOffice is allowed only after Word is confirmed unavailable or unable to
render the document; record that fallback explicitly.

Treat a repair prompt, page-count drift, field-result drift, missing field,
changed TOC leader,
unexpected blank page, font substitution, or run-audit failure as a release
failure. The final evidence must correspond to the exact DOCX delivered, not an
earlier working copy.
