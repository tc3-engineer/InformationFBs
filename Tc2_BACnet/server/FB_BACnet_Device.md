# FB_BACnet_Device

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Server core` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319293451.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BACnet_Device.TcPOU`](../examples/P_Demo_FB_BACnet_Device.TcPOU) |

---

## 1. 功能简述

用于在运行时修改本机 BACnet Device 对象的属性（如 `Object_Name`、`Description`、`Location`）。BACnet 协议中 Device 对象代表了"这台 BACnet 控制器自身"，包含厂商、型号、本地时钟等元信息；正常情况下绝大部分 Device 对象属性已在 System Manager 中静态配置好，本 FB 仅供运行时按需调整（例如 HMI 上让运维人员改控制器位置描述、或多套硬件出厂前由 PLC 程序按机柜编号统一写入序列号）。

## 2. 接口定义

> PDF §6.8 仅给出 FB 用途说明 + 一段运行时改属性的代码示例，未单独列 `VAR_INPUT` / `VAR_OUTPUT` 区。下表整理 PDF 示例中确认存在的属性引脚。

### VAR_INPUT

```iecst
VAR_INPUT
END_VAR
```

> ⚠️ PDF 未单独列 `VAR_INPUT`；所有属性通过 FB 实例的成员变量赋值生效（见下表）。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

> ⚠️ PDF 未单独列 `VAR_OUTPUT`。

### VAR_IN_OUT

无。

### 关键属性 / 成员（按 PDF §6.8 示例确认）

| 名称 | 类型 | 说明 |
|---|---|---|
| `sObjectName` | `STRING` | Device 对象的 `Object_Name` 属性；BACnet 网络中本机的"名字"，BMS 上看到的就是这条 |
| `sDescription` | `STRING` | Device 对象的 `Description` 属性；自由文本，常用作"这台控制器是干什么的"说明 |
| `sLocation` | `STRING` | Device 对象的 `Location` 属性；常用作"机柜位置"等场地标识 |

⚠️ PDF 仅展示了以上 3 个最常改的属性，BACnet 标准中 Device 对象还有 vendor / model / firmware-version 等属性。需操作其他属性请对照 InfoSys 在线手册 `FB_BACnet_Device` 主题。

## 3. 行为说明

FB 在变量区直接声明即可：`fbDevice : FB_BACnet_Device;` 不需要任何 `VAR_INPUT` 初始化。每个 PLC 周期 `fbDevice()` 调用一次；要修改属性时在 PLC 程序里直接给 `fbDevice.sObjectName := '新名字';` 即可，下一个周期 BACnet supplement 同步到协议栈，BMS 重读 Object_Name 就能看到新值。**写入语义是电平触发的"赋值即生效"**：只要 PLC 端值不变，会按 supplement 内部协议持续同步；想避免周期写入，使用 PDF §6.3.1 推荐的"写一次条件触发"模式（demo 中 `bDescriptionChanged` 模式）。本 FB 不返回错误码；如要确认 BMS 端是否真的收到新值，需用 `FB_BACnetRM_ReadProperty` 跨连接读回校验，或用 BACnet Explorer 抓包。

## 4. 错误码 / 返回值

PDF §6.8 / InfoSys 均未列错误码。本 FB 仅修改本机 Device 对象的属性，写入失败的途径较少（属性名错只会编译失败、不会运行时报错）。⚠️ 待人工对照 InfoSys 在线 `FB_BACnet_Device` 主题确认是否有 `bError` / `nErrId` 输出。

## 5. 使用注意 / 常见坑

- **不要周期赋值变化字段**：PDF §6.3.1 反例：把 `fbDevice.sDescription := '...';` 每周期写一次会把 BACnet 客户端的写请求覆盖（"无法从 BACnet 改"），应改 PDF §6.3.1 推荐的"条件触发"模式：`IF bChanged THEN fbDevice.sDescription := '...'; bChanged := FALSE; END_IF`。
- **要每周期调用一次 `fbDevice()`**：所有 BACnet FB 必须每周期调用一次且同周期任务，本 FB 也不例外（PDF §6.4.1 / §6.4.2）。
- **`Object_Name` 在 BMS 注册表中是唯一索引**：改 `sObjectName` 后 BMS 通常需要"重新发现 (re-bind)"才能跟踪新值，否则可能出现 BMS 端历史趋势曲线断裂（工程经验补充）。
- **修改的属性默认非持久化**：与其他 BACnet 对象一样，运行时写入 Device 属性的新值需要 supplement 持久化（默认 30 分钟一次或断电触发 `SavePersistentStackData()`），否则重启后会回到 System Manager 中的初始配置。
- **本 FB 不能改 Device 实例号**：Device 实例号是 BACnet 网络上的唯一身份标识，必须在 System Manager / Device Management 中配置，不能在线改。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BACnet_Device.TcPOU`](../examples/P_Demo_FB_BACnet_Device.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_Device
VAR
    fbDevice          : FB_BACnet_Device;
    bChangeDeviceObj  : BOOL;
END_VAR

fbDevice();

IF bChangeDeviceObj THEN
    bChangeDeviceObj := FALSE;
    fbDevice.sObjectName  := 'CX5240_Floor3_HVAC';
    fbDevice.sDescription := 'HVAC controller, Bldg A floor 3';
    fbDevice.sLocation    := 'Bldg-A / Floor-3 / Cabinet-3.2';
END_IF
```

## 7. 业务场景与实际价值

- **场景**：交付现场时维护人员用 HMI 设置 BACnet 控制器名字（每台机柜按楼层重新命名），不必让维护人员开 XAE 修改 System Manager 配置再 Reload。或集成商批量上电出厂控制器，用 PLC 程序根据机柜里读到的序列号自动写入对应 `Object_Name` + `Location`。
- **价值**：把 Device 对象的运行时修改从"需要工程模式 + 重新激活配置"降级为"在 HMI 上点一下按钮"。
- **替代方案对比**：
  - 改 System Manager 后重新激活：需要工程师在场 + 工程模式权限，运行中 PLC 必须停一次
  - 在 BMS 侧用 BACnet `WriteProperty` 改 Device 对象：能做，但需要 BMS 已经识别到这台控制器（出厂未上线时不可能）
  - **本 FB**：完全在 PLC 内部完成，HMI 触发即可，无需重启

## 8. 参考资料

- **PDF**：[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.8、§6.3.1（写一次条件触发模式）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319293451.html；库根 https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/index.html
- **相关 FB / FC**：`FB_BACnet_Adapter`（一个 Device 在一个 Adapter 上）、`FB_BACnet_Server`（Device 对象生命周期归 Server 管）、`FB_BACnetRM_ReadProperty`（从其他 BACnet 设备回读本机 Device 属性做验证）
