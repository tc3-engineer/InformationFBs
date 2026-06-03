"""Hand-written Chinese narrative for each Tc2_EtherCAT FB/FC.

Schema per entry:
    NARRATIVE["<Name>"] = {
        "summary": str,        # §1 功能简述
        "descs":   dict[str, str],   # variable -> Chinese description
        "behavior": str,       # §3 行为说明 (≥ 80 CJK chars after bullets stripped)
        "errors":   str,       # §4 错误码 / 返回值
        "caveats":  str,       # §5 使用注意 / 常见坑
        "scenario": str,       # §7 业务场景与实际价值
        "refs":     str,       # §8 相关 FB / FC 横向链接
    }

    EXAMPLE_VARS["<Name>"] = {
        "header": str,   # ST CDATA 顶部三件套注释（场景/价值/验证步骤）
        "decl":   str,   # PROGRAM VAR ... END_VAR 内部声明区
        "body":   str,   # <Implementation>/<ST> CDATA body
    }
"""

NARRATIVE = {}
EXAMPLE_VARS = {}
