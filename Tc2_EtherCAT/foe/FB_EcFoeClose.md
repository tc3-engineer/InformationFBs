# FB_EcFoeClose

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `FoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57040267.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcFoeClose.TcPOU`](../examples/P_Demo_FB_EcFoeClose.TcPOU) |

---

## 1. 功能简述

关闭由 `FB_EcFoeOpen` 打开的 FoE 通信端口。是 FoE 三件套的收尾环节，传输完成或出错都必须调用以释放从站邮箱资源。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    hFoe     : T_HFoe;
    bExecute : BOOL; 
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `hFoe` | `T_HFoe` | — | 要关闭的 FoE handle |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后判结果。

**FoE 三件套收尾**：FoE Open 打开了从站端口资源，使用完毕必须 Close 释放。即使 Access 期间出错也必须 Close，否则该从站邮箱可能被占住直到主站重启。这是 FoE 协议与许多其他资源型协议的共性 —— 显式释放比依赖自动回收可靠得多。

**典型用法**：流式 FoE 流程的最后一步。

**典型陷阱**：
- 漏 Close 导致句柄泄漏 —— 在 try/finally 风格代码中本 FB 是 finally 分支
- 重复 Close 同一 handle 会报错
- 关闭后 handle 失效，不能再用于 Access

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 已关闭 |
| `1861` (`0x745`) | 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **错误处理也要关**：Access 报错时也务必关 handle
- **不可重复关**：状态机管理好"is_opened"标志
- **作为 RAII 风格收尾**（工程经验补充）：包成 FB 内部 method 自动调

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcFoeClose.TcPOU`](../examples/P_Demo_FB_EcFoeClose.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：流式读完日志文件后必调本 FB 关闭句柄，释放从站邮箱资源
- **价值**：避免句柄泄漏触发主站邮箱资源耗尽
- **替代方案对比**：依赖主站超时回收 → 不可靠；本 FB → 显式释放

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §8.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57040267.html
- **相关 FB / FC**：`FB_EcFoeOpen`、`FB_EcFoeAccess`、`T_HFoe`
