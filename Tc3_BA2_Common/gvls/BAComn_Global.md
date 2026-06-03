# BAComn_Global

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `GVL` |
| Category | `GVLs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/14592850571.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_BAComn_Global.TcPOU`](../examples/P_Demo_BAComn_Global.TcPOU) |

---

## 1. 功能简述

BA2_Common 库的全局常量集合。包含基本数据类型的最小/最大值（如 `nMinByte / nMaxByte / nMinInt / nMaxInt / tMinTime / tMaxTime / tMaxDATE`）、I/O 原始值常量（0V / 1V / 2V / 5V / 10V 对应的 INT 原始数）、时间换算常量（秒-毫秒、分-秒等）、字符常量（数字 0-9 的 ASCII、加号、减号、小数点）、ADS 常量（loopback NetID、符号分隔符）以及避免除零的小数常量 `fCloseToZero`。所有常量都标 `qualified_only`，使用时必须用 `BAComn_Global.<name>` 访问。

## 2. 接口定义

### VAR_GLOBAL

```iecst
VAR_GLOBAL CONSTANT
// Datatype Ranges:
 {warning disable C0196}
     nMinByte               : BYTE   := 16#00;
     nMaxByte               : BYTE   := 16#FF;
     nMinInt                : INT    := 16#8000;
     nMaxInt                : INT    := 16#7FFF;
     nMinUInt               : UINT   := 16#0000;


     nMaxUInt               : UINT   := 16#FFFF;
     nMinDInt               : DINT   := 16#80000000;
     nMaxDInt               : DINT   := 16#7FFFFFFF;
     nMinUDInt              : UDINT  := 16#00000000;
     nMaxUDInt              : UDINT  := 16#FFFFFFFF;
     fMinReal               : REAL   := -3.402823E+38;
     fMaxReal               : REAL   := 3.402823E+38;
     tMinTime               : TIME   := TO_TIME(0);
     tMaxTime               : TIME   := TO_TIME(16#FFFFFFFF);
     tMinTOD                : TOD    := TO_TOD(0);
     tMaxTOD                : TOD    := TO_TOD(16#FFFFFFFF);
     tMinDATE               : DATE   := TO_DATE(0);
     tMaxDATE               : DATE   := TO_DATE(16#FFFFFFFF);
     tMinDT                 : DT     := TO_DT(0);
     tMaxDT                 : DT     := TO_DT(16#FFFFFFFF);
 {warning restore C0196}
// I/O:
     nIO_RawMin             : INT     := 0;
     nIO_RawMax             : INT     := nMaxInt;
     nIO_Raw0V              : INT     := 0;                 // Raw value for 0V
     nIO_Raw1V              : INT     := (nIO_RawMax / 10); // Raw value for 1V
     nIO_Raw2V              : INT     := (nIO_Raw1V * 2);   // Raw value for 2V
     nIO_Raw3V              : INT     := (nIO_Raw1V * 3);   // Raw value for 3V
     nIO_Raw5V              : INT     := (nIO_Raw1V * 5);   // Raw value for 5V
     nIO_Raw10V             : INT     := (nIO_Raw1V * 10);  // Raw value for 10V
END_VAR
// General:
VAR_GLOBAL CONSTANT
 {region 'Time'}
     nMilli2Sek             : UINT    := 1000;
     nSek2Min               : UINT    := 60;
     nMin2Hour              : UINT    := 60;
     n24Hour2Hour           : UDINT   := (24 * 60 * 60);
     n24Hour2Milli          : UDINT   := n24Hour2Hour * 1000;
     udiMaxSecInMilli       : UDINT   := (nMaxUDInt / nMilli2Sek);     // Max. capable value (in [s]
) in a UDINT
     udiMaxMinInMilli       : UDINT   := (udiMaxSecInMilli / nSek2Min);// Max. capable value (in [m]
) in a UDINT
 {endregion}
 {region 'Characters'}
     bChar_0                : BYTE    := 16#30;
     bChar_1                : BYTE    := 16#31;
     bChar_2                : BYTE    := 16#32;
     bChar_3                : BYTE    := 16#33;
     bChar_4                : BYTE    := 16#34;
     bChar_5                : BYTE    := 16#35;
     bChar_6                : BYTE    := 16#36;
     bChar_7                : BYTE    := 16#37;
     bChar_8                : BYTE    := 16#38;
     bChar_9                : BYTE    := 16#39;
     bChar_Plus             : BYTE    := 16#2B;
     bChar_Minus            : BYTE    := 16#2D;
     bChar_Dot              : BYTE    := 16#2E;
 {endregion}
 {region 'Type'}
     fCloseToZero           : REAL   := 0.00001;   // Comparison value to prevent a division by zero
 {endregion}
 {region 'ADS'}
     tAmsNetID_Loopback     : T_AmsNetIdArr   := [ 127,0,0,1,1,1 ];
     sSymbolSeparator       : STRING(1)       := '.';
 {endregion}
END_VAR
```

⚠️ 这是 GVL（全局常量集合）。本表给出代表性条目；完整定义见 PDF 原文。


## 3. 行为说明

BA2_Common 库的全局常量集合。包含基本数据类型的最小/最大值（如 `nMinByte / nMaxByte / nMinInt / nMaxInt / tMinTime / tMaxTime / tMaxDATE`）、I/O 原始值常量（0V / 1V / 2V / 5V / 10V 对应的 INT 原始数）、时间换算常量（秒-毫秒、分-秒等）、字符常量（数字 0-9 的 ASCII、加号、减号、小数点）、ADS 常量（loopback NetID、符号分隔符）以及避免除零的小数常量 `fCloseToZero`。所有常量都标 `qualified_only`，使用时必须用 `BAComn_Global.<name>` 访问。 本 GVL 是 *只读全局常量* 集合：所有字段在 PLC 启动时已初始化为定值，运行时不允许写入（编译器静态强制）。可被任意 POU 通过 `GVL 名.字段名` 访问。 典型工程场景：在自定义 BA FB 中需要"24 小时换算成秒数"时直接用 `BAComn_Global.n24Hour2Hour`，避免到处写 `24 * 60 * 60` 散落各处。

## 4. 错误码 / 返回值

本 GVL 无返回值（全局常量集合）。

本条目无 `bError` / `nErrId` 输出（全局常量），不存在运行时错误。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BAComn_Global.TcPOU`](../examples/P_Demo_BAComn_Global.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：在自定义 BA FB 中需要"24 小时换算成秒数"时直接用 `BAComn_Global.n24Hour2Hour`，避免到处写 `24 * 60 * 60` 散落各处。
- **价值**：集中管理避免硬编码魔数；常量统一命名便于 IDE 搜索。
- **替代方案对比**：到处散落 `60 * 60 * 24` 等硬编码（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/14592850571.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
