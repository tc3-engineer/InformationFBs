# F_CheckSum16

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35109899.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CheckSum16.xml`](../examples/P_Demo_F_CheckSum16.xml) |

---

## 1. 功能简述

对任意长度的数据缓冲计算 16 位累加和（checksum）。比 CRC-16 简单（仅做字节累加），通常用于"不严格但便宜"的完整性快检——例如配方文件版本指纹、retain 数据快照比对，或一些 vendor 自定义协议把 checksum 当帧尾校验。

支持把上一次结果作为 `wChkSum` 入参继续累积，所以可以分段计算（比如配方分多个 4KB 块读出，逐块累加得到整体 checksum）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    dwSrcAddr  : POINTER TO BYTE;
    cbLen      : UDINT;
    wChkSum    : WORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `dwSrcAddr` | `POINTER TO BYTE` | — | 数据缓冲起始地址（`ADR()`）。 |
| `cbLen` | `UDINT` | — | 数据长度（字节，`SIZEOF()`）。 |
| `wChkSum` | `WORD` | — | 初值 = 0 或上一次的 checksum；连续分段计算时把上次返回值传进来。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `WORD` | 16 位累加和；后续段可作为下次 `wChkSum` 入参。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数从 `dwSrcAddr` 起，按字节累加到 `wChkSum`，溢出截断到 16 位（即 mod 65536）。处理完 `cbLen` 字节后返回新的累加和。

特性：
- **不带多项式 / 位移**：和 CRC 不同，纯加法，强度低但快。
- **可分段累加**：每段开始时把上次返回值当 `wChkSum` 入参传入；整体结果等价于一次性算整个 buffer。
- **初值**：通常 `0`；某些协议规定其他初值，按协议给。
- **不区分大小端**：按字节累加，与字节序无关。

典型用法：
```iecst
wSum := F_CheckSum16(ADR(arData1), SIZEOF(arData1), 0);
wSum := F_CheckSum16(ADR(arData2), SIZEOF(arData2), wSum);  // 接着累加第二段
```

注意：checksum 强度远低于 CRC——交换两个字节顺序、内容相同时 checksum 不变（CRC 会变）。涉及完整性安全要求高的场合（消息篡改检测）必须用 `F_DATA_TO_CRC16_CCITT`。

## 4. 错误码 / 返回值

返回 `WORD`，无错误码。`cbLen = 0` 时直接返回入参 `wChkSum`（什么都没加）。

## 5. 使用注意 / 常见坑

- **强度远低于 CRC**：相同字节集（不同顺序）checksum 相同；要严格校验用 CRC。
- **初值非零的协议要核对**：默认 0 不一定满足所有 vendor 规范，看协议。
- **分段累加要把上次结果传回去**：忘记传 → 每段从 0 重算 → 最终是最后一段的 checksum。
- **大端协议 vs 小端 PLC**：本函数按字节累加，结果不受 PLC 字节序影响；但若协议规定 checksum 字段在帧尾是大端存放，PLC 这边要 `SWAP` 一下再写帧（工程经验补充）。
- **不要用作密码学完整性**：可被恶意修改（已知 checksum 后可构造碰撞字节）；只用于无敌意环境下的简单检错。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CheckSum16.xml`](../examples/P_Demo_F_CheckSum16.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_CheckSum16
VAR
    arRetain : ARRAY[0..15] OF BYTE;
    wSum     : WORD;
END_VAR

wSum := F_CheckSum16(dwSrcAddr := ADR(arRetain), cbLen := SIZEOF(arRetain), wChkSum := 0);
```

## 7. 业务场景与实际价值

- **场景**：每个 PLC 周期对一组 retain 变量算 checksum 写入诊断区，HMI 周期性比对——若 checksum 不变说明用户没动过这组变量。
- **价值**：手写 FOR 循环要 5 行 + 易写 16 位溢出错；本函数一行调用，性能稳定。
- **替代方案对比**：
  - 手写 `FOR i: wSum := wSum + arData[i];`：工作但每次写一遍易遗漏
  - CRC：更安全但更慢；对快速指纹有点过度
  - 本函数：单调用、O(N) 时间

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.31 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35109899.html
- **相关函数**：`F_BYTE_TO_CRC16_CCITT`（单字节 CRC）、`F_DATA_TO_CRC16_CCITT`（整段 CRC，更安全）
