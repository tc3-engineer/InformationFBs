# InfoSys topic URL map for the 61 numeric helpers covered by the
# 2026-05-12 Tc2_Utilities rewrite (uint64 + int64_signed + fix16 + float + lcomplex).
# Each entry is verified against the per-category index pages of
# https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/

BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities"

URLS = {
    # 64 bit integer functions (unsigned) — 31 entries
    "LREAL_TO_UINT64":   "35197323",
    "LWORD_TO_ULARGE":   "934116875",
    "STRING_TO_UINT64":  "35198859",
    "UInt32x32To64":     "35168139",
    "UINT64_TO_LREAL":   "35200395",
    "UINT64_TO_STRING":  "35201931",
    "UInt64Add64":       "35163531",
    "UInt64Add64Ex":     "35165067",
    "UInt64And":         "35178891",
    "UInt64Cmp64":       "35177355",
    "UInt64Div16Ex":     "934153483",
    "UInt64Div64":       "35172747",
    "UInt64Div64Ex":     "35174283",
    "UInt64isZero":      "35195787",
    "UInt64Limit":       "35188107",
    "UInt64Max":         "35186571",
    "UInt64Min":         "35185035",
    "UInt64Mod64":       "35175819",
    "UInt64Mul64":       "35169675",
    "UInt64Mul64Ex":     "35171211",
    "UInt64Not":         "35183499",
    "UInt64Or":          "35180427",
    "UInt64Rol":         "35192715",
    "UInt64Ror":         "35194251",
    "UInt64Shl":         "35189643",
    "UInt64Shr":         "35191179",
    "UInt64Sub64":       "35166603",
    "UInt64Xor":         "35181963",
    "ULARGE_INTEGER":    "35161995",
    "ULARGE_TO_ULINT":   "934157323",
    "ULARGE_TO_LWORD":   "934155403",

    # 64 bit functions (signed) — 15 entries
    "INT64_TO_LREAL":    "35220235",
    "Int64Add64":        "35206411",
    "Int64Add64Ex":      "35207947",
    "Int64Cmp64":        "35212555",
    "Int64Div64Ex":      "35211019",
    "Int64IsZero":       "35217163",
    "Int64Negate":       "35215627",
    "Int64Not":          "35214091",
    "Int64Sub64":        "35209483",
    "LARGE_INTEGER":     "35204875",
    "LARGE_TO_LINT":     "934103435",
    "LARGE_TO_ULARGE":   "35223307",
    "LINT_TO_LARGE":     "934107275",
    "LREAL_TO_INT64":    "35218699",
    "ULARGE_TO_LARGE":   "35221771",

    # 16 bit fixed point number functions (signed) — 9 entries
    "FIX16_TO_LREAL":    "35227787",
    "FIX16_TO_WORD":     "35230859",
    "FIX16Add":          "35232395",
    "FIX16Align":        "35233931",
    "FIX16Div":          "35235467",
    "FIX16Mul":          "35237003",
    "FIX16Sub":          "35238539",
    "LREAL_TO_FIX16":    "35226251",
    "WORD_TO_FIX16":     "35229323",

    # FLOAT functions — 4 entries
    "LrealIsFinite":     "2570925451",
    "LrealIsNaN":        "2572585227",
    "RealIsFinite":      "11506278283",
    "RealIsNaN":         "11506311563",

    # LCOMPLEX functions — 2 entries
    "LcomplexIsNaN":     "2572609163",
    "LcomplexAbs":       "3535240971",
}


def url_for(name):
    tid = URLS.get(name)
    if tid is None:
        return None
    return f"{BASE}/{tid}.html"
