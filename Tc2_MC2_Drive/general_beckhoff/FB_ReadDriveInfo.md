# FB_ReadDriveInfo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `General Beckhoff` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/14430503947.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ReadDriveInfo.xml`](../examples/P_Demo_FB_ReadDriveInfo.xml) |

---

## 1. 功能简述

读取与 Beckhoff 伺服硬件通信所需**基础信息**的功能块（Function Block, FB）。给定一根 NC 轴（`Axis`），FB 返回一个 `ST_DriveInfo` 结构，里面装着该轴所连驱动器的 AMS NetId、从站地址、通道号、是否 MDP 协议、设备名、设备类型等"寻址元数据"。

这个 FB 的核心价值是**为后续 SoE/CoE 参数访问做准备**：`FB_SoERead`/`FB_CoERead` 等需要知道驱动器在 EtherCAT 上的 NetId 和从站地址，而这些信息可以由本 FB 从 `AXIS_REF` 自动解析出来，省去人工查找配置的麻烦，也让代码不写死从站地址、跟着配置走。

与本库其它 FB 不同，本 FB **有 `Done` 输出**（成功完成置 TRUE），其余 `Busy`/`Error`/`ErrorID` 时序与库内其它 FB 一致。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次读取；不需保持高电平 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 唯一标识系统中一根轴的数据结构，含位置、速度、错误状态等循环数据。**必须传引用**（VAR_IN_OUT 语义） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Done      : BOOL;
    Busy      : BOOL;
    Error     : BOOL;
    ErrorID   : UDINT;
    DriveInfo : ST_DriveInfo;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Done` | `BOOL` | 命令成功执行后置 `TRUE` |
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `Error` | `BOOL` | `Busy` 复位后若传输命令时发生错误则置位 |
| `ErrorID` | `UDINT` | `Error = TRUE` 时返回 ADS 错误码（见 §4） |
| `DriveInfo` | `ST_DriveInfo` | 与 Beckhoff 伺服硬件通信所需的基础信息结构（见下） |

### `ST_DriveInfo` 结构（PDF §5.8）

```iecst
TYPE ST_DriveInfo :
STRUCT
    NetId        : T_AmsNetId;
    SlaveAddress : T_AmsPort;
    Channel      : USINT;
    MDPProfile   : BOOL;
    DeviceName   : STRING;
    DeviceType   : E_DeviceType;
END_STRUCT
END_TYPE
```

| 成员 | 类型 | 说明 |
|---|---|---|
| `NetId` | `T_AmsNetId` | EtherCAT 主站设备的 AMS NetId 字符串 |
| `SlaveAddress` | `T_AmsPort` | EtherCAT 从站的固定地址 |
| `Channel` | `USINT` | EtherCAT 从站的通道号 |
| `MDPProfile` | `BOOL` | 是否为 MDP（Modular Device Profile）配置文件 |
| `DeviceName` | `STRING` | 设备名 |
| `DeviceType` | `E_DeviceType` | 设备类型枚举（`DEVICETYPE_UNKNOWN` = 0、`DEVICETYPE_SOE_DEFAULT` = 1、`DEVICETYPE_AX2000` = 21、`DEVICETYPE_EL72x1` = 22、`DEVICETYPE_EL72x1_OCT` = 23、`DEVICETYPE_EL72x1_OCT_SAFETY` = 24 等） |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次读取：FB 从 `Axis` 解析出底层驱动器的寻址信息并填充 `DriveInfo`，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到结束。

**状态收敛（本 FB 有 Done）**：
- **成功**：读取完成 → `Busy := FALSE`、`Done := TRUE`、`Error := FALSE`，此时 `DriveInfo` 各字段有效可用
- **出错**：ADS 通信失败 / 轴未正确 Link 等 → `Busy := FALSE`、`Done := FALSE`、`Error := TRUE`、`ErrorID` 给 ADS 错误码

**与无 Done 的兄弟 FB 区别**：库内大多数 FB（如 `FB_BrakeControl`、`FB_SetPositionOffset`）只有 `Busy`/`Error`，本 FB 额外提供 `Done`，可直接以 `Done` 的上升沿作为"结果就绪"的触发条件，把 `DriveInfo` 拷出来给后续 SoE/CoE FB 用。

**典型链式用法**：`FB_ReadDriveInfo` 读出 `DriveInfo.NetId` → 把它作为 `FB_SoERead.NetId` / `FB_CoERead.NetId` 的输入，从而不在代码里写死 NetId。`Execute` 是边沿触发，重读需新的上升沿；读到的信息在配置不变期间是稳定的，通常初始化时读一次即可。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 **ADS 错误码**（不是 NC 错误号、也不是 HRESULT）。

| 错误来源 | 含义 | 处理建议 |
|---|---|---|
| ADS 通信错误 | 与驱动器/EtherCAT 主站的 ADS 传输失败 | 检查 EtherCAT 总线 OP、轴 Link、`Axis` 引用有效性 |
| 轴未关联到支持的驱动器 | `Axis` 没连到 AX5xxx / AX8xxx / 紧凑型驱动等受支持硬件 | 核对 NC 轴的 I/O Link，确认连的是受支持的 Beckhoff 伺服硬件 |

⚠️ PDF 与 InfoSys 在本 FB 章节未逐条列出具体 ADS 错误码，请参见 Beckhoff ADS Return Codes 总表。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **本 FB 有 `Done`，用它判完成最稳**：`Done` 上升沿即"`DriveInfo` 就绪"，比盯 `Busy` 下降沿更直观。
- **`DriveInfo.NetId` 用来喂给 SoE/CoE FB**：这是本 FB 最常见用法——避免在代码里写死 NetId。
- **初始化时读一次即可**：配置不变时 `DriveInfo` 稳定，没必要每周期反复读。
- **`Execute` 是边沿触发 + `Busy` 期间持续循环调用**：异步跨周期。
- **`DeviceType` 用于分支型号专用逻辑**：例如据此决定用 SoE 还是 CoE 路径访问参数。
- **`Channel` 区分多通道设备**：AX5x06 等双通道设备靠 `Channel` 区分 A/B 通道（工程经验补充）。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ReadDriveInfo.xml`](../examples/P_Demo_FB_ReadDriveInfo.xml)

```iecst
// 场景：初始化时读出驱动器寻址信息，供后续 SoE/CoE 参数访问使用
rtReadTrig(CLK := bReadInfoReq);
fbReadInfo(
    Execute := rtReadTrig.Q,
    Axis    := axisMain,
    Done    => bInfoDone,
    Busy    => bInfoBusy,
    Error   => bInfoError,
    ErrorID => nInfoErrorID,
    DriveInfo => stDriveInfo
);
```

## 7. 业务场景与实际价值

- **场景**：初始化时自动获取驱动器 NetId/从站地址供后续参数访问、运行期诊断界面显示设备名/类型、据 `DeviceType` 分支不同型号逻辑。
- **价值**：把"驱动器在总线上是谁"从人工查配置变成程序化读取，代码不写死从站地址，跟着 System Manager 配置走，换硬件不改代码。
- **替代方案对比**：
  - 在代码里硬编码 NetId / SlaveAddress：换从站位置就要改代码，易错
  - 手动从 System Manager 抄写：人工、易过时
  - **本 FB**：从 `AXIS_REF` 自动解析，唯一标准入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.1.5，结构 §5.8 `ST_DriveInfo`、§5.6 `E_DeviceType`
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/14430503947.html
- **相关 FB**：`FB_SoERead` / `FB_CoERead`（用 `DriveInfo.NetId` 做参数访问）
