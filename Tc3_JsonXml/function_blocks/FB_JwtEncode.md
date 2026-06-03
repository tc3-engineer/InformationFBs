# FB_JwtEncode

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/9007206565189899.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JwtEncode.TcPOU`](../examples/P_Demo_FB_JwtEncode.TcPOU) |

---

## 1. 功能简述

`FB_JwtEncode` 用于生成 JSON Web Token（JWT，RFC 7519）。给定头部算法、payload 和私钥（PEM 文件路径或内存指针），异步生成完整的 base64url 编码且签名后的 JWT 字符串。常用于物联网设备身份认证、API 调用 OAuth2 / OIDC Bearer Token 生成场景。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    sHeaderAlg : STRING(46);
    sPayload : STRING(1023);
    sKeyFilePath : STRING(511);
    tTimeout : TIME;
    pKey : PVOID;
    nKeySize : UDINT;
    nJwtSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿激活功能块执行。 |
| `sHeaderAlg` | `STRING(46)` | JWT 头部使用的签名算法（例如 RS256）。 |
| `sPayload` | `STRING(1023)` | JWT 负载（payload）字符串。 |
| `sKeyFilePath` | `STRING(511)` | 用于 JWT 签名的私钥文件路径。 |
| `tTimeout` | `TIME` | 内部用于私钥文件访问的 ADS 超时。 |
| `pKey` | `PVOID` | 用于读取私钥的缓冲区指针。 |
| `nKeySize` | `UDINT` | 缓冲区最大大小（字节）。 |
| `nJwtSize` | `UDINT` | 生成 JWT 的字节数（含尾零）。 |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    hrErrorCode : HRESULT;
    initStatus : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 功能块处理过程进行中保持 TRUE。 |
| `bError` | `BOOL` | 出现错误时变为 TRUE。 |
| `hrErrorCode` | `HRESULT` | bError 为 TRUE 时返回错误码，错误码含义见附录 ADS Return Codes 表。 |
| `initStatus` | `HRESULT` | 功能块实例化失败时返回错误码。 |


### VAR_IN_OUT

```iecst
VAR_IN_OUT
    sJwt : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sJwt` | `STRING` | 功能块处理完成后，包含完整编码并签名后的 JWT 字符串。 |


## 3. 行为说明

异步生成 JWT。`bExecute` 上升沿触发，`bBusy = TRUE` 期间内部读私钥、做 base64url、用指定算法（如 RS256）签名；完成后 `bBusy = FALSE`，`bError` 指示是否失败，`sJwt`（VAR_IN_OUT 字符串）填充完整 JWT，`nJwtSize` 给出实际长度。私钥可通过 `sKeyFilePath`（PEM 路径）或 `pKey`+`nKeySize`（内存缓冲）两种方式提供，二选一。调用周期：每次完整调用要在 PLC 多个周期内复跑直到 `bBusy = FALSE`；再次发起新签名前先把 `bExecute` 拉低一个周期清掉前一次状态。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- 实例化后先检查 VAR_OUTPUT 中的 `initStatus`，确认 FB 初始化成功（`S_OK`）再调业务方法。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JwtEncode.TcPOU`](../examples/P_Demo_FB_JwtEncode.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：PLC 直接对接 AWS IoT Core / Azure IoT Hub 的 OAuth2 Bearer Token 认证，需要本地生成签名 JWT。
- **价值**：一次调用完成 base64url + RS256 签名；私钥保留在 PLC 文件系统，不需暴露到外部服务。
- **替代方案对比**：把私钥导出到外部签名服务 → 攻击面大；用预生成长期 token → 失去短周期轮换的安全收益。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/9007206565189899.html
