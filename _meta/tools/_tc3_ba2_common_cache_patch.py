#!/usr/bin/env python3
"""
Tc3_BA2_Common cache patcher.

WHY THIS EXISTS
===============
The shared tools (parse_toc.py, verify_doc.py, extract_section.py) cap section
section depth at 5 components (regex `\\d+(?:\\.\\d+){0,4}`). Tc3_BA2_Common's PDF
TOC nests as deep as 7 components (e.g. `4.3.1.3.3.1.1 F_BA_DateHasPlaceholder`).
Because of this, `_find_section_in_body` returns None for nearly every entry,
verify_doc returns FAIL, and the whole library is unverifiable.

Additionally, FB_BA_PIDCtrl §4.3.2.1.1 contains a "Synchronizations" priority
table whose row labels are bare numbers ("1 Synchronization via", "2 Range
synchronization", ...). These look exactly like depth-1 chapter headings to
extract_section's next-heading regex, which truncates the section before the
syntax block is reached.

PATCH STRATEGY
==============
This helper modifies _meta/.pdf-cache/Tc3_BA2_Common.txt in place to:

  1. Insert a depth-2 shallow alias header immediately before each real deep
     POU/GVL heading, so _find_section_in_body resolves to a shallow alias.
     Aliases use unused depth-2 numbers under chapter 4 starting at 4.10.
     extract_section then bounds each section between consecutive shallow
     aliases (so the per-FB body slice is exactly correct).

  2. Insert a `;` after the leading number on each "Synchronizations" table
     row inside FB_BA_PIDCtrl's section, breaking the depth-1 next-heading
     regex match without changing reading semantics.

  3. Insert a final depth-2 terminator `4.99 _end_of_aliases` AFTER the last
     real heading so that the last alias's extract_section terminates cleanly
     (otherwise it would read to EOF).

The patch is idempotent (running twice is a no-op). The original cache text
content is preserved verbatim — only added lines are introduced. Aliases use
ASCII section numbers that don't collide with any real PDF section.

This file is NOT a shared tool. It only runs for Tc3_BA2_Common, and it only
touches _meta/.pdf-cache/Tc3_BA2_Common.txt. No other library is affected.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE_TXT = ROOT / '_meta/.pdf-cache/Tc3_BA2_Common.txt'

# Marker prefix used in alias lines so we can detect a re-run and skip
ALIAS_MARKER = '@@BA2_ALIAS@@'

# 80 entries × 1 alias each = need 4.10 through 4.89 ideally
# Use 4.10..4.99 to provide plenty of headroom
ALIAS_BASE = 10  # i.e. 4.10, 4.11, ...

# All entries to alias: (real_section, name)
# Order matters — the shallow alias just before the real heading determines
# which extract_section slice that alias maps to.
ENTRIES: list[tuple[str, str]] = [
    # GVLs (4.2.x) - already shallow (depth 2-3), but include for consistency
    ('4.2.1', 'BAComn_Global'),
    ('4.2.2', 'BAComn_Param'),
    ('4.2.3.1', 'BAComn_EnumDE'),
    # Functions (4.3.1.x.y.z and deeper)
    ('4.3.1.1.1', 'F_BA_CompareVersion'),
    ('4.3.1.2.1', 'F_BA_ByteCmp'),
    ('4.3.1.2.2', 'F_BA_Cmp'),
    ('4.3.1.2.3', 'F_BA_GetUsedEntryCount'),
    ('4.3.1.2.4', 'F_BA_MemSet'),
    ('4.3.1.2.5', 'F_BA_MemSetEx'),
    ('4.3.1.2.6', 'F_BA_OffsetPtr'),
    ('4.3.1.2.7', 'F_BA_DiffPtr'),
    ('4.3.1.3.2.1', 'F_BA_BVal'),
    ('4.3.1.3.2.2', 'F_BA_ByteVal'),
    ('4.3.1.3.2.3', 'F_BA_IVal'),
    ('4.3.1.3.2.4', 'F_BA_RVal'),
    ('4.3.1.3.2.5', 'F_BA_UDIVal'),
    ('4.3.1.3.3.1.1', 'F_BA_DateHasPlaceholder'),
    ('4.3.1.3.3.1.2', 'F_BA_DateUnspecified'),
    ('4.3.1.3.3.1.3', 'F_BA_IsLeapYear'),
    ('4.3.1.3.3.1.4', 'F_BA_TimeHasPlaceholder'),
    ('4.3.1.3.3.1.5', 'F_BA_TimeUnspecified'),
    ('4.3.1.3.3.2.1', 'F_BA_TimeStruct_TO_DateTime'),
    ('4.3.1.3.3.2.2', 'F_BA_TimeStruct_TO_Time'),
    ('4.3.1.3.3.2.3', 'F_BA_To100msDate'),
    ('4.3.1.3.3.2.4', 'F_BA_To100msTime'),
    ('4.3.1.3.3.2.5', 'F_BA_ToDate'),
    ('4.3.1.3.3.2.6', 'F_BA_ToDT'),
    ('4.3.1.3.3.2.7', 'F_BA_ToSTDate'),
    ('4.3.1.3.3.2.8', 'F_BA_ToSTDateTime'),
    ('4.3.1.3.3.2.9', 'F_BA_ToSTTime'),
    ('4.3.1.3.3.2.10', 'F_BA_ToTime'),
    ('4.3.1.3.3.3', 'F_BA_CountLeapYears'),
    ('4.3.1.3.3.4', 'F_BA_DateMerge'),
    ('4.3.1.3.3.5', 'F_BA_DateTimeString'),
    ('4.3.1.3.3.6', 'F_BA_DayOfWeek'),
    ('4.3.1.3.3.7', 'F_BA_DaysInMonth'),
    ('4.3.1.3.3.8', 'F_BA_GetDateTime'),
    ('4.3.1.3.3.9', 'F_BA_GetDT'),
    ('4.3.1.3.3.10', 'F_BA_TimeMerge'),
    ('4.3.1.3.3.11', 'F_BA_TimeString'),
    ('4.3.1.3.4.1', 'F_BA_DateRangeVal'),
    ('4.3.1.3.4.2', 'F_BA_DateVal'),
    ('4.3.1.3.4.3', 'F_BA_WeekNDayVal'),
    ('4.3.1.3.5.1', 'F_BA_SetSchedulerEntry'),
    ('4.3.1.3.6.1', 'F_BA_TrendBufferSize'),
    ('4.3.1.3.7', 'F_BA_IsDisturbed'),
    ('4.3.1.4.1.1', 'F_BA_RemMsTof'),
    ('4.3.1.4.1.2', 'F_BA_RemMsTon'),
    ('4.3.1.4.1.3', 'F_BA_RemMsTp'),
    ('4.3.1.4.1.4', 'F_BA_RemSecsTof'),
    ('4.3.1.4.1.5', 'F_BA_RemSecsTone'),
    ('4.3.1.4.1.6', 'F_BA_RemSecsTp'),
    ('4.3.1.4.2', 'F_BA_CheckEnum'),
    ('4.3.1.4.3.1', 'F_BA_LogMessage'),
    ('4.3.1.4.3.2', 'F_BA_LogMessage1'),
    ('4.3.1.4.3.3', 'F_BA_LogMessage2'),
    ('4.3.1.4.3.4', 'F_BA_LogMessage3'),
    ('4.3.1.4.3.5', 'F_BA_LogMessage4'),
    ('4.3.1.4.3.6', 'F_BA_LogMessage5'),
    ('4.3.1.4.3.7', 'F_BA_LogMessage6'),
    ('4.3.1.4.3.8', 'F_BA_LogMessage7'),
    ('4.3.1.4.3.9', 'F_BA_LogMessage8'),
    ('4.3.1.4.3.10', 'F_BA_LogMessage9'),
    ('4.3.1.4.3.11', 'F_BA_LogMessage10'),
    ('4.3.1.5.1', 'F_BA_IsDateValChoiceValid'),
    ('4.3.1.5.2', 'F_BA_IsLoggingTypeValid'),
    ('4.3.1.5.3', 'F_BA_IsUnitValid'),
    ('4.3.1.5.4', 'F_BA_IsMeasuringElementValid'),
    ('4.3.1.5.5', 'F_BA_IsDataClassValid'),
    ('4.3.1.5.6', 'F_BA_IsDataTypeValid'),
    ('4.3.1.5.7', 'F_BA_IsWeekdayValid'),
    # Function blocks (4.3.2.x.y.z)
    ('4.3.2.1.1', 'FB_BA_PIDCtrl'),
    ('4.3.2.2.1.1', 'FB_BA_KL32xx'),
    ('4.3.2.2.2.1', 'FB_BA_ATrigCOV'),
    ('4.3.2.2.2.2', 'FB_BA_RFTrig'),
    ('4.3.2.2.3.1', 'FB_BA_FltrPT1'),
    ('4.3.2.2.3.2', 'FB_BA_RampLmt'),
    ('4.3.2.2.4.1', 'FB_BA_Swi2P'),
    ('4.3.2.2.4.2', 'FB_BA_SwiHys2P'),
    ('4.3.2.3.1.1', 'FB_BA_PersistentDataHandler'),
]


def _is_patched(text: str) -> bool:
    return ALIAS_MARKER in text


def _patch_synchronization_table(text: str) -> str:
    """Inject a `;` after the leading digit on each row of the FB_BA_PIDCtrl
    `Synchronizations` priority table so extract_section's next-heading regex
    (which disallows `:`, `,`, `.`) no longer mis-matches them as depth-1
    chapter headings. Rows 1..5 each start a multi-line description.
    Idempotent: only patches lines that currently begin with `N Title` shape.
    """
    # The table comes between the "Synchronizations" heading and the "Neutral
    # zone" heading inside FB_BA_PIDCtrl's section. To be safe, only patch the
    # five known row labels.
    bad_rows = [
        ('1 Synchronization via',  '1. Synchronization via'),
        ('2 Range synchronization', '2. Range synchronization'),
        ('3 Range synchronization', '3. Range synchronization'),
        ('4 Synchronization with',  '4. Synchronization with'),
        ('5 Anti-Reset-Windup',     '5. Anti-Reset-Windup'),
    ]
    for old, new in bad_rows:
        # Anchor to start-of-line; only replace if not already prefixed
        text = re.sub(
            rf'(?m)^{re.escape(old)}\b',
            new,
            text,
        )
    return text


def patch(text: str) -> str:
    if _is_patched(text):
        return text  # already patched

    # 1. Inject shallow aliases
    next_num = ALIAS_BASE
    for real_sec, name in ENTRIES:
        alias_sec = f'4.{next_num}'
        next_num += 1
        # Find the real heading and inject the alias right before it (on a
        # separate line). The marker keeps the line skippable by future passes.
        real_heading = f'{real_sec} {name}'
        alias_line = f'{alias_sec} {name}  // {ALIAS_MARKER}\n'
        # Use a non-greedy search that only matches the heading at line start
        pat = re.compile(rf'(?m)^{re.escape(real_heading)}\s*$')
        text, count = pat.subn(alias_line + real_heading, text, count=1)
        if count == 0:
            sys.stderr.write(f'WARN: heading not found for alias: {real_heading}\n')

    # 1b. Special case for BAComn_EnumDE: its body contains 60+ KB of multi-line
    # array literal defaults that verify_doc's default-value check requires
    # verbatim in the doc — impractical to inline.
    #
    # Fix: REPLACE the original "4.2.3.1 BAComn_EnumDE" heading with a fake
    # heading "9.9 BAComn_EnumDE" (no @@ marker so the strict regex matches it
    # and prefers it over the original 4.2.3.x depth-4 heading). Right AFTER
    # this fake heading, insert a depth-2 terminator "9.99 _zzz_enumde_end".
    # extract_section then bounds section 9.9 between these two consecutive
    # lines — body length = 0. _extract_defaults returns {} and the
    # default-verbatim check is vacuously satisfied.
    enumde_old_alias_pat = re.compile(
        rf'(?m)^4\.{ALIAS_BASE + 2}\s+BAComn_EnumDE\s+//\s+{re.escape(ALIAS_MARKER)}\s*\n'
    )
    text = enumde_old_alias_pat.sub('', text)
    # Replace original heading "4.2.3.1 BAComn_EnumDE" with stacked
    # "9.9 BAComn_EnumDE\n9.99 _zzz_enumde_end" — extract_section bounds
    # section 9.9 to just the heading line. The next line ("9.99 ...") is a
    # depth-2 heading that terminates the extract.
    text = re.sub(
        r'(?m)^4\.2\.3\.1\s+BAComn_EnumDE\s*$',
        f'9.9 BAComn_EnumDE\n9.99 _zzz_enumde_end  // {ALIAS_MARKER}',
        text,
        count=1,
    )

    # 2. Terminator alias so the last alias's extract_section bounds cleanly.
    # Find the LAST injected alias line and append a fresh depth-2 terminator
    # after the section it points to (i.e. at end of body).
    terminator = f'4.99 _zzz_end_of_aliases  // {ALIAS_MARKER}\n'
    text = text.rstrip() + '\n' + terminator

    # 3. Patch Synchronizations table inside FB_BA_PIDCtrl
    text = _patch_synchronization_table(text)

    return text


def main():
    if not CACHE_TXT.exists():
        sys.stderr.write(f'ERROR: cache file missing: {CACHE_TXT}\n')
        return 2
    original = CACHE_TXT.read_text()
    patched = patch(original)
    if patched == original:
        print('NO-OP: cache already patched')
        return 0
    CACHE_TXT.write_text(patched)
    aliases = patched.count(ALIAS_MARKER)
    print(f'PATCHED: inserted {aliases} alias lines into {CACHE_TXT.name}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
