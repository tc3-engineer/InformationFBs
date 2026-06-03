# FB_EcGetAllSlaveAddr

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57011339.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetAllSlaveAddr.TcPOU`](../examples/P_Demo_FB_EcGetAllSlaveAddr.TcPOU) |

---

## 1. 功能简述

读取主站所有从站的 EtherCAT 配置地址（Configured Address）。一次成功调用后 `pAddrBuf` 指向的 UINT 数组按主站从站顺序填入每个从站的固定地址。这些固定地址是后续用 `eAdressingType_Fixed` 寻址 FPRD/FPWR 等命令的输入。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId   : T_AmsNetId;
    pAddrBuf : POINTER TO ARRAY[0..EC_MAX_SLAVES] OF UINT; 
    cbBufLen : UDINT; 
    bExecute : BOOL; 
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站的 AMS NetID。本机用空串 `''` |
| `pAddrBuf` | `POINTER TO ARRAY[0..EC_MAX_SLAVES] OF UINT` | — | 接收数组首地址 |
| `cbBufLen` | `UDINT` | — | 数组字节容量 |
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy   : BOOL;
    bError  : BOOL;
    nErrId  : UDINT;
    nSlaves : UINT; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 落沿后若出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码；`1798` 空指针、`1797` 缓冲过小 |
| `nSlaves` | `UINT` | 主站连接的从站总数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿启动一次 ADS 读。期间继续每周期调用让状态机推进；`bBusy` 落沿后才能读数组。

**地址语义**：返回的是 EtherCAT 配置地址（Configured Address），不是 AutoInc 寻址用的环位置。每个从站启动时由主站分配一个 16-bit 固定地址（典型 16#03E9 = 1001 起始）。一旦分配，无论从站在物理拓扑何处都用同一个地址 FPRD/FPWR 寻址。

**典型用法**：启动诊断阶段读全清单 → 把数组保存为 GVL → 后续诊断 / 物理读写 FB 用其中地址寻址，无需再次枚举。`FB_EcPhysicalReadCmd / FB_EcPhysicalWriteCmd` 在 `eAdressingType_Fixed` 模式下的 `adp` 参数就是这里返回的值之一。

**典型陷阱**：
- 数组容量小于 `nSlaves` 时只填到容量上限，但 `nSlaves` 仍返回真实数
- 不要把 `nSlaves` 和数组维度搞混；用 `nSlaves` 做循环上界
- 从站顺序按主站枚举顺序（与 XAE 显示一致），不是物理顺序

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `nSlaves` 与数组 |
| `1798` (`0x706`) | 空指针 | 检查 `ADR(arr)` |
| `1797` (`0x705`) | 缓冲过小 | 扩大数组 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **主站重启后地址可能变**：通常稳定，但若重新 scan 会重新分配。生产工程应锁配置
- **缓冲生命周期**（工程经验补充）：数组用全局或 FB 成员
- **配合使用**：本 FB 给出地址清单，`FB_EcGetSlaveIdentity` 给出每个地址对应的厂商/产品码，二者结合可生成"从站清单 + 型号映射"

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetAllSlaveAddr.TcPOU`](../examples/P_Demo_FB_EcGetAllSlaveAddr.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：新机型工程，前 50 从站每台都要遍历调用 `FB_EcPhysicalReadCmd` 读厂商寄存器；先用本 FB 一次拿全 50 个 adp 存到全局数组
- **价值**：把"每个从站 adp 是多少"的查询自动化，避免手工抄写 50 个数字
- **替代方案对比**：在 XAE 视图手抄 → 易错且不便维护；本 FB 给出运行时实际清单

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57011339.html
- **相关 FB / FC**：`FB_EcGetSlaveIdentity`、`FB_EcPhysicalReadCmd`（`eAdressingType_Fixed`）
