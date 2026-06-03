# FB_DALIV2AddressingRandomAddressing

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_DALI` |
| Library Version | `2.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `Part 102 / Addressing (High-Level)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/index.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_DALIV2AddressingRandomAddressing.TcPOU`](../examples/P_Demo_FB_DALIV2AddressingRandomAddressing.TcPOU) |

---

## 1. 功能简述

**DALI 控制设备随机寻址（high-level）**——本 FB 是 DALI 寻址流程的完整封装。把所有未寻址（即短地址为 MASK）的镇流器按内部随机算法分配短地址（顺序 / 自定义起点）。整个流程几分钟到十几分钟（取决于灯数），过程中 PLC 可观察 `nAddressedDevices` 实时累加。**比 `FB_DALIV2AddressingIntRandomAddressing` 更慢，但提供过程反馈和提前终止能力。**

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart                 : BOOL;
    bCancel                : BOOL;
    nStartWithShortAddress : BYTE  := 0;
    nOptions               : DWORD := DALIV2_OPTION_OPTICAL_FEEDBACK;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 上升沿启动寻址流程 |
| `bCancel` | `BOOL` | — | ⚠️ 待人工确认 |
| `nStartWithShortAddress` | `BYTE` | `0` | 第一盏灯的短地址（其它灯依次递增） |
| `nOptions` | `DWORD` | `DALIV2_OPTION_OPTICAL_FEEDBACK` | 选项位（按 OR 组合 `DALIV2_OPTION_*` 常量）：全新寻址 / 删除原组归属 / 删除原场景 / 视觉反馈 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy                 : BOOL;
    bError                : BOOL;
    nErrorId              : UDINT;
    nCurrentSearchAddress : UDINT;
    arrAddressedDevices   : ARRAY [0..63] OF BOOL;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 寻址流程进行中 |
| `bError` | `BOOL` | 寻址出错 |
| `nErrorId` | `UDINT` | 错误号 |
| `nCurrentSearchAddress` | `UDINT` | ⚠️ 待人工确认 |
| `arrAddressedDevices` | `ARRAY [0..63] OF BOOL` | ⚠️ 待人工确认 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stCommandBuffer : ST_DALIV2CommandBuffer;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stCommandBuffer` | `ST_DALIV2CommandBuffer` | DALI 命令缓冲区结构；连到对应 KL68x1 通信 FB 的同名变量 |


## 3. 行为说明

**整体流程**：本 FB 内部调一系列低层 DALI 命令完成 IEC 62386 Part 102 章节 11.2 描述的标准二分搜索寻址流程：（1）`Reset`（如果 `OPTION_COMPLETE_NEW_INSTALLATION` 置位）；（2）`Randomise` 让所有灯生成 24-bit 随机地址；（3）循环用 `SearchAddrH/M/L` 二分查找下一个未寻址灯；（4）找到后 `ProgramShortAddress` 写入短地址；（5）`Withdraw` 让该灯退出寻址队列；（6）回到 (3) 直到所有灯被寻址。

**`nOptions` 详解**：4 个 DWORD 常量可 OR 组合——`DALIV2_OPTION_COMPLETE_NEW_INSTALLATION` 重新寻址所有灯（包括已有短地址的）；`DALIV2_OPTION_DELETE_ALL_GROUP_ASSIGNMENTS` 寻址前先清所有组归属；`DALIV2_OPTION_DELETE_ALL_SCENE_ASSIGNMENTS` 寻址前先清所有场景；`DALIV2_OPTION_OPTICAL_FEEDBACK`（默认）寻址前所有灯调到 `MIN VALUE`、新分配地址的灯立即全亮——人眼可见地确认寻址进度。

**与 `FB_DALIV2AddressingIntRandomAddressing` 区别**：后者由 KL6821 端子内部执行（更快但不能提前终止 / 无进度反馈），本 FB 由 PLC 协调（更慢但全可控）。

**典型陷阱**：① 寻址期间不要下发其它 DALI 命令——会被本 FB 拒绝；② 寻址过程几分钟，HMI 要显示进度条避免用户以为程序死了；③ `bAbort` 仅停止后续分配，已分配的地址保留。

## 4. 错误码 / 返回值

`nErrorId` 复用 `Tc2_DALI` 全库错误码（见 [`error_handling/Error_Codes.md`](../error_handling/Error_Codes.md)）。

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0xxx` | 命令缓冲区溢出 | 缩短 `FB_KL68x1Communication` 任务节拍 |
| `16#1xxx` | 目标设备无响应 | 用 `FB_DALIV2QueryControlGearPresent` 确认设备在线 |
| `16#2xxx` | `nAddr` 越界或 `eAddrType` 不匹配 | 校验范围 |

## 5. 使用注意 / 常见坑

- 寻址期间不要下发其它 DALI 命令。
- 整个过程几分钟到十几分钟，HMI 需显示进度（用 `nAddressedDevices`）。
- 上线第一步通常配 `OPTION_COMPLETE_NEW_INSTALLATION | OPTION_DELETE_ALL_GROUP_ASSIGNMENTS | OPTION_DELETE_ALL_SCENE_ASSIGNMENTS`。
- `bAbort` 不撤销已分配的地址。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_DALIV2AddressingRandomAddressing.TcPOU`](../examples/P_Demo_FB_DALIV2AddressingRandomAddressing.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

完整可运行版本（包含 KL68x1 通信链上下文）见配套 TcPOU 文件。

## 7. 业务场景与实际价值

- **场景**：DALI 工程上线第一步——把所有刚装上的镇流器（出厂状态，无短地址）按物理位置依次分配短地址。HMI 显示寻址进度（已分配 X / 总 Y 个）。
- **价值**：替代厂家寻址工具（如 Tridonic masterCONFIGURATOR）；PLC 程序里一键启动，与工程版本绑定。
- **替代方案对比**：1) `FB_DALIV2AddressingIntRandomAddressing`：端子内部寻址，更快但无反馈；2) `FB_DALIV2AddressingPhysicalSelection`：物理按键选灯寻址（每盏灯逐个按按钮）；3) **本 FB**：批量寻址 + 进度反馈，工程标准方法。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DALI_EN.pdf) §4.1.1.1.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dali/142884107.html
- **相关**：[`FB_DALIV2AddressingIntRandomAddressing`](FB_DALIV2AddressingIntRandomAddressing.md)、[`FB_DALIV2AddressingPhysicalSelection`](FB_DALIV2AddressingPhysicalSelection.md)、[`FB_DALIV2ChangeAddressList`](FB_DALIV2ChangeAddressList.md)（地址表批量改）
