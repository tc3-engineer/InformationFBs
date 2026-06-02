# FB_TcTouchLock_AcquireFocus

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `TcTouchLock` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/6811367563.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcTouchLock_AcquireFocus.TcPOU`](../examples/P_Demo_FB_TcTouchLock_AcquireFocus.TcPOU) |

---

## 1. 功能简述

多触摸屏聚焦控制：一台 IPC 接多个多触控屏时，避免多屏并发输入相互干扰。本 FB 给某个屏请求 / 释放 input focus；同一时刻只有持有 focus 的屏可输入，其余被屏蔽。使用前需先用命令行工具 `TcTouchLockService.exe` 给每个屏分配一个唯一标识号 (`sSetID`)。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable : BOOL;
    sSetID : STRING(32);
    tLEDTime : TIME := 200;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bEnable` | `BOOL` | - | TRUE = 请求 focus；FALSE = 释放 focus。 |
| `sSetID` | `STRING(32)` | - | 屏的唯一标识（由 `TcTouchLockService.exe` 配置时分配）。 |
| `tLEDTime` | `TIME` | `200` | 等待 focus 时 LED 闪烁周期（100 ms - 1 s）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bAcquired : BOOL := FALSE;
    bLED : BOOL := FALSE;
    bBusy : BOOL;
    bError : : BOOL;
    nErrID : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bAcquired` | `BOOL` | `FALSE` | TRUE = 本屏获得 focus；FALSE = 失去 focus。 |
| `bLED` | `BOOL` | `FALSE` | 状态 LED 输出（常亮 / 常灭 / 闪烁，详见行为说明）。 |
| `bBusy` | `BOOL` | - | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `: BOOL` | - | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `nErrID` | `UDINT` | - | ADS 错误号 (`0x0006` 端口未找到 = 服务未运行)。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`bEnable = TRUE` 请求 focus；`bEnable = FALSE` 释放 focus。若另一屏当前持有 focus，则要等它释放后本屏才能拿到 → `bAcquired` 从 FALSE 变 TRUE。`bLED` 输出可接到屏的状态 LED：常亮 = 本屏持有 focus；常灭 = 本屏未持有；按 `tLEDTime` 周期闪烁 = 本屏在等待 focus。`bBusy` 表示请求处理中；`bError` / `nErrID` 反映 ADS 错误。错误码：`0x0000` 无错；`0x0006` 目标端口未找到（多半 `TcTouchLockService.exe` 没运行）。

## 4. 错误码 / 返回值

本 FB 通过 `bError` / `ERR` + `nErrId` / `ERRID` 输出报告错误：

- `bError = FALSE` 且 `nErrId = 0`：调用成功。
- `bError = TRUE`：调用失败，错误号在 `nErrId`。

常见错误号（按 ADS Return Codes 表）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND）—— 设备未启用或 DeviceId 错 |
| `0x07` | 目标机不在线（ADSERR_DEVICE_NOTREADY） |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT）—— `TMOUT` 太短或现场总线响应慢 |
| 其他 | 见 Beckhoff **ADS Return Codes** 在线表，及现场总线主站特有的错误码（PDF 未列入本节） |

⚠️ PDF / InfoSys 未在本 FB 处列具体的现场总线错误号，需配合主站手册查询。

## 5. 使用注意 / 常见坑

- **先用 `TcTouchLockService.exe` 配置屏的 sSetID**——不配的话本 FB 直接报 `0x0006`。（工程经验补充）
- PDF VAR 区把 `bError` 写成 `bError:`（末尾多冒号），是 PDF 排版错误；接口实际名是 `bError`。（工程经验补充）
- `tLEDTime` 范围 100 ms - 1 s；超出可能不闪烁或闪烁异常。（工程经验补充）
- 焦点切换有几百毫秒延迟，业务侧不要期待瞬间响应。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcTouchLock_AcquireFocus.TcPOU`](../examples/P_Demo_FB_TcTouchLock_AcquireFocus.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：大型设备 IPC 接 3 块控制面板：操作员在面板 A 上做配置时不应被面板 B / C 误触；用本 FB 让 A 独占输入。
- **价值**：避免多面板并发输入冲突，提升大型设备人机界面安全性。
- **替代方案对比**：
  - 不用：多面板都能输入 → 操作冲突
  - 软件锁定其它面板的输入事件：需要修改 HMI 软件
  - **本 FB**：标准方案

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.13.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/6811367563.html
