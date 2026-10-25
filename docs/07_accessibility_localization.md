# 07 — Accessibility and localization

## Target
Aim for WCAG 2.2 AA in the critical patient flow. Automated axe checks are necessary but not certification; pair them with manual keyboard, screen-reader and zoom checks.

## UI requirements
Semantic landmarks and heading order; labels/instructions; keyboard-only operation; visible focus; no traps; polite live announcements for loading/result/error; large readable text; contrast; reflow at 200–400%; no color-only meaning; clear action labels; mobile touch targets; reduced-motion respect; clear generic errors. Do not re-announce full report text.

## Evidence interaction
Claim selection exposes exact cited words in a visibly labeled region (“Source excerpt from your report”), keyboard-accessible and adjacent to claim. Multiple citations all navigable. Do not rely on color highlight alone. Test offsets/quotes across Tamil/Devanagari combining marks, line endings, Unicode normalization, and non-BMP characters; Python and JS string indices differ.

## Language commitment
Target concept languages: English, Tamil, Hindi, Spanish. Support means complete UI, safety/refusal strings, evidence labels, result generation, PDFs where offered, and review—not a locale dropdown. Keep quotation in source language and identify it separately from translated explanation. Preserve negation, numbers, biomarkers and uncertainty.

## Three-day policy
Ship English plus one other language only if a fluent reviewer can review safety and meaning. Otherwise ship English-only and explicitly call others planned/unvalidated. Do not present machine translation as medically validated.

## Typography and reading level
Noto Sans Tamil/Devanagari needs real browser/PDF tests for shaping, wrapping, embedding and licensing. Disable a locale/card if glyph output breaks. “Simple/standard/detailed” is not a grade guarantee. textstat is English-centric; do not use it as a Tamil/Hindi/Spanish score.
