# F_IOPortRead

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `I/O port access` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31026059.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_IOPortRead.TcPOU`](../examples/P_Demo_F_IOPortRead.TcPOU) |

---

## 1. 功能简述

F_IOPortRead 直接读取 PC 内一个 I/O 端口（不是工业 IO 模块，是 x86 主板 I/O 总线上的端口地址）。适用于直接控制 PC 主板硬件（如蜂鸣器、并口、串口寄存器），是与硬件低层打交道的桥梁。`eSize` 指定读取宽度（1 / 2 / 4 字节）；返回值是读到的 32 位无符号整数。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nAddr : UDINT;
    eSize : E_IOAccessSize;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nAddr` | `UDINT` | I/O 端口地址（16 位 I/O 空间，如 `16#378` LPT、`16#61` 蜂鉣器）。 |
| `eSize` | `E_IOAccessSize` | 读取宽度枚举（`IOAS_BYTE` / `IOAS_WORD` / `IOAS_DWORD`），决定读 1 / 2 / 4 字节。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：同步函数，立刻返回读到的值。

**端口宽度 `eSize`**：`E_IOAccessSize` 枚举，常用值 `IOAS_BYTE`（1 字节）、`IOAS_WORD`（2 字节）、`IOAS_DWORD`（4 字节）。读 1 字节时高位字节为 0。

**端口地址**：典型值是 LPT 端口 `0x378`、串口寄存器 `0x3F8`、PC 蜂鉣器 `0x61` 等 16 位 I/O 空间地址。读地址不会破坏硬件，但写地址（`F_IOPortWrite`）可能损坏，PDF NOTICE 警告。

**只在 PC / IPC 上有效**：CX 之类的嵌入式控制器可能没有标准的 x86 I/O 端口空间，调用此函数行为未定义。

## 4. 错误码 / 返回值

本函数返回 `DWORD`：读到的端口值，高位未读字节为 0（如读 1 字节时高 24 位 = 0）。

## 5. 使用注意 / 常见坑

- **端口地址必须正确**：错误的端口地址可能读到不相关硬件状态或 0xFF；查 PC 主板手册或设备 datasheet 确认。
- **`eSize` 不当**：用 `IOAS_DWORD` 读 8 位端口可能跨端口读取，结果不可靠。匹配硬件实际宽度。
- **实时性影响**：直接 I/O 端口操作绕过 OS，可能阻塞 PLC 任务调度；高频调用慎用。（工程经验补充）
- **Embedded PC / Arm 平台**：CX Arm 系列没有 x86 风格 I/O 端口空间，本函数无意义。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_IOPortRead.TcPOU`](../examples/P_Demo_F_IOPortRead.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：读取 LPT 并口当前输入状态做硬件诊断；或读 PC 主板 GPIO 寄存器查询机柜门开关。
- **价值**：替代 OS 级 DDK 调用 / 写驱动；PLC 一行代码直读硬件端口。
- **替代方案对比**：
  - 写 Windows 驱动 `inp` / `outp`：能用但要内核态权限。
  - TwinCAT IO Driver（标准 EtherCAT 终端）：现代工程首选，避免直接端口操作。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31026059.html
- **相关 FB / FC**：`F_IOPortWrite`, `LPTSIGNAL`
