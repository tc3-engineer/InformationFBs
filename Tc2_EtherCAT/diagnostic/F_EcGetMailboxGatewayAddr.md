# F_EcGetMailboxGatewayAddr

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/20498780427.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_F_EcGetMailboxGatewayAddr.TcPOU`](../examples/P_Demo_F_EcGetMailboxGatewayAddr.TcPOU) |

---

## 1. 功能简述

通过 EtherCAT 主站的 Object ID 查询该主站对应物理网卡的 IPv4 地址和 MAC 地址。如果需要字符串形式，配合 Tc2_System 中的 `F_CreateIPv4Addr` 与 `F_CreateMacAddr`。返回 `HRESULT`。

## 2. 接口定义

**FUNCTION 声明（PDF §4.25 原文逐字）**：

> `METHOD F_EcGetMailboxGatewayAddr : HRESULT`（PDF 标 METHOD，实际 FUNCTION）
>
> Inputs:
> - `oidEcMaster : OTCID;` (object ID of EtherCAT master)
>
> Outputs:
> - `aIpAddress      : T_IPv4AddrArr;`
> - `aMacAddress     : ARRAY[0..5] OF BYTE;`

### VAR_INPUT 参数

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `oidEcMaster` | `OTCID` | — | EtherCAT 主站 Object ID（用 `FB_EcMasterObjectID` 取） |

### VAR_OUTPUT 参数

| 名称 | 类型 | 说明 |
|---|---|---|
| `aIpAddress` | `T_IPv4AddrArr` | IPv4 地址 4 字节数组（典型 `[10, 0, 0, 1]`） |
| `aMacAddress` | `ARRAY[0..5] OF BYTE` | MAC 地址 6 字节数组 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用即返回**：同步 FUNCTION，立即返回 HRESULT。

**用途**：EtherCAT Mailbox Gateway 是个高级功能，允许外部设备（PC、移动 App）通过 IP 网络访问 EtherCAT mailbox 协议（CoE / FoE / SoE 等）。本 FC 给出"我应该连哪个 IP" —— 是用 mailbox gateway 客户端必填的信息。在多网卡 IPC 上更显重要：操作系统层的 ipconfig 看不出哪张网卡专门承载 EtherCAT 主站，本 FC 是程序化获取的唯一方式。

**典型用法**：
- HMI 显示"EtherCAT Mailbox Gateway 地址: 10.0.0.1"
- 写"PC 端 mailbox gateway 客户端"前先调本 FC 获取目标 IP

**返回值**：
- `SUCCEEDED(hr) = TRUE`：成功
- 失败：HRESULT 错误码

**典型陷阱**：
- TwinCAT 版本要求 v3.1.4026.16 + Tc2_EtherCAT ≥ 3.7.1.0
- 输出是字节数组；要 STRING 须配 `F_CreateIPv4Addr(aIpAddress)`
- `oidEcMaster = 0` 必失败

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `S_OK` (0) | 成功 | 读 aIpAddress / aMacAddress |
| `E_FAIL` 等 | 失败 | 检查 oidEcMaster 是否有效 |

## 5. 使用注意 / 常见坑

- **字节数组 → 字符串**：用 Tc2_System 的 `F_CreateIPv4Addr(aIpAddress)` / `F_CreateMacAddr(aMacAddress, '-', FALSE)`
- **配合 `FB_EcMasterObjectID`**：先拿 OID 再调本 FC
- **作为完整诊断链一环**（工程经验补充）：HMI 主站详情页一般显示 NetID、OID、IP、MAC 一组

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_EcGetMailboxGatewayAddr.TcPOU`](../examples/P_Demo_F_EcGetMailboxGatewayAddr.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：客户的移动端 App 需要通过 Mailbox Gateway 连主站查从站 CoE 对象；HMI 显示一个二维码包含主站 IP，App 扫码即连。先调本 FC 拿 IP
- **价值**：把"应该连哪个 IP"做成运行时查询，免去硬编码
- **替代方案对比**：Windows ipconfig 看网卡 IP → 不知道哪张卡是主站；本 FC → 精确定位

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.25
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/20498780427.html
- **相关 FB / FC**：`FB_EcMasterObjectID`（取 OID）、Tc2_System 的 `F_CreateIPv4Addr` 与 `F_CreateMacAddr`
