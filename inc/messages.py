# We need different kind of messages:
# Set Mode (CN -> PN) 
# Set Mode config(CN -> PN) which Mode (Winter/Spring/Summer/Autumn) which humidity/soil moisture wanted
# 
# 
# 
# 
# 
# Send Status (PN -> CN) (ERRORCODE) and average humidity etc. every 12 hours
# 
# 
# 
# settings are          Mode            goal soil mosture           wakeupInterval          sendInterval
# 
# 
# MessageID     Description                                                                     Message content
# 0x00          EMERGENCY ERROR of a plant node
# 0x01          Init traffic (from Plant node)                                                  MsgID, NodeID, statusID, avrgTemp, avrgSoil, avrgHumidity
# 0x02          Answer to 0x01 (from CN)                                                        MsgID, NodeID, mode, goalSoilMoisture, wakeupInterval, sendInterval
# 0x03          response to 0x02 or 0x04 (from PN)                                              MsgID, NodeID, mode, goalSoilMoisture, wakeupInterval, sendInterval
# 0x04          Response to 0x03 when everything checks out. Close connection (from CN)         MsgID, NodeID, statusID
# 0x05          Close connection acknowledged (from PN)                                         MsgID, NodeID, statusID
# 
# CN                                               PN
#                                                0x01 Hello, i am Node X my  status is S and my avrg temp/soil moisture/humidity is: Z
# Hello Node X these are your settings Y 0x02
#                                                  0x03 Ok, my settings set are Y
# (Not ok, [take a step back]) Ok, c ya 
#                                                      c ya
# 

messageID = {
    "EMERGENCY" : 0x00,
    "INIT" : 0x01,
    "INIT_ACK" : 0x02,
    "SETTINGS" : 0x03,
    "SETTINGS_ACK" : 0x04,
    "CLOSE" : 0x05,
    "CLOSE_ACK" : 0x06
}

status = {
    "OK": 1,
    "ERROR" : 2,
    "PUMPNOTWORKING" : 3,
}

modes = {
    "WINTER": 0,
    "SPRING": 1,
    "SUMMER": 2,
    "AUTUMN": 3
}