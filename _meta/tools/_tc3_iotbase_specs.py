"""Static spec data for the Tc3_IotBase generator.

All fields are extracted verbatim from the cached PDF
TF6701_TC3_IoT_Communication_MQTT_EN.pdf (version 1.13.0). The Chinese
description for each variable was hand-translated from the PDF's English
'Description' column (cross-checked against the InfoSys topic where
available).

Entries are grouped into categories matching the on-disk subdirectories.
The helper module _tc3_iotbase_gen.py consumes this data to write the
final markdown docs and TcPOU examples.
"""

LIB = "Tc3_IotBase"
VERSION = "1.13.0"
PDF_URL = "https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf"
INFOSYS_BASE = "https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt"

INFOSYS = {
    # MQTT3 parent
    "MQTT3": f"{INFOSYS_BASE}/12567701259.html",
    "FB_IotMqttClient": f"{INFOSYS_BASE}/3391835403.html",
    "ST_IotMqttWill": f"{INFOSYS_BASE}/3392049675.html",
    "ST_IotMqttTLS": f"{INFOSYS_BASE}/3392077451.html",
    "FB_IotMqttMessageQueue": f"{INFOSYS_BASE}/3392486923.html",
    "FB_IotMqttMessage": f"{INFOSYS_BASE}/3392642699.html",
    # MQTT5
    "MQTT5": f"{INFOSYS_BASE}/12567704971.html",
    "FB_IotMqtt5Client": f"{INFOSYS_BASE}/13990483211.html",
    "FB_IotMqtt5ClientBase": f"{INFOSYS_BASE}/12560546699.html",
    "ST_IotMqtt5Will": f"{INFOSYS_BASE}/12567451275.html",
    "ST_IotMqtt5Tls": f"{INFOSYS_BASE}/12567830411.html",
    "ST_IotMqtt5Auth": f"{INFOSYS_BASE}/12565490699.html",
    "ST_IotMqtt5Connect": f"{INFOSYS_BASE}/12564928395.html",
    "FB_IotMqtt5MessageQueue": f"{INFOSYS_BASE}/14021292811.html",
    "FB_IotMqtt5Message": f"{INFOSYS_BASE}/14629604107.html",
    # MQTT5 Properties
    "MQTT5_Properties": f"{INFOSYS_BASE}/14622482571.html",
    "FB_IotMqtt5ConnAckProperties": f"{INFOSYS_BASE}/13964180235.html",
    "FB_IotMqtt5DisconnectProperties": f"{INFOSYS_BASE}/13964069515.html",
    "FB_IotMqtt5PublishProperties": f"{INFOSYS_BASE}/13961526539.html",
    "FB_IotMqtt5SubscribeProperties": f"{INFOSYS_BASE}/13963958795.html",
    "FB_IotMqtt5UnsubscribeProperties": f"{INFOSYS_BASE}/13971628683.html",
    "FB_IotMqtt5UserProperties": f"{INFOSYS_BASE}/13962881163.html",
    # enum + parameter list
    "ETcIotMqttClientState": f"{INFOSYS_BASE}/12887974283.html",
    "ParameterList": f"{INFOSYS_BASE}/14020193419.html",
}

# Each FB/FC/method spec contains the exact PDF VAR text + Chinese description.
# Layout: { name: { ... } }
