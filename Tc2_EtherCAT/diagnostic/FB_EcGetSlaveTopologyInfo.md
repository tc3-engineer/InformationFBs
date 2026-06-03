# FB_EcGetSlaveTopologyInfo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/9007201494226699.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetSlaveTopologyInfo.TcPOU`](../examples/P_Demo_FB_EcGetSlaveTopologyInfo.TcPOU) |

---

## 1. 功能简述

读取主站全网的拓扑信息。每个从站对应一条 `ST_TopologyDataEx` 记录，含端口连接关系、上游/下游邻居地址等。本 FB 是程序化获取拓扑的唯一手段；XAE Topology 视图给出的是图形化结果，本 FB 给出可被 PLC 程序消费的数据。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId    :  T_AmsNetId;
    pAddrBuf  :  POINTER TO ARRAY [0..EC_MAX_SLAVES] OF ST_TopologyDataEx;
    cbBufLen  :  UDINT;
    bExecute  :  BOOL;
    tTimeout  :  TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `pAddrBuf` | `POINTER TO ARRAY [0..EC_MAX_SLAVES] OF ST_TopologyDataEx` | — | 接收每从站拓扑数据的数组首地址 |
| `cbBufLen` | `UDINT` | — | 数组字节容量；至少 `nSlaves * 64` 字节 |
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | — | ADS 调用超时（无默认值，必须显式传） |

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
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码；`1798` 空指针、`1797` 缓冲过小 |
| `nSlaves` | `UINT` | 从站总数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读数组。

**拓扑数据语义**：`ST_TopologyDataEx` 每条记录含从站固定地址、对应每端口（A/B/C/D）连接的下家从站地址，以及该从站的物理端口数。可由此重建整张拓扑图。开放端口（未接东西）对应字段为 0 或保留值；分支耦合器（EK1122）会在 D 端口字段填上另一条分支的首个从站地址。

**典型用法**：
- 把现场实际拓扑与工程预期拓扑做 diff，发现"接线接错"
- 远程诊断：把拓扑数据序列化推给云端，工程师不到现场也能看图
- 异常定位：当某从站断线时，知道它在拓扑中哪个位置 → 上游 / 下游谁影响谁

**典型陷阱**：
- `tTimeout` 无默认值
- `ST_TopologyDataEx` 比 `ST_EcSlaveScannedData` 大；数组维度按 64 B/从站估算栈消耗
- 拓扑改变（拔插从站）后须重新调本 FB

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `nSlaves` 与数组 |
| `1798` (`0x706`) | 空指针 | 检查 `ADR` |
| `1797` (`0x705`) | 缓冲过小 | 扩大数组 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **PDF 印刷小笔误**：PDF §4.15 标题写作 "FB_EcGetSlaveTopolgyInfo"（缺一个 o），实际 IEC 名为 `FB_EcGetSlaveTopologyInfo`，请按 InfoSys topic 与 InfoSys 库索引为准
- **拓扑变更后立即调**：现场重新插拔后需重读
- **远程可视化**（工程经验补充）：可把数组 JSON 化推给 SCADA / 云平台做拓扑图

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetSlaveTopologyInfo.TcPOU`](../examples/P_Demo_FB_EcGetSlaveTopologyInfo.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：现场连线变化后，HMI 上加"拓扑核对"功能：调本 FB 拿实际拓扑，与工程拓扑做 diff，差异以高亮显示
- **价值**：把"装错线"问题在工程上线时就发现，免去运行后才报奇怪故障
- **替代方案对比**：XAE 在线 Topology 视图需电脑；本 FB → PLC + HMI 端搞定

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.15
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/9007201494226699.html
- **相关 FB / FC**：`ST_TopologyDataEx`、`FB_EcGetAllSlaveAddr`、`ST_PortAddr`
