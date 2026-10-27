# Manual accessibility checklist (WCAG 2.2 AA)

Automated checks (`frontend/e2e/patient-flow.spec.ts` runs axe on the main flow) are
necessary but not sufficient. Run this checklist manually before release and after any
change to `frontend/app/analyzer.tsx` or `layout.tsx`. Record results in the table at
the bottom.

Scope: the critical patient flow — landing page → analyzer form → analysis result →
source evidence expansion. Target: WCAG 2.2 AA.

## 1. Keyboard-only traversal

- [ ] Unplug the mouse (or use Windows/macOS keyboard navigation). Complete a full
      analysis using only `Tab`, `Shift+Tab`, `Enter`, `Space`, `Esc`.
- [ ] Every interactive element is reachable in a logical order: disclosure button →
      report textarea → question textarea → reading-style select → both confirmation
      checkboxes → submit button → source-expansion buttons → "another analysis" reset.
- [ ] Focus is always visible (`:focus-visible` ring) on: links, textareas, select,
      checkboxes, submit button, source-expansion buttons. No focus is lost or
      trapped after results render or after an error appears.
- [ ] Skip-to-content link (if present) or first focusable element lands on real
      content, not the disclosure banner.
- [ ] With results on screen, `Tab` walks through each "View source" button; `Enter`
      or `Space` toggles it and focus stays on the button.

## 2. Zoom and reflow (WCAG 1.4.4, 1.4.10)

- [ ] 200% text zoom: no loss of content or functionality.
- [ ] 400% zoom (or 320px-wide viewport): page reflows to a single column with no
      horizontal scrolling; long evidence quotes wrap.
- [ ] "Report excerpt" counter, checkboxes, and buttons remain usable at 400%.

## 3. Contrast (WCAG 1.4.3, 1.4.11)

- [ ] Body text, labels, helper text (`text-slate-600`), and the amber/rose notice
      text on `bg-amber-50` / `bg-rose-50` all meet 4.5:1 (3:1 for large text).
- [ ] Submit button (`bg-emerald-900` + white) meets 4.5:1.
- [ ] Focus indicators are visible against every background used.
- [ ] Checkbox and radio affordances have 3:1 non-text contrast.

## 4. Screen reader (NVDA + Firefox on Windows, VoiceOver + Safari on macOS)

- [ ] Form controls announce name, role, and state: "Report excerpt, edit, multi-line",
      "Reading style, combobox", both checkboxes announce checked/unchecked.
- [ ] `aria-describedby` content is announced: character-count help and question help.
- [ ] While analyzing, the progress message (`role="status"`) is announced without
      stealing focus.
- [ ] Errors (`role="alert"`) are announced when they appear.
- [ ] Refusal messages (`role="status"`) are read as part of the result.
- [ ] Each source-expansion button announces its full label
      ("View source 1 for histology …"), and `aria-expanded` state changes are
      announced on toggle.
- [ ] Result section heading is reachable/announced via `aria-labelledby`.
- [ ] Reading order matches visual order (no orphaned or out-of-sequence content).

## 5. Content and semantics

- [ ] One `h1`; heading levels do not skip.
- [ ] All images/icons that convey meaning have accessible names; decorative ones are
      hidden from assistive tech.
- [ ] Language of page is declared (`lang="en"`).
- [ ] Status is never conveyed by color alone (refusal, error, verification state
      include text labels).
- [ ] Error messages are specific and adjacent to the invalid control (or programmatically
      associated).

## 6. Motion and timing (WCAG 2.3.3, 2.2.1)

- [ ] No auto-playing animation; `prefers-reduced-motion` disables non-essential
      transitions.
- [ ] No user-controlled time limit on the form; the request may take long but the
      page never times out the user's input.

## 7. Pointer / touch

- [ ] Interactive targets are at least 24x24 CSS px (checkbox rows use `min-h-11`,
      submit uses `min-h-12`).
- [ ] Usable at 320px width and with touch (no hover-only functionality).

## Run log

| Date | Tester | Browser / AT | Result | Notes |
|---|---|---|---|---|
| | | | | |
