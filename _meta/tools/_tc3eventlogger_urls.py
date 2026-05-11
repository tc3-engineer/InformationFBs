# InfoSys topic URL map for Tc3_EventLogger entries
# Built from infosys.beckhoff.com 2026-05-11

BASE = "https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger"

URLS = {
    # Asynchronous text requests
    "FB_AsyncStrResult": "4278667403",
    "FB_RequestCauseRemedy": "13723756427",
    "FB_RequestEventClassDetails": "13723757579",
    "FB_RequestEventClassName": "5001014795",
    "FB_RequestEventDetails": "13723758731",
    "FB_RequestEventText": "5001250443",
    "FB_RequestTranslation": "14997124747",
    "FB_TcCauseRemedy": "13723759883",
    "FB_TcDetail": "13723761035",
    "F_GetEventClassName": "4278877579",
    "F_GetEventText": "5001474059",
    # EventEntry conversion
    "AdsErr_TO_TcEventEntry": "5001527435",
    "HRESULTAdsErr_TO_TcEventEntry": "5001571211",
    "TcEventEntry_TO_AdsErr": "5001614987",
    "TcEventEntry_TO_HRESULTAdsErr": "5001658763",
    # Filter
    "FB_TcClearLoggedEventsSettings": "9956769291",
    "FB_TcEventCsvExportSettings": "9956771211",
    "FB_TcEventFilter": "9956773131",
    # RemoteEventLogger
    "FB_RemoteListenerBase": "13723762187",
    "FB_TcRemoteEventLogger": "13723763339",
    # FB_ListenerBase2 parent + methods
    "FB_ListenerBase2": "5001704075",
    "FB_ListenerBase2.Execute": "5050384907",
    "FB_ListenerBase2.Subscribe": "5050398219",
    "FB_ListenerBase2.Subscribe2": "10361960203",
    "FB_ListenerBase2.Unsubscribe": "5050411915",
    "FB_ListenerBase2.OnAlarmCleared": "5051447947",
    "FB_ListenerBase2.OnAlarmConfirmed": "5051461259",
    "FB_ListenerBase2.OnAlarmDisposed": "5051475339",
    "FB_ListenerBase2.OnAlarmRaised": "5051489419",
    "FB_ListenerBase2.OnMessageSent": "5051503499",
    # FB_TcAlarm parent + methods
    "FB_TcAlarm": "5001926923",
    "FB_TcAlarm.Clear": "5050438027",
    "FB_TcAlarm.Confirm": "5050451339",
    "FB_TcAlarm.Create": "5050465035",
    "FB_TcAlarm.CreateEx": "5050478347",
    "FB_TcAlarm.Raise": "5050505739",
    "FB_TcAlarm.SetJsonAttribute": "5006660363",
    # FB_TcArguments
    "FB_TcArguments": "5002149771",
    "FB_TcArguments.IsEmpty": "5050589323",
    # FB_TcEvent (misc, read-only)
    "FB_TcEvent": "5002372619",
    # FB_TcEventBase parent + methods
    "FB_TcEventBase": "5002595467",
    "FB_TcEventBase.EqualsTo": "5002755467",
    "FB_TcEventBase.EqualsToEventClass": "5007175435",
    "FB_TcEventBase.EqualsToEventEntry": "5007225483",
    "FB_TcEventBase.EqualsToEventEntryEx": "5007275531",
    "FB_TcEventBase.GetJsonAttribute": "5007475723",
    "FB_TcEventBase.Release": "5053026955",
    "FB_TcEventBase.RequestEventClassName": "5007675915",
    "FB_TcEventBase.RequestEventText": "5007725963",
    "FB_TcEventBase.ipArguments": "5050737547",
    "FB_TcEventBase.ipSourceInfo": "5286521355",
    # FB_TcEventLogger parent + methods
    "FB_TcEventLogger": "5002818315",
    "FB_TcEventLogger.ClearAlarms": "10361937547",
    "FB_TcEventLogger.ClearAllAlarms": "5050746891",
    "FB_TcEventLogger.ClearLoggedEvents": "10408816395",
    "FB_TcEventLogger.ConfirmAlarms": "10361939723",
    "FB_TcEventLogger.ConfirmAllAlarms": "5050773003",
    "FB_TcEventLogger.ExportLoggedEvents": "10361941643",
    "FB_TcEventLogger.GetAlarm": "5050786699",
    "FB_TcEventLogger.GetAlarmEx": "5050800779",
    "FB_TcEventLogger.IsAlarmRaised": "5050814859",
    "FB_TcEventLogger.IsAlarmRaisedEx": "5050828939",
    "FB_TcEventLogger.SendMessage": "5050843019",
    "FB_TcEventLogger.SendMessage2": "10361943563",
    "FB_TcEventLogger.SendMessageEx": "5050857483",
    "FB_TcEventLogger.SendMessageEx2": "10361958283",
    # FB_TcMessage parent + methods
    "FB_TcMessage": "5003041163",
    "FB_TcMessage.Create": "5050907915",
    "FB_TcMessage.CreateEx": "5050947211",
    "FB_TcMessage.SetJsonAttribute": "5006660363",
    # FB_TcSourceInfo parent + methods
    "FB_TcSourceInfo": "5003264011",
    "FB_TcSourceInfo.Clear": "5050985483",
    "FB_TcSourceInfo.ExtendName": "5050998795",
    "FB_TcSourceInfo.ResetToDefault": "5051012491",
}


def url_for(key: str) -> str:
    tid = URLS.get(key)
    if not tid:
        return ""
    return f"{BASE}/{tid}.html"
