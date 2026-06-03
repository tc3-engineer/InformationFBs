# FB_EcGetMasterState

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT State Machine` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/9007199311767563.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetMasterState.TcPOU`](../examples/P_Demo_FB_EcGetMasterState.TcPOU) |

---

## 1. 功能简述

读取 EtherCAT 主站的当前状态机状态。返回 WORD 类型的 `state`，取值为 EC_DEVICE_STATE_INIT (0x01) / PREOP (0x02) / SAFEOP (0x04) / OP (0x08) 之一。正常运行期主站应在 OP。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId   : T_AmsNetId; 
    bExecute : BOOL; 
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站的 AMS NetID |
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    state  : WORD; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `state` | `WORD` | 主站状态机状态：0x01=INIT, 0x02=PREOP, 0x04=SAFEOP, 0x08=OP |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `state`。

**主站状态机概念**：EtherCAT 主站有 INIT → PREOP → SAFEOP → OP 四态状态机。
- INIT：未配置，无邮箱通信，从站尚未识别身份
- PREOP：已配置，邮箱可用（CoE / FoE / SoE 都能调），PDO 关闭
- SAFEOP：PDO 输入侧有效，输出由从站本地"safe state"控制（典型为 0 输出）
- OP：完全运行，PDO 输入输出都有效，是业务正常态

主站启动过程会依序经历这四个状态；任何中间错误都可能让主站停在中间态，影响业务。

**判定方法**：正常运行时应有 `state = EC_DEVICE_STATE_OP` (0x08)。其他值多为错误或启动中过渡态。状态字可能包含错误位（如 0x14 = SAFEOP + Error），所以判 OP 必须用等于 0x08 而非 `>= 0x08`，这是判读最容易踩的坑。

**典型用法**：
- HMI 主页状态指示绑本 FB 1 s 刷新
- 业务程序在主循环开始处判 `state = 0x08` 才允许动作；不在 OP 不下发 PDO
- 配合 `F_ConvStateToString` 显示可读字符串

**典型陷阱**：
- `state` 可能含错误标志位（如 `0x14` = SAFEOP + Error）；判 OP 要用等号 `= 0x08` 不要 `≥`
- 主站启动到 OP 需要一定时间，重启后需等几秒
- 想"请求转 OP" 用 `FB_EcSetMasterState`，本 FB 只读不写

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `state` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **`EC_DEVICE_STATE_OP` 常量**：用 GVL 中常量避免硬编码
- **配合 `F_ConvStateToString`**：把 WORD 翻译成 "INIT" / "OP" 等字符串
- **配合 `FB_EcGetAllSlaveStates`**：主站 OP 不代表所有从站都 OP，需双重判定

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetMasterState.TcPOU`](../examples/P_Demo_FB_EcGetMasterState.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：业务主循环开始处判"主站是不是 OP"。若不是 OP 业务跳过本周期，避免向脱机网络写 PDO 触发奇怪现象
- **价值**：把"前置条件检查"做成 1 行 IF
- **替代方案对比**：直接看 PDO 链接状态 → 单从站精度而非主站全局；本 FB → 全局判定

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §5.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/9007199311767563.html
- **相关 FB / FC**：`FB_EcSetMasterState`（请求状态）、`FB_EcReqMasterState`（异步请求）、`F_ConvStateToString`
