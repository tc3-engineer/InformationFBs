# Tc2_Utilities content registry — part 2 (remaining 86 entries).
# Concise hand-curated Chinese content per 2026-05-11 charter.

from _tc2utilities_registry import REG


def _add(name, *, summary, behavior, pitfalls, scenario, value, alt,
         xml_scen, xml_val, xml_verify, var_desc=None,
         return_kind="NONE", related=None, xml_extra_vars=None,
         xml_call=None):
    REG[name] = dict(
        summary=summary, behavior=behavior, pitfalls=pitfalls,
        scenario=scenario, value=value, alt=alt,
        xml_scen=xml_scen, xml_val=xml_val, xml_verify=xml_verify,
        var_desc=var_desc or {}, return_kind=return_kind,
        related=related or [], xml_extra_vars=xml_extra_vars or [],
        xml_call=xml_call,
    )


# ============================================================================
# BCD / DEC converters
# ============================================================================

_add(
    "BCD_TO_DEC",
    summary=(
        "BCD_TO_DEC 把一个 BCD（Binary Coded Decimal）编码的字节转换为它对应的十进制 BYTE。"
        "BCD 编码常见于硬件拨码开关、老式 PLC 模块的状态寄存器、传统现场总线设备："
        "每 4 个二进制位代表 1 个十进制数字，例如 BCD `0x47` 实际表示十进制 47。\n\n"
        "本 FB 是个简单的纯计算包装，并不做合法性校验——如果输入字节里某 4 位 nibble 大于 9（非法 BCD），结果未定义。"
    ),
    behavior=(
        "**调用方式**：每次调用读 `BCDIN`，把高 4 位 × 10 + 低 4 位累加，结果赋给 `DECOUT`。无内部状态、无时序、不阻塞。\n\n"
        "**典型用例**：\n"
        "- BK 系列拨码开关：物理上 2 位拨码 → 1 个 BCD 字节 → 本 FB → 程序里的十进制工位编号。\n"
        "- 老式 DALI / KNX 设备的状态寄存器：1 个 BCD 字节读上来 → 本 FB 还原成可显示数字。\n\n"
        "**合法输入范围**：BCD `0x00..0x99`（高位 nibble 0..9，低位 nibble 0..9），输出 `0..99`。"
        "超出范围的字节（如 `0xAF`）结果未定义，PDF 没有承诺非法输入的行为，业务侧应自行校验。"
    ),
    pitfalls=[
        ("**不校验合法性**：输入 `0xAF` 会得到 `15 × 10 + 15 = 165`，可能掩盖现场总线数据帧错误。", False),
        ("**只接受 1 字节**：两位以上的 BCD 数字需要拆字节后多次调用，或换用更高位宽的转换辅助函数。", False),
        ("**不是位串到 BCD 的转换**：若现场数据是按位散落的（如某个 16 位寄存器里高 8 位是状态、低 8 位才是 BCD），需要先 `BAND` 取低字节再传入。", True),
        ("与 `DEC_TO_BCD` 不是恒等可逆对——后者只接受 0..99 输入；BCD_TO_DEC(DEC_TO_BCD(N)) 仅在 0..99 范围内等于 N。", True),
        ("PDF 未列错误码：错误输入只反映在输出值异常，不会有 `bError` 输出。", False),
    ],
    var_desc={
        "BCDIN": "输入字节，按 BCD 编码（高 4 位 = 十位数字 0..9；低 4 位 = 个位数字 0..9）。",
        "DECOUT": "对应的十进制值，范围 0..99（合法 BCD 输入下）。",
    },
    scenario="读 BK1120 拨码开关字节，把 BCD 编码的工位号还原成可显示的十进制数字。",
    value="把 PDF 文档里没明说的位运算（`SHR(b,4) * 10 + (b AND 16#0F)`）封装为一次调用，业务代码可读性更高，且不需要在维护代码里维护 BCD 位掩码常量。",
    alt=(
        "- 自写位运算：`SHR(BCD,4) * 10 + (BCD AND 16#0F)`，1 行能做，但每个地方都得重复且容易写错。\n"
        "- 用 `BYTE_TO_HEXSTR` 然后字符串转 INT：可行但慢且占代码。\n"
        "- **本 FB**：标准库提供，零依赖。"
    ),
    xml_scen="模拟从 IO 模块读到一个 BCD 字节 16#47（实际表示工位号 47），用本 FB 转成十进制 BYTE 显示给 HMI。",
    xml_val="替代手写 SHR/AND 位运算。",
    xml_verify="登录后在线改 bcdRawInput := 16#47，观察 decWorkstationNo 应为 47；改 16#99 应为 99；改 16#0F（非法 BCD）能看到结果异常值，提醒输入需校验。",
    xml_extra_vars=[
        ("bcdRawInput", "BYTE", "16#47", "模拟从 BK1120 拨码开关读到的 BCD 字节"),
        ("decWorkstationNo", "BYTE", None, "转换后的十进制工位编号 (0..99)"),
    ],
    xml_call=(
        "// 单次调用形式\n"
        "fbBCD_TO_DEC(BCDIN := bcdRawInput, DECOUT => decWorkstationNo);"
    ),
    related=["DEC_TO_BCD"],
)


_add(
    "DEC_TO_BCD",
    summary=(
        "DEC_TO_BCD 是 BCD_TO_DEC 的反向：把一个十进制 BYTE（0..99）编码为对应的 BCD 字节。"
        "用于把 PLC 内部的工位号、状态码写到老式 BCD 显示模块、拨码灯阵列等硬件输出端口。\n\n"
        "本 FB 也只接受单字节输入，对 ≥ 100 的值不做范围限制——超出 99 的输入会产生不再是有效 BCD 的字节。"
    ),
    behavior=(
        "**计算公式**：`BCDOUT := SHL(DECIN / 10, 4) OR (DECIN MOD 10)`。整数除法和模运算把十进制拆为十位与个位，再拼成 BCD。\n\n"
        "**合法输入范围**：0..99。输入 100..255 时结果仍然是个字节，但已经不是合法 BCD（高 nibble 会 ≥ A），具体值需要看公式得到的字节是否能被下游 BCD 显示模块识别。\n\n"
        "**无副作用、无时序、不阻塞**。可在任意上下文中调用。"
    ),
    pitfalls=[
        ("**不做范围校验**：输入 100 → 输出 `0x60`（看似合法 BCD 60），实际语义错乱。业务侧务必先 `LIMIT(0, val, 99)`。", False),
        ("BCD 数字不能直接送到普通显示器——硬件接口要明确是 BCD 类（如 7 段译码 IC、老式 BK 拨码 IO）才用。", True),
        ("与 BCD_TO_DEC 配对时只在 0..99 范围内可逆，否则可能不等。", True),
        ("PDF 未列错误码：错误只反映在输出字节异常，无 `bError`。", False),
        ("跨字节数值（≥ 100）应使用多次调用拆位发送或使用专门的多位 BCD 包，本 FB 不能处理。", False),
    ],
    var_desc={
        "DECIN": "输入十进制值（建议 0..99）。",
        "BCDOUT": "对应的 BCD 字节，高 nibble = 十位、低 nibble = 个位。",
    },
    scenario="把 PLC 内部计数器 0..99 编码为 BCD 字节，输出到老式 7 段译码板显示。",
    value="封装 `SHL(D/10,4) OR (D MOD 10)` 这段位运算，零依赖。",
    alt=(
        "- 自写表达式：`SHL(D/10,4) OR (D MOD 10)`，一行能做但易写错。\n"
        "- **本 FB**：标准库提供，含义自解释。"
    ),
    xml_scen="把工位号 0..99 编码为 BCD 字节，输出到老式 7 段显示模块。",
    xml_val="封装位运算，意图清晰。",
    xml_verify="改 decValue := 47，观察 bcdOutput 应为 16#47；改 99 应为 16#99；改 100 应为 16#60（脱离合法 BCD）。",
    xml_extra_vars=[
        ("decValue", "BYTE", "47", "PLC 内部十进制值"),
        ("bcdOutput", "BYTE", None, "送往 7 段译码模块的 BCD 字节"),
    ],
    xml_call=(
        "decValue := LIMIT(0, decValue, 99);  // 工程保护：超范围会得到非法 BCD\n"
        "fbDEC_TO_BCD(DECIN := decValue, BCDOUT => bcdOutput);"
    ),
    related=["BCD_TO_DEC"],
)
