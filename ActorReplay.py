# Created by moeheart at 10/11/2020
# 演员复盘的基础方法库。

import json
import urllib.request
import hashlib
import time
import os
from PIL import Image, ImageFont, ImageDraw

from ReplayBase import StatGeneratorBase
from Functions import *
from Constants import *

class ActorStatGenerator(StatGeneratorBase):
    yanyeID = {}
    yanyeThreshold = 0.04
    yanyeActive = 0
    wumianguiID = {}
    chizhuActive = 0
    chizhuID = ""
    baimouActive = 0
    baimouID = ""
    anxiaofengActive = 0
    anxiaofengID = ""
    yuanfeiActive = 0
    mitaoActive = 0
    yatoutuoActive = 0
    yuelinActive = 0
    yuhuiActive = 0
    fulingID = {}
    sideTargetID = {}
    guishouID = {}
    yingyuanHistory = {}
    occDetailList = {}
    longzhuID =""
    upload = 0

    startTime = 0
    finalTime = 0
    playerIDList = {}
    firstHitList = {}

    actorSkillList = ["22520",  # 锈铁钩锁
                      "22521",  # 火轮重锤
                      "22203",  # 气吞八方
                      "22388",  # 岚吟
                      "22367",  # 禊祓·绀凌
                      "22356",  # 禊祓·绛岚
                      "22374",  # 零域
                      "22776",  # 双环掌击
                      "22246",  # 劈山尾鞭
                      "22272",  # 追魂扫尾
                      "22111",  # 巨力爪击
                      "23621",  # 隐雷鞭
                      "23700",  # 短歌式
                      "24029",  # 赤镰乱舞·矩形
                      "24030",  # 赤镰乱舞·扇形
                      "24031",  # 赤镰乱舞·圆形
                      "24471",  #"无尽刀狱·左"
                      "24533",  #"无尽刀狱·右"
                      "24438",  #"血海寒刀"
                      "24416",  #"宓桃普攻"
                      "24417",  #"飞轮回刃"
                      "24325",  #"挽花"
                      "24326",  #"摘月"
                      "24388",  #"银丝千织"
                      "25295",  #"幻影腿"
                      "24512",  #"万剑阵"
                      "24976",  #"净天眼"
                      "24617",  #"隼掠式"
                      "24627",  #"雁翔式"
                      "24625",  #"鹰啄式"
                      ]

    actorBuffList = ["16316",  # 离群之狐成就buff
                     "16842",  # 符咒禁锢buff
                     "17110",  # 安小逢P1站错，绞首链buff
                     "17301",  # 安小逢P2站错，不听话的小孩子buff
                     ]

    bossNameDict = {"铁黎": 1,
                    "陈徽": 2,
                    "藤原武裔": 3,
                    "源思弦": 4,
                    "咒飚狐": 4,
                    "咒凌狐": 4,
                    "驺吾": 5,
                    "方有崖": 6,
                    "周贽": 1,
                    "狼牙精锐": 1,
                    "狼牙刀盾兵": 1,
                    "厌夜": 2,
                    "迟驻": 3,
                    "白某": 4,
                    "安小逢": 5,
                    "余晖": 1, 
                    "宓桃": 2, 
                    "武雪散": 3, 
                    "猿飞": 4, 
                    "哑头陀": 5, 
                    "岳琳": 6,
                    "毗流驮迦": 5, 
                    "毗留博叉": 5, 
                    "充能核心": 5,
                    }

    def getMaskName(self, name):
        s = name.strip('"')
        if self.mask == 0:
            return s
        else:
            return s[0] + '*' * (len(s) - 1)

    def makeEmptyHitList(self):
        res = {}
        for i in self.actorSkillList:
            res["s" + i] = 0
        for i in self.actorBuffList:
            res["b" + i] = 0
        return res

    def checkFirst(self, key, data, occdict):
        if occdict[key][0] != '0' and key not in data.hitCount:
            data.hitCount[key] = self.makeEmptyHitList()
            data.hitCountP2[key] = self.makeEmptyHitList()
            data.deathCount[key] = [0, 0, 0, 0, 0, 0, 0]
            data.innerPlace[key] = [0, 0, 0, 0]
            data.drawer[key] = 0
        return data

    def hashGroup(self):
        nameList = []
        for line in self.namedict:
            if line in self.occdict and self.occdict[line][0].strip('"') != "0":
                nameList.append(self.namedict[line][0].strip('"'))
        nameList.sort()
        hashStr = self.battleDate + self.bossname + self.rawdata['20'][0].strip('"') + EDITION + "".join(nameList)
        hashres = hashlib.md5(hashStr.encode(encoding="utf-8")).hexdigest()
        return hashres

    def prepareUpload(self):
        result = {}
        server = self.rawdata["19"][0].strip('"')
        result["server"] = server
        result["boss"] = self.bossname
        result["battledate"] = self.battleDate
        result["mapdetail"] = self.rawdata['20'][0].strip('"')
        result["edition"] = EDITION
        result["hash"] = self.hashGroup()
        result["win"] = self.win
        result["time"] = int(time.time())
        allInfo = {}
        allInfo["effectiveDPSList"] = self.effectiveDPSList
        allInfo["potList"] = self.potList
        allInfo["battleTime"] = self.battleTime
        for i in range(len(allInfo["effectiveDPSList"])):
            allInfo["effectiveDPSList"][i][0] = self.getMaskName(allInfo["effectiveDPSList"][i][0])
        for i in range(len(allInfo["potList"])):
            allInfo["potList"][i][0] = self.getMaskName(allInfo["potList"][i][0])

        result["statistics"] = allInfo

        Jdata = json.dumps(result)

        jpost = {'jdata': Jdata}
        jparse = urllib.parse.urlencode(jpost).encode('utf-8')
        urllib.request.urlopen('http://139.199.102.41:8009/uploadActorData', data=jparse)
        
    def getMap(self):
        mapid = self.rawdata['20'][0]
        if mapid == "428":
            self.mapDetail = "25人英雄敖龙岛"
        elif mapid == "427":
            self.mapDetail = "25人普通敖龙岛"
        elif mapid == "426":
            self.mapDetail = "10人普通敖龙岛"
        elif mapid == "454":
            self.mapDetail = "25人英雄范阳夜变"
        elif mapid == "453":
            self.mapDetail = "25人普通范阳夜变"
        elif mapid == "452":
            self.mapDetail = "10人普通范阳夜变"
        elif mapid == "484":
            self.mapDetail = "25人英雄达摩洞"
        elif mapid == "483":
            self.mapDetail = "25人普通达摩洞"
        elif mapid == "482":
            self.mapDetail = "10人普通达摩洞"
        else:
            self.mapDetail = "未知"

    def firstStageAnalysis(self):
        res = self.rawdata

        namedict = res['9'][0]
        occdict = res['10'][0]
        sk = res['16'][0][""]

        self.namedict = namedict
        self.occdict = occdict
        occDetailList = {}

        self.playerIDList = {}

        self.firstHitList = {}

        self.toutianhuanri = 0
        
        occDetailList = {}
        
        for line in occdict:
            if occdict[line][0] != '0':
                occDetailList[line] = occdict[line][0]

        for line in sk:
            item = line[""]

            if self.startTime == 0:
                self.startTime = int(item[2])
            self.finalTime = int(item[2])

            if item[3] == "1":
                if item[5] not in namedict:
                    continue

                if occdict[item[5]][0] != '0':
                    self.playerIDList[item[5]] = 0

                if namedict[item[5]][0] == '"厌夜"' and occdict[item[5]][0] == '0':
                    if item[5] not in self.yanyeID:
                        self.yanyeID[item[5]] = 0
                    if int(item[13]) > 0:
                        self.yanyeActive = 1
                if item[4] in self.yanyeID:
                    if item[7] == "23635":
                        self.yanyeID[item[4]] = 1
                    elif item[7] == "23637":
                        self.yanyeID[item[4]] = 2

                if namedict[item[5]][0] == '"无面鬼"' and occdict[item[5]][0] == '0':
                    self.wumianguiID[item[5]] = 0

                if namedict[item[5]][0] == '"迟驻"' and occdict[item[5]][0] == '0':
                    self.chizhuActive = 1
                    self.chizhuID = item[5]

                if namedict[item[5]][0] == '"白某"' and occdict[item[5]][0] == '0':
                    self.baimouActive = 1
                    self.baimouID = item[5]

                if namedict[item[5]][0] == '"安小逢"' and occdict[item[5]][0] == '0':
                    self.anxiaofengActive = 1
                    self.anxiaofengID = item[5]

                if namedict[item[5]][0] in ['"少阴符灵"', '"少阳符灵"'] and occdict[item[5]][0] == '0':
                    self.fulingID[item[5]] = 1

                if namedict[item[5]][0] in ['"狼牙斧卫"', '"水鬼"'] and occdict[item[5]][0] == '0':
                    self.sideTargetID[item[5]] = 1

                if namedict[item[5]][0] in ['"鬼首"'] and occdict[item[5]][0] == '0':
                    self.guishouID[item[5]] = 1

                if item[6] == "17440" and item[10] == '1':  # 偷天换日
                    self.toutianhuanri = 1
                    
                if namedict[item[5]][0] == '"猿飞"' and occdict[item[5]][0] == '0':
                    self.yuanfeiActive = 1
                    
                if namedict[item[5]][0] == '"宓桃"' and occdict[item[5]][0] == '0':
                    if self.mitaoActive == 0:
                        self.mitaoActive = 1
                        self.dizzyDict = {}
                        self.leadDict = {}
                        
                if namedict[item[5]][0] in ['"毗流驮迦"', '"毗留博叉"'] and occdict[item[5]][0] == '0':
                    if self.yatoutuoActive == 0:
                        self.yatoutuoActive = 1
                        self.burstList = []
                        
                if namedict[item[5]][0] == '"岳琳"' and occdict[item[5]][0] == '0':
                    self.yuelinActive = 1
                        
                if namedict[item[5]][0] in ['"戏龙珠"'] and occdict[item[5]][0] == '0':
                    self.longzhuID = item[5]
                    
                if namedict[item[5]][0] == '"余晖"' and occdict[item[5]][0] == '0':
                   self.yuhuiActive = 1
                        
                if self.mitaoActive:
                    if item[7] in ["24704", "24705"]:
                        if item[4] not in self.leadDict:
                            self.leadDict[item[4]] = []
                        if item[4] in self.dizzyDict and self.dizzyDict[item[4]] != []:
                            self.dizzyDict[item[4]].pop()
                        self.leadDict[item[4]].append(int(item[2]))
                        
                if self.yatoutuoActive:
                    if item[7] == "24650":
                        if self.burstList == [] or int(self.burstList[-1]) + 1000 < int(item[2]):
                            self.burstList.append(int(item[2]))
                    
                if item[4] in occDetailList and occDetailList[item[4]] in ['1', '2', '3', '4', '5', '6', '7', '10', '21', '22']:
                    occDetailList[item[4]] = checkOccDetailBySkill(occDetailList[item[4]], item[7], item[13])
                    
            elif item[3] == "5":
                if occdict[item[5]][0] != '0':
                    self.playerIDList[item[5]] = 0
                if item[4] in occDetailList and occDetailList[item[4]] in ['1', '3', '10', '21']:
                    occDetailList[item[4]] = checkOccDetailByBuff(occDetailList[item[4]], item[6])
                if self.mitaoActive:
                    if item[6] in ["17767", "17919"]:
                        if item[5] not in self.dizzyDict:
                            self.dizzyDict[item[5]] = []
                        if item[10] == '1':
                            if self.dizzyDict[item[5]] == [] or self.dizzyDict[item[5]][-1][1] == 0:
                                self.dizzyDict[item[5]].append([int(item[2]) ,1])
                        else:
                            if self.dizzyDict[item[5]] != []:
                                self.dizzyDict[item[5]][-1][1] = 0

        for id in self.playerIDList:
            self.firstHitList[id] = 0
            
        self.occDetailList = occDetailList
        
        #for line in occDetailList:
        #    print(line, namedict[line], occDetailList[line])

    def secondStageAnalysis(self):
        res = self.rawdata

        namedict = res['9'][0]
        occdict = res['10'][0]
        skilldict = res['11'][0]
        sk = res['16'][0][""]
        
        if self.occDetailList != {}:
            occDetailList = self.occDetailList
        else:
            occDetailList = {}
            for line in occdict:
                if occdict[line][0] != '0':
                    occDetailList[line] = occdict[line][0]

        data = ActorData()

        num = 0
        skillLog = []

        no5P2 = 0

        lastHit = {}

        self.potList = []

        deathHit = {}
        deathHitDetail = {}

        deathBuffDict = {"9299": 30000,  # 杯水留影
                         "16981": 30000,  # 翩然
                         "17128": 5000,  # 阴阳逆乱}
                         "16892": 36000,  # 应援
                         "17301": 16000,  # 不听话的小孩子
                         "16349": 16349,  # 试炼逃避者
                         }
        deathBuff = {}
        
        xiaoyaoCount = {}
        
        for line in self.playerIDList:
            deathHitDetail[line] = []
            xiaoyaoCount[line] = {"18280": 0, #辅助药品
                                  "18281": 0, #增强药品 
                                  "18303": 0, #辅助食品
                                  "18304": 0, #增强食品
                                  }

        rateStandard = {"0": 0,
                        "25": 0.98,
                        "21": 0.95,
                        "9": 0.94,
                        "6": 0.88,
                        "2": 0.87,
                        "24": 0.87,
                        "22": 0.85,
                        "7": 0.83,
                        "8": 0.83,
                        "23": 0.82,
                        "10": 0.82,
                        "3": 0.82,
                        "1": 0.78,
                        "5": 0.77,
                        "4": 0.76,
                        "21d": 0.95,
                        "21t": 0.95,
                        "9": 0.94,
                        "6d": 0.88,
                        "6h": 0.88,
                        "7p": 0.83,
                        "7m": 0.83,
                        "2d": 0.87,
                        "2h": 0.87,
                        "22d": 0.85,
                        "22h": 0.85,
                        "10d": 0.82,
                        "10t": 0.82,
                        "3d": 0.82,
                        "3t": 0.82,
                        "1d": 0.78,
                        "1t": 0.78,
                        "5d": 0.77,
                        "5h": 0.77,
                        "4p": 0.76,
                        "4m": 0.76}

        rateThreshold = {"0": 0,
                         "25": 0.87,
                         "21": 0.84,
                         "9": 0.83,
                         "6": 0.77,
                         "2": 0.77,
                         "24": 0.77,
                         "22": 0.75,
                         "7": 0.73,
                         "8": 0.73,
                         "23": 0.73,
                         "10": 0.72,
                         "3": 0.72,
                         "1": 0.69,
                         "5": 0.68,
                         "4": 0.67,
                        "21d": 0.95,
                        "21t": 0.95,
                        "9": 0.94,
                        "6d": 0.88,
                        "6h": 0.88,
                        "7p": 0.83,
                        "7m": 0.83,
                        "2d": 0.87,
                        "2h": 0.87,
                        "22d": 0.85,
                        "22h": 0.85,
                        "10d": 0.82,
                        "10t": 0.82,
                        "3d": 0.82,
                        "3t": 0.82,
                        "1d": 0.78,
                        "1t": 0.78,
                        "5d": 0.77,
                        "5h": 0.77,
                        "4p": 0.76,
                        "4m": 0.76}

        self.dps = {}
        self.deathName = {}

        yanyeActive = self.yanyeActive
        if yanyeActive:
            yanyeHP = [0, 261440000, 261440000]
            yanyeMaxHP = 261440000
            yanyeDPS = {}
            rushDPS = {}
            rushTmpDPS = {}
            paneltyDPS = {}
            wasteDPS = {}
            yanyeResult = {}
            rush = 1
            wumianguiLabel = 0

        chizhuActive = self.chizhuActive
        if chizhuActive:
            chizhuBuff = ["16909", "16807", "16824", "17075"]
            self.buffCount = {}
            for line in self.playerIDList:
                self.buffCount[line] = {}
                for id in chizhuBuff:
                    self.buffCount[line][id] = BuffCounter(id, self.startTime, self.finalTime)
                self.dps[line] = [0, 0]

        baimouActive = self.baimouActive
        if baimouActive:
            self.breakBoatCount = {}
            for line in self.playerIDList:
                self.breakBoatCount[line] = {}
                self.breakBoatCount[line] = BuffCounter("16841", self.startTime, self.finalTime)
                self.dps[line] = [0, 0, 0]
            mingFuHistory = {}

        anxiaofengActive = self.anxiaofengActive
        if anxiaofengActive:
            self.catchCount = {}
            self.rumo = {}
            self.xuelian = {}
            self.yingyuanHistory = {}
            self.yingyuanQueue = []
            self.jingshenkuifa = {}
            for line in self.playerIDList:
                self.dps[line] = [0, 0, 0, 0, 0, 0]
                self.catchCount[line] = 0
                self.rumo[line] = BuffCounter("16796", self.startTime, self.finalTime)
                self.xuelian[line] = []
                self.yingyuanHistory[line] = 0
                self.jingshenkuifa[line] = 0
            P3 = 0
            P3TimeStamp = 0
            sideTime = 0
            guishouTime = 0
            xuelianStamp = 0
            xuelianTime = 0
            xuelianCount = 0
            
        yuanfeiActive = self.yuanfeiActive
        if yuanfeiActive:
            ballDict = {}
            for line in namedict:
                if namedict[line][0].strip('"') == "横绝气劲":
                    ballDict[line] = {"player1": 0, "player2": 0, "time1": 0, "time2": 0, "lastHit": 0, "status": 0}
            playerBallDict = {}
            for line in self.playerIDList:
                playerBallDict[line] = {"score": 0, "log": []}
                
        yuhuiActive = self.yuhuiActive
        if yuhuiActive:
            playerHitDict = {}
            playerUltDict = {}
            for line in self.playerIDList:
                playerHitDict[line] = {"num": 0, "log": []}
                playerUltDict[line] = {"num": 0, "log": []}
            countHit = 1
                
        mitaoActive = self.mitaoActive
        if mitaoActive:
            self.lastLead = "0"
            self.lastLeadTime = "0"
            
        yatoutuoActive = self.yatoutuoActive
        if yatoutuoActive:
            playerDamageDict = {}
            playerWork = {}
            playerInBattle = {}
            self.jingshenkuifa = {}
            for line in self.playerIDList:
                playerDamageDict[line] = [0] * len(self.burstList)
                playerWork[line] = 0
                playerInBattle[line] = 1
                self.jingshenkuifa[line] = 0
            burstCount = [0] * len(self.burstList)
            nowBurst = 0
            
        yuelinActive = self.yuelinActive
        if yuelinActive:
            pass
            

        if not self.lastTry:
            self.finalTime -= self.failThreshold * 1000
        
        for line in sk:
            item = line[""]

            if int(item[2]) > self.finalTime:
                break

            if item[3] == '1':  # 技能

                # 群24105 单24144
                '''
                if item[7] in ["24654"]:
                    print(item)
                    print(skilldict[item[9]][0][""][0].strip('"'))
                    
                #if item[5] in namedict and namedict[item[5]][0].strip('"') == "横绝气劲":
                #    print(item)
                #if item[4] in namedict and namedict[item[4]][0].strip('"') == "横绝气劲":
                #    print(item)
                if item[4] in namedict and item[5] in namedict:
                    print(namedict[item[4]], namedict[item[5]])
                else:
                    print("未知")
                print(item)
                '''

                if occdict[item[5]][0] != '0':
                    data = self.checkFirst(item[5], data, occdict)
                    if item[7] in self.actorSkillList and int(item[10]) != 2:
                        if item[7] == "22520":  # 锈铁钩锁
                            if item[5] not in lastHit or int(item[2]) - lastHit[item[5]] > 10000:  # 10秒缓冲时间
                                lastHit[item[5]] = int(item[2])
                            else:
                                continue
                        data.hitCount[item[5]]["s" + item[7]] += 1
                        if no5P2:
                            data.hitCountP2[item[5]]["s" + item[7]] += 1

                    if item[7] == "23092":  # 震怒咆哮
                        no5P2 = 1

                    if item[13] != item[14]:
                        deathHit[item[5]] = [int(item[2]), skilldict[item[9]][0][""][0].strip('"'), int(item[13])]

                    if item[7] == "23687":
                        deathHit[item[5]] = [int(item[2]), "死线", 0]
                        
                    if item[13] != "0" and item[5] in deathHitDetail:
                        if len(deathHitDetail[item[5]]) >= 5:
                            del deathHitDetail[item[5]][0]
                        deathHitDetail[item[5]].append([int(item[2]), skilldict[item[9]][0][""][0].strip('"'), int(item[13]), item[4]])

                    if anxiaofengActive:
                        hasRumo = self.rumo[item[5]].checkState(int(item[2]))
                        if hasRumo and occdict[item[4]][0] != '0':
                            self.dps[item[4]][5] += int(item[12])

                        if item[7] in ["24105", "24144"]:
                            if int(item[2]) - xuelianStamp > 10000:
                                if xuelianTime > 0:
                                    for line in self.xuelian:
                                        while len(self.xuelian[line]) < xuelianTime:
                                            self.xuelian[line].append(0)
                                xuelianTime += 1
                                xuelianCount = 1
                            elif int(item[2]) - xuelianStamp > 500:
                                xuelianCount += 1
                            if len(self.xuelian[item[5]]) == xuelianTime - 1:
                                if item[7] == "24105":
                                    self.xuelian[item[5]].append(xuelianCount)
                                else:
                                    self.xuelian[item[5]].append(-1)
                            xuelianStamp = int(item[2])
                            
                    if yuhuiActive:
                        if item[7] == "24438":
                            playerHitDict[item[5]]["num"] += 3
                            playerHitDict[item[5]]["log"].append("%s，血海寒刀：3层"%parseTime((int(item[2]) - self.startTime) / 1000))
                        if item[7] == "24464":
                            playerHitDict[item[5]]["num"] += 5
                            playerHitDict[item[5]]["log"].append("%s，摧城盾冲：5层"%parseTime((int(item[2]) - self.startTime) / 1000))
                        if item[7] in ["24471", "24533"]:
                            playerHitDict[item[5]]["num"] += 5
                            playerHitDict[item[5]]["log"].append("%s，无尽刀狱：5层"%parseTime((int(item[2]) - self.startTime) / 1000))
                        if item[7] == "24472":
                            playerHitDict[item[5]]["num"] += 5
                            playerHitDict[item[5]]["log"].append("%s，寒刃血莲：5层"%parseTime((int(item[2]) - self.startTime) / 1000))    
                        if item[7] == "24465" and int(item[13]) > 0:
                            playerUltDict[item[5]]["num"] += 1
                            playerUltDict[item[5]]["log"].append("%s，引导：震天血盾"%parseTime((int(item[2]) - self.startTime) / 1000)) 
                            if item[5] in playerHitDict:
                                playerHitDict[item[5]]["num"] -= 5
                        if item[7] == "24473" and int(item[13]) > 0:
                            playerUltDict[item[5]]["num"] += 1
                            playerUltDict[item[5]]["log"].append("%s，引导：血莲绽放"%parseTime((int(item[2]) - self.startTime) / 1000))
                            if item[5] in playerHitDict:
                                playerHitDict[item[5]]["num"] -= 5

                    if yuanfeiActive:
                        if item[7] == "24655" and item[4] in ballDict and int(item[2]) - ballDict[item[4]]["lastHit"] > 500:
                            if ballDict[item[4]]["player1"] == 0:
                                ballDict[item[4]]["player1"] = int(item[5])
                                ballDict[item[4]]["time1"] = int(item[2])
                                ballDict[item[4]]["lastHit"] = int(item[2])
                                ballDict[item[4]]["status"] = 1 #传球失败
                            elif ballDict[item[4]]["player2"] == 0:
                                ballDict[item[4]]["player2"] = int(item[5])
                                ballDict[item[4]]["time2"] = int(item[2])
                                ballDict[item[4]]["lastHit"] = int(item[2])
                                ballDict[item[4]]["status"] = 2 #射门失败
                            else:
                                ballDict[item[4]]["lastHit"] = int(item[2])
                                ballDict[item[4]]["status"] = 3 #射门传到第三个人
                        elif item[7] == "25421" and item[4] in ballDict and int(item[2]) - ballDict[item[4]]["lastHit"] > 500 and ballDict[item[4]]["status"] not in [1,2,3]:
                            if ballDict[item[4]]["player1"] == 0:
                                ballDict[item[4]]["time1"] = int(item[2])
                                ballDict[item[4]]["lastHit"] = int(item[2])
                                ballDict[item[4]]["status"] = 4 #无人接球
                            elif ballDict[item[4]]["player2"] == 0:
                                ballDict[item[4]]["time2"] = int(item[2])
                                ballDict[item[4]]["lastHit"] = int(item[2])
                                ballDict[item[4]]["status"] = 5 #传球出界
                            else:
                                ballDict[item[4]]["lastHit"] = int(item[2])
                                ballDict[item[4]]["status"] = 6 #射门打偏
                                
                    if yatoutuoActive:
                        if item[7] == "24650":
                            if int(item[14]) != 0 and nowBurst < len(self.burstList):
                                if abs(self.burstList[nowBurst] - int(item[2])) > 1000:
                                    nowBurst += 1
                                    for line in self.playerIDList:
                                        if playerDamageDict[line][nowBurst-1] == 0 and playerInBattle[line] == 0:
                                            playerDamageDict[line][nowBurst-1] = 2
                                playerDamageDict[item[5]][nowBurst] = 1
                                burstCount[nowBurst] += 1 

                else:
                    calculDPS = 1

                    if item[13] != "0" and item[14] == "0":  # 检查反弹
                        deathHit[item[4]] = [int(item[2]), skilldict[item[9]][0][""][0].strip('"'), int(item[13])]
                        if item[5] in deathHitDetail:
                            if len(deathHitDetail[item[5]]) >= 5:
                                del deathHitDetail[item[5]][0]
                            deathHitDetail[item[4]].append([int(item[2]), skilldict[item[9]][0][""][0].strip('"'), int(item[13]), item[4]])

                    if item[4] in self.playerIDList and int(item[11]) == 0 and item[5] in namedict and namedict[item[5]][0].strip('"') in self.bossNameDict:
                        if self.firstHitList[item[4]] == 0:
                            self.firstHitList[item[4]] = [int(item[2]), skilldict[item[9]][0][""][0].strip('"'), "", 0]
                        elif self.firstHitList[item[4]][1][0] == '#' and self.firstHitList[item[4]][2] == "":
                            if skilldict[item[9]][0][""][0].strip('"')[0] != "#":
                                self.firstHitList[item[4]][2] = skilldict[item[9]][0][""][0].strip('"')
                                self.firstHitList[item[4]][3] = int(item[2])

                    if yanyeActive:
                        calculDPS = 0
                        if item[5] in self.yanyeID:
                            yanyeLabel = self.yanyeID[item[5]]
                            yanyeHP[yanyeLabel] -= int(item[14])
                            if rush == 2:
                                if item[4] not in rushTmpDPS:
                                    rushTmpDPS[item[4]] = [0, 0, 0]
                                    yanyeResult[item[4]] = [0, 0, 0, 0, 0, 0]
                                rushTmpDPS[item[4]][yanyeLabel] += int(item[14])
                            elif rush == 1:
                                if item[4] not in rushDPS:
                                    rushDPS[item[4]] = 0
                                    yanyeResult[item[4]] = [0, 0, 0, 0, 0, 0]
                                rushDPS[item[4]] += int(item[14])
                            else:
                                if item[4] not in yanyeDPS:
                                    yanyeDPS[item[4]] = [0, 0, 0]
                                    yanyeResult[item[4]] = [0, 0, 0, 0, 0, 0]
                                yanyeDPS[item[4]][yanyeLabel] += int(item[14])
                                if yanyeHP[yanyeLabel] < yanyeHP[3 - yanyeLabel] - 0.04 * yanyeMaxHP:
                                    if item[4] not in paneltyDPS:
                                        paneltyDPS[item[4]] = 0
                                        yanyeResult[item[4]] = [0, 0, 0, 0, 0, 0]
                                    paneltyDPS[item[4]] += int(item[14])
                        if item[5] in self.wumianguiID:
                            if item[4] not in rushDPS:
                                rushDPS[item[4]] = 0
                                yanyeResult[item[4]] = [0, 0, 0, 0, 0, 0]
                            rushDPS[item[4]] += int(item[14])
                            yanyeHP[wumianguiLabel] -= int(item[14])

                    elif chizhuActive:
                        calculDPS = 0
                        if item[5] == self.chizhuID and item[4] in self.buffCount:
                            self.dps[item[4]][0] += int(item[14])
                            self.dps[item[4]][1] += int(item[14])
                            # kanpo = self.buffCount[item[4]]["17075"].checkState(int(item[2]))
                            # if kanpo < 6:
                            #    self.dps[item[4]][1] += int(item[14]) / (1 - 0.15 * kanpo)

                    elif baimouActive:
                        calculDPS = 0
                        if item[5] == self.baimouID and item[4] in self.breakBoatCount:
                            self.dps[item[4]][0] += int(item[14])
                        if item[5] in self.fulingID and item[4] in self.breakBoatCount:
                            self.dps[item[4]][1] += int(item[14])
                        if item[5] in namedict and item[4] in self.breakBoatCount and namedict[item[5]][0] == '"水牢"':
                            self.dps[item[4]][2] += int(item[14])

                    elif anxiaofengActive:
                        calculDPS = 0
                        if item[4] in self.playerIDList:
                            self.dps[item[4]][0] += int(item[14])
                        if item[5] == self.anxiaofengID and item[4] in self.playerIDList:
                            self.dps[item[4]][1] += int(item[14])
                        if item[5] in self.sideTargetID and item[4] in self.playerIDList:
                            self.dps[item[4]][2] += int(item[14])
                        if item[5] in self.guishouID and item[4] in self.playerIDList:
                            self.dps[item[4]][3] += int(item[14])
                        if P3 and item[4] in self.playerIDList:
                            self.dps[item[4]][4] += int(item[14])
                            
                    if mitaoActive:
                        if item[7] in ["24704", "24705"]:
                            self.lastLead = item[4]
                            self.lastLeadTime = item[2]
                    
                    elif yuanfeiActive:
                        if item[7] == "25459" and item[5] in ballDict and int(item[2]) - ballDict[item[5]]["lastHit"] > 500:
                            if ballDict[item[5]]["player1"] == 0:
                                ballDict[item[5]]["player1"] = int(item[4])
                                ballDict[item[5]]["time1"] = int(item[2])
                                ballDict[item[5]]["lastHit"] = int(item[2])
                                ballDict[item[5]]["status"] = 7 #传球成功
                            elif ballDict[item[5]]["player2"] == 0:
                                ballDict[item[5]]["player2"] = int(item[4])
                                ballDict[item[5]]["time2"] = int(item[2])
                                ballDict[item[5]]["lastHit"] = int(item[2])
                                ballDict[item[5]]["status"] = 8 #射门成功
                            else:
                                ballDict[item[5]]["lastHit"] = int(item[2])
                                ballDict[item[5]]["status"] = 9 #射门传到第三个人
                            
                    elif yatoutuoActive:
                        if item[5] == self.longzhuID and item[7] in ["242", "546", "305", "1613", "2479", "3971", "22341"]:
                            playerWork[item[4]] += 1
                    
                    if calculDPS:
                        if item[4] in self.playerIDList:
                            if item[4] not in self.dps:
                                self.dps[item[4]] = [0]
                            self.dps[item[4]][0] += int(item[14])
                            
                    

            elif item[3] == '5':  # 气劲

                if occdict[item[5]][0] == '0':
                    continue
                data = self.checkFirst(item[5], data, occdict)
                if item[6] == "15868":  # 老六内场buff
                    data.innerPlace[item[5]][int(item[7]) - 1] = 1
                if item[6] == "15419":  # 老五吃球buff
                    if item[9] == "false" and item[10] == '1':
                        data.drawer[item[5]] += 1
                if item[6] in self.actorBuffList and int(item[10]) == 1:
                    if item[5] not in data.hitCount:
                        data.hitCount[item[5]] = self.makeEmptyHitList()
                    data.hitCount[item[5]]["b" + item[6]] += 1

                if item[6] in deathBuffDict:
                    if item[5] not in deathBuff:
                        deathBuff[item[5]] = {}
                    deathBuff[item[5]][item[6]] = [int(item[2]), skilldict[item[8]][0][""][0].strip('"'), deathBuffDict[item[6]]]
                    
                if item[6] in ["18280", "18281", "18303", "18304"] and item[5] in self.playerIDList and item[10] == '1':
                    xiaoyaoCount[item[5]][item[6]] = 1

                if yanyeActive:
                    if item[6] == "16913":  # 厌夜威压buff
                        halfHP = (yanyeHP[1] + yanyeHP[2]) / 2
                        yanyeHP[1] = halfHP
                        yanyeHP[2] = halfHP
                        rush = 0
                        wumianguiLabel = 0

                if chizhuActive:
                    if item[6] in chizhuBuff:
                        self.buffCount[item[5]][item[6]].setState(int(item[2]), int(item[10]))

                if baimouActive:
                    if item[6] == "16841":
                        self.breakBoatCount[item[5]].setState(int(item[2]), int(item[10]))
                    if item[6] in ["16818", "16819", "16816", "16817"]:
                        mingFuHistory[item[5]] = item[6]
                    if item[6] == "16842" and item[10] == '1':
                        if item[5] in mingFuHistory:
                            lockReason = ["命符·生", "命符·死", "命符·阴", "命符·阳"][int(mingFuHistory[item[5]]) - 16816] + "站错"
                        else:
                            lockReason = "未知原因"
                        lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                        self.potList.append([namedict[item[5]][0],
                                             occDetailList[item[5]],
                                             1,
                                             self.bossNamePrint,
                                             "%s由于 %s 被锁" % (lockTime, lockReason)])

                if anxiaofengActive:
                    if item[6] == "16796" and int(item[7]) >= 9 and item[5] in self.playerIDList:  # 走火入魔
                        # print(item)
                        self.rumo[item[5]].setState(int(item[2]), int(item[10]))
                    if item[6] == "16892" and item[10] == '1':  # 应援
                        self.catchCount[item[5]] += 34.9
                        self.yingyuanHistory[item[5]] = int(item[2])
                        self.yingyuanQueue.append([int(item[2]) + 40000, int(item[7]), item[5]])
                    if item[6] == "17440" and item[10] == '1':  # 偷天换日
                        self.yingyuanHistory[item[5]] = 0
                    if item[6] == "16795" and item[10] == '1':  # 安小逢的凝视
                        self.catchCount[item[5]] += 19.9
                    if item[6] == "17110" and item[10] == '1':
                        lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                        self.potList.append([namedict[item[5]][0],
                                             occDetailList[item[5]],
                                             0,
                                             self.bossNamePrint,
                                             "%s触发P1惩罚" % lockTime])
                    if item[6] == "17301" and item[10] == '1':
                        lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                        self.potList.append([namedict[item[5]][0],
                                             occDetailList[item[5]],
                                             0,
                                             self.bossNamePrint,
                                             "%s触发P2惩罚" % lockTime])
                    if len(self.yingyuanQueue) > 0 and int(item[2]) > self.yingyuanQueue[0][0]:
                        yingyuanTop = self.yingyuanQueue.pop(0)
                        if self.yingyuanHistory[yingyuanTop[2]] != 0 and self.toutianhuanri:
                            lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                            reason = "未知"
                            if yingyuanTop[1] == 1:
                                reason = "真粉"
                            elif yingyuanTop[1] == 2:
                                reason = "假粉"
                            self.potList.append([namedict[yingyuanTop[2]][0],
                                                 occDetailList[yingyuanTop[2]],
                                                 1,
                                                 self.bossNamePrint,
                                                 "%s应援按错(%s)" % (lockTime, reason)])

                    if item[6] in ["15774", "17200"]:  # buff精神匮乏
                        stack = int(item[10])
                        if stack >= 20 and self.jingshenkuifa[item[5]] == 0:
                            lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                            self.jingshenkuifa[item[5]] = 1
                            self.potList.append([namedict[item[5]][0],
                                                 occDetailList[item[5]],
                                                 0,
                                                 self.bossNamePrint,
                                                 "%s减疗叠加20层" % lockTime,
                                                 ["不间断的减疗只计算一次"]])
                        if stack < 20 and self.jingshenkuifa[item[5]] == 1:
                            self.jingshenkuifa[item[5]] = 0
                
                if mitaoActive:
                    if item[5] in self.dizzyDict and self.dizzyDict[item[5]] != [] and self.dizzyDict[item[5]][0][0] <= int(item[2]):
                        lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                        self.potList.append([namedict[item[5]][0],
                                             occDetailList[item[5]],
                                             0,
                                             self.bossNamePrint,
                                             "%s进迷雾被魅惑" % lockTime,
                                             ["因引导而被魅惑不计算在内"]])
                        del self.dizzyDict[item[5]][0]
                        
                if yatoutuoActive:
                    if item[6] in ["15774", "17200"]:  # buff精神匮乏
                        stack = int(item[10])
                        if stack >= 20 and self.jingshenkuifa[item[5]] == 0:
                            lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                            self.jingshenkuifa[item[5]] = 1
                            self.potList.append([namedict[item[5]][0],
                                                 occDetailList[item[5]],
                                                 0,
                                                 self.bossNamePrint,
                                                 "%s减疗叠加20层" % lockTime,
                                                 ["不间断的减疗只计算一次"]])
                        if stack < 20 and self.jingshenkuifa[item[5]] == 1:
                            self.jingshenkuifa[item[5]] = 0
                            
                if yuelinActive:
                    if item[6] in ["17899"] and int(item[10]) in [8,9]:
                        lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                        self.potList.append([namedict[item[5]][0],
                                             occDetailList[item[5]],
                                             0,
                                             self.bossNamePrint,
                                             "%s传功失败：%d层" % (lockTime, int(item[10])),
                                             ["8-9层通常不影响通关，无伤大雅。"]])
                    if item[6] in ["17899"] and int(item[10]) in [1,2,3,4,5,6,7]:
                        lockTime = parseTime((int(item[2]) - self.startTime) / 1000)
                        self.potList.append([namedict[item[5]][0],
                                             occDetailList[item[5]],
                                             1,
                                             self.bossNamePrint,
                                             "%s传功失败：%d层" % (lockTime, int(item[10])),
                                             ["7层以下通常为纯演员，建议分锅。"]])


            elif item[3] == '3':  # 重伤记录
                if item[4] not in occdict or occdict[item[4]][0] == '0':
                    continue

                data = self.checkFirst(item[4], data, occdict)
                if item[4] in occdict and int(occdict[item[4]][0]) != 0:
                    severe = 1
                    if self.bossname in self.bossNameDict:
                        data.deathCount[item[4]][self.bossNameDict[self.bossname]] += 1

                    self.deathName[namedict[item[4]][0].strip('"')] = 1

                    deathTime = parseTime((int(item[2]) - self.startTime) / 1000)

                    deathSource = "未知"
                    if item[4] in deathHit and abs(deathHit[item[4]][0] - int(item[2])) < 1000:
                        deathSource = "%s(%d)" % (deathHit[item[4]][1], deathHit[item[4]][2])
                    elif item[4] in deathBuff:
                        for line in deathBuff[item[4]]:
                            if deathBuff[item[4]][line][0] + deathBuff[item[4]][line][2] > int(item[2]):
                                deathSource = deathBuff[item[4]][line][1]
                            if deathSource == "杯水留影":
                                severe = 0

                    if deathSource == "翩然":
                        deathSource = "推测为摔死"
                        
                    if item[4] in deathHitDetail:
                        deathSourceDetail = ["死前所受伤害："]
                        for line in deathHitDetail[item[4]]:
                            name = "未知"
                            if line[3] in namedict:
                                name = namedict[line[3]][0].strip('"')
                            deathSourceDetail.append("%s, %s:%s(%d)"%(parseTime((int(line[0]) - self.startTime) / 1000), name, line[1], line[2]))

                        self.potList.append([namedict[item[4]][0],
                                             occDetailList[item[4]],
                                             severe,
                                             self.bossNamePrint,
                                             "%s重伤，来源：%s" % (deathTime, deathSource),
                                             deathSourceDetail])
                        
                        if yuhuiActive and countHit:
                            playerHitDict[item[4]]["num"] += 10
                            playerHitDict[item[4]]["log"].append("%s，重伤：10层"%parseTime((int(item[2]) - self.startTime) / 1000)) 
                                         
                if yatoutuoActive:
                    playerInBattle[item[4]] = 0

            elif item[3] == '8':  # 喊话
                # print(item)
                if len(item) < 5:
                    continue
                if yanyeActive:
                    if item[4] in ['"吱吱叽！！！"', '"咯咯咕！！！"', '"……锋刃可弃身。"']:
                        rush = 2
                        rushTmpDPS = {}
                    if item[4] in ['"呜啊……！"']:
                        if rush == 2:
                            if yanyeHP[1] < yanyeHP[2]:
                                wumianguiLabel = 1
                            else:
                                wumianguiLabel = 2
                            for line in rushTmpDPS:
                                if line not in rushDPS:
                                    rushDPS[line] = 0
                                    yanyeResult[line] = [0, 0, 0, 0, 0, 0]
                                if line not in wasteDPS:
                                    wasteDPS[line] = 0
                                    yanyeResult[line] = [0, 0, 0, 0, 0, 0]
                                rushDPS[line] += rushTmpDPS[line][wumianguiLabel]
                                wasteDPS[line] += rushTmpDPS[line][3 - wumianguiLabel]
                            rushTmpDPS = {}
                        rush = 1
                if anxiaofengActive:
                    if item[4] in ['"你们全都要死！"']:
                        P3 = 1
                        P3TimeStamp = int(item[2])

                    if item[4] in ['"永远忠诚的部下们到达了！"']:
                        sideTime += 35
                    if '"来陪人家玩儿嘛~"' in item[4]:
                        sideTime += 20
                    if item[4] in ['"哼哼哼哼……"']:
                        sideTime += 20
                        guishouTime += 20
                        
                #print(item)
                
                if yuhuiActive:
                    if item[4] == '"是时候用你们的鲜血来换取最高的欢呼声了！"':
                        countHit = 0
                        
                if mitaoActive:
                    if item[4] == '"你……你不是宓桃大人！"':
                        if self.lastLead != "0" and int(item[2]) - int(self.lastLeadTime) < 13000 and int(item[2]) - int(self.lastLeadTime) > 1000:
                            id = self.lastLead
                            self.potList.append([namedict[self.lastLead][0],
                                                 occDetailList[self.lastLead],
                                                 1,
                                                 self.bossNamePrint,
                                                 "%s引导出错" % parseTime((int(item[2]) - self.startTime) / 1000),
                                                 ["持续时间：%ss/14s"%((int(item[2]) - int(self.lastLeadTime)) / 1000)]])
                
                
                if item[4] in ['"可恶…"',
                               '"哈哈哈哈哈，一群蠢货！手刃好友的滋味如何？"',
                               '"呵！算你们机灵。不过既然来了范阳，就别想都能活着回去。"',
                               '"迟驻短歌，人间大梦……"',
                               '"别打了！可是宿世散人？"',
                               '"天时已至，诸位请便。"',
                               '"呃啊...俺始终无法逃脱这牢笼..."',
                               '"不，我还不能在这里倒下，大人还需要我。"',
                               '"武士之道，虽死犹荣！"',  # 老三没有通关喊话，推定直接通关
                               '"…… …… ……"',
                               '"情况不太对……咳咳……"',  # 驺吾没有通关喊话，暂时以这句话代替
                               '"三千世界生死限，九天有苍十方剑！"',  # 方有崖暂时以这句话代替
                               '"不可能！我才是……血斗场的……王者……"', #余晖通关喊话
                               '"咳咳，不打了，我还不想现在死，咱们来日方长……"', #宓桃通关喊话
                               '"能和妾身玩这么久的人你们还是第一个，不过妾身一心只惦记着小将军……"', #宓桃25人通关喊话
                               '"想不到我武雪散竟亡于这……畜生道……可悲啊……"', #武雪散通关喊话
                               '"呃啊...啊，这双腿...还是...大不如....从前了...."', #猿飞通关喊话
                               '"…… …… …… ……"', #哑头陀通关喊话
                               '"你们竟敢染指琅弟心中所好，通通该死！"', #岳琳&岳琅通关喊话
                               ]:
                    self.win = 1
                    
            elif item[3] == "10": #战斗状态变化
                if yatoutuoActive:
                    if item[8] in self.playerIDList and item[6] == 'true':
                        playerInBattle[item[8]] = 1

            if item[3] == "6" and len(item) > 7 and item[7] == '"乌承恩"':
                self.win = 1

            num += 1
            
        #if self.bossname in ["哑头陀", "岳琳&岳琅"]:
        #    self.win = 1

        yanyeResultList = []

        effectiveDPSList = []
        
        calculDPS = 1

        if yanyeActive:
            for line in yanyeDPS:
                yanyeResult[line][0] = int(yanyeDPS[line][1] / self.battleTime)
                yanyeResult[line][1] = int(yanyeDPS[line][2] / self.battleTime)
            for line in rushDPS:
                yanyeResult[line][2] = int(rushDPS[line] / self.battleTime)
            for line in wasteDPS:
                yanyeResult[line][3] = int(wasteDPS[line] / self.battleTime)
            for line in paneltyDPS:
                yanyeResult[line][4] = int(paneltyDPS[line] / self.battleTime)
            for line in yanyeResult:
                if yanyeResult[line][0] + yanyeResult[line][1] + yanyeResult[line][2] - yanyeResult[line][4] > 10000:
                    yanyeResultList.append([namedict[line][0]] + [occDetailList[line]] + [yanyeResult[line][0] + yanyeResult[line][1] + yanyeResult[line][2] - yanyeResult[line][4]] + yanyeResult[line])

            yanyeResultList.sort(key=lambda x: -x[2])

            effectiveDPSList = yanyeResultList

            self.yanyeResult = yanyeResultList
            
            calculDPS = 0

            # print(yanyeResultList)

        elif chizhuActive:
            chizhuResult = []
            for line in self.buffCount:
                disableTime = 0
                for id in ["16909", "16807", "16824"]:
                    res = self.buffCount[line][id].sumTime()
                    disableTime += res
                wushiTime = self.buffCount[line]["17075"].sumTime()
                baseTime = self.battleTime - disableTime / 1000
                if self.dps[line][1] / baseTime > 10000:
                    chizhuResult.append([namedict[line][0],
                                         occDetailList[line],
                                         self.dps[line][1] / baseTime,
                                         disableTime / 1000,
                                         wushiTime / 1000,
                                         self.dps[line][0] / self.battleTime])

            chizhuResult.sort(key=lambda x: -x[2])
            # print(chizhuResult)

            effectiveDPSList = chizhuResult

            self.chizhuResult = chizhuResult
            
            calculDPS = 0

        elif baimouActive:
            baimouResult = []
            for line in self.breakBoatCount:
                disableTime = self.breakBoatCount[line].sumTime()
                baseTime = self.battleTime - disableTime / 1000
                effectiveDPS = (self.dps[line][0] + self.dps[line][1]) / baseTime
                originDPS = (self.dps[line][0] + self.dps[line][1] + self.dps[line][2]) / self.battleTime
                if effectiveDPS > 10000:
                    baimouResult.append([namedict[line][0],
                                         occDetailList[line],
                                         effectiveDPS,
                                         self.dps[line][0] / (baseTime - 170.5),
                                         self.dps[line][1] / 170.5,
                                         self.dps[line][2] / self.battleTime,
                                         originDPS,
                                         disableTime / 1000])

            baimouResult.sort(key=lambda x: -x[2])
            # print(baimouResult)

            effectiveDPSList = baimouResult

            self.baimouResult = baimouResult
            
            calculDPS = 0

        elif anxiaofengActive:
            for line in self.xuelian:
                while len(self.xuelian[line]) < xuelianTime:
                    self.xuelian[line].append(0)
            anxiaofengResult = []
            for line in self.playerIDList:
                disableTime = self.catchCount[line]
                P3Time = (self.finalTime - P3TimeStamp) / 1000
                originDPS = self.dps[line][0] / self.battleTime
                bossDPS = self.dps[line][1] / self.battleTime
                sideDPS = self.dps[line][2] / (sideTime - disableTime)
                guishouDPS = self.dps[line][3] / guishouTime
                P3DPS = self.dps[line][4] / P3Time
                rumoHeal = self.dps[line][5]
                luanwuHit = data.hitCount[line]["s24029"] + data.hitCount[line]["s24030"] + data.hitCount[line]["s24031"]
                xuelianStr = ""
                for ch in self.xuelian[line]:
                    if ch == -1:
                        xuelianStr += 'X'
                    else:
                        xuelianStr += str(ch)
                anxiaofengResult.append([namedict[line][0],
                                         occDetailList[line],
                                         originDPS,
                                         bossDPS,
                                         sideDPS,
                                         guishouDPS,
                                         P3DPS,
                                         rumoHeal,
                                         luanwuHit,
                                         xuelianStr
                                         ])

            # print(anxiaofengResult)
            anxiaofengResult.sort(key=lambda x: -x[2])
            effectiveDPSList = anxiaofengResult
            self.anxiaofengResult = anxiaofengResult
            
            calculDPS = 0
            
        elif yuhuiActive:
            if self.mapDetail != "10人普通达摩洞":
                playerHitList = []
                for line in playerHitDict:
                    if playerHitDict[line]["num"] != 0:
                        playerHitList.append([line, playerHitDict[line]["num"], playerHitDict[line]["log"]])
                playerHitList.sort(key = lambda x:-x[1])
                for i in range(len(playerHitList)):
                    id = playerHitList[i][0]
                    if playerHitList[i][1] >= 10:
                        self.potList.append([namedict[id][0],
                                             occdict[id][0],
                                             1,
                                             self.bossNamePrint,
                                             "狂热崇拜值叠加：%d层" %playerHitList[i][1],
                                             playerHitList[i][2]])
                    elif playerHitList[i][1] > 0:
                        self.potList.append([namedict[id][0],
                                             occdict[id][0],
                                             0,
                                             self.bossNamePrint,
                                             "狂热崇拜值叠加：%d层" %playerHitList[i][1],
                                             playerHitList[i][2]])
                
                for line in playerUltDict:
                    id = line
                    if playerUltDict[line]["num"] > 0:
                        self.potList.append([namedict[id][0],
                                             occdict[id][0],
                                             3,
                                             self.bossNamePrint,
                                             "完成引导，次数：%d" %playerUltDict[line]["num"],
                                             playerUltDict[line]["log"]])

                #for line in self.potList:
                #    print(line)
            
        elif yuanfeiActive:
            for line in ballDict:
                player1 = str(ballDict[line]["player1"])
                player2 = str(ballDict[line]["player2"])
                time1 = int(ballDict[line]["time1"])
                time2 = int(ballDict[line]["time2"])
                if ballDict[line]["status"] == 1:
                    playerBallDict[player1]["log"].append([time1, "%s手球犯规！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] -= 2
                elif ballDict[line]["status"] == 2:
                    playerBallDict[player1]["log"].append([time1, "%s传球成功！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] += 1
                    playerBallDict[player2]["log"].append([time2, "%s手球犯规！"%(parseTime((time2 - self.startTime) / 1000))])
                    playerBallDict[player2]["score"] -= 2
                elif ballDict[line]["status"] == 3:
                    playerBallDict[player1]["log"].append([time1, "%s传球成功！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] += 1
                    playerBallDict[player2]["log"].append([time2, "%s射门打偏！"%(parseTime((time2 - self.startTime) / 1000))])
                    playerBallDict[player2]["score"] -= 2
                elif ballDict[line]["status"] == 5:
                    playerBallDict[player1]["log"].append([time1, "%s传球出界！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] -= 2
                elif ballDict[line]["status"] == 6:
                    playerBallDict[player1]["log"].append([time1, "%s传球成功！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] += 1
                    playerBallDict[player2]["log"].append([time2, "%s射门打偏！"%(parseTime((time2 - self.startTime) / 1000))])
                    playerBallDict[player2]["score"] -= 2
                elif ballDict[line]["status"] == 7:
                    playerBallDict[player1]["log"].append([time1, "%s乌龙球！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] -= 2
                elif ballDict[line]["status"] == 8:
                    playerBallDict[player1]["log"].append([time1, "%s传球成功！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] += 1
                    playerBallDict[player2]["log"].append([time2, "%s射门成功！"%(parseTime((time2 - self.startTime) / 1000))])
                    playerBallDict[player2]["score"] += 1
                elif ballDict[line]["status"] == 9:
                    playerBallDict[player1]["log"].append([time1, "%s传球成功！"%(parseTime((time1 - self.startTime) / 1000))])
                    playerBallDict[player1]["score"] += 1
                    playerBallDict[player2]["log"].append([time2, "%s射门打偏！"%(parseTime((time2 - self.startTime) / 1000))])
                    playerBallDict[player2]["score"] -= 2
            
            playerBallList = []
            for line in playerBallDict:
                if playerBallDict[line]["log"] != []:
                    playerBallDict[line]["log"].sort(key = lambda x:x[0])
                    ballActualLog = []
                    for t in playerBallDict[line]["log"]:
                        ballActualLog.append(t[1])
                    playerBallList.append([line, playerBallDict[line]["score"], ballActualLog])
            playerBallList.sort(key = lambda x:-x[1])
            scoreRank = 0
            highScore = 1
            for i in range(len(playerBallList)):
                scoreRank += 1
                if scoreRank <= 3 and playerBallList[i][1] > 0:
                    highScore = playerBallList[i][1]
                if scoreRank >= 4:
                    break
            for i in range(len(playerBallList)):
                id = playerBallList[i][0]
                if playerBallList[i][1] >= highScore:
                    self.potList.append([namedict[id][0],
                                         occdict[id][0],
                                         3,
                                         self.bossNamePrint,
                                         "踢球得分：%d分，评级：梅西" %playerBallList[i][1],
                                         playerBallList[i][2]])
                elif playerBallList[i][1] >= 0:
                    self.potList.append([namedict[id][0],
                                         occdict[id][0],
                                         0,
                                         self.bossNamePrint,
                                         "踢球得分：%d分，评级：正常" %playerBallList[i][1],
                                         playerBallList[i][2]])
                else:
                    self.potList.append([namedict[id][0],
                                         occdict[id][0],
                                         1,
                                         self.bossNamePrint,
                                         "踢球得分：%d分，评级：国足" %playerBallList[i][1],
                                         playerBallList[i][2]])
                                       
        elif mitaoActive:
            for id in self.leadDict:
                timeList = []
                for row in self.leadDict[id]:
                    timeList.append(parseTime((row - self.startTime) / 1000))
                self.potList.append([namedict[id][0],
                                     occdict[id][0],
                                     3,
                                     self.bossNamePrint,
                                     "完成引导，次数：%d" %len(timeList),
                                     timeList])
                                     
        elif yatoutuoActive:
            for line in self.playerIDList:
                if nowBurst < len(playerDamageDict[line]):
                    if playerDamageDict[line][nowBurst] == 0 and playerInBattle[line] == 0:
                        playerDamageDict[line][nowBurst] = 2
            playerEscapeDict = {}
            for line in self.playerIDList:
                playerEscapeDict[line] = []
            numEffective = 0
            for i in range(len(self.burstList)):
                if burstCount[i] > 4:
                    numEffective += 1
                    for line in playerDamageDict:
                        if playerDamageDict[line][i] == 0:
                            playerEscapeDict[line].append(str(numEffective))
            for id in playerEscapeDict:
                if len(playerEscapeDict[id]) > 0:
                    s = ",".join(playerEscapeDict[id])
                    self.potList.append([namedict[id][0],
                                         occdict[id][0],
                                         0,
                                         self.bossNamePrint,
                                         "承伤逃课，次数：%d" %len(playerEscapeDict[id]),
                                         ["总承伤次数：%d"%numEffective, "逃课记录：%s"%s]])  
            for id in playerWork:
                if playerWork[id] > 0:
                    self.potList.append([namedict[id][0],
                                         occdict[id][0],
                                         3,
                                         self.bossNamePrint,
                                         "控制戏龙珠，次数：%d" %playerWork[id],
                                         ["大部分推拉技能都会被计入这项统计中，用于补贴"]]),                                          
                                       
        if calculDPS:
            bossResult = []
            for line in self.playerIDList:
                if line in self.dps:
                    dps = self.dps[line][0] / self.battleTime
                    bossResult.append([namedict[line][0],
                                       occDetailList[line],
                                       dps
                                       ])
            effectiveDPSList = bossResult

        sumDPS = 0
        numDPS = 0
        for line in effectiveDPSList:
            sumDPS += line[2]
            numDPS += 1

        averageDPS = sumDPS / (numDPS + 1e-10)
        
        if self.playerIDList != {}:
            result = {"mapdetail": self.mapDetail, "boss": self.bossname}
            Jdata = json.dumps(result)
            jpost = {'jdata': Jdata}
            jparse = urllib.parse.urlencode(jpost).encode('utf-8')
            resp = urllib.request.urlopen('http://139.199.102.41:8009/getDpsStat', data=jparse)
            res = json.load(resp)
            if res['result'] == 'success':
                resultDict = json.loads(res['statistics'].replace("'", '"'))
                sumStandardDPS = 0
                

                for i in range(len(effectiveDPSList) - 1, -1, -1):
                    line = effectiveDPSList[i]
                    occ = str(line[1])
                    if occ not in resultDict:
                        resultDict[occ] = ["xx", "xx", 50000]
                    #if occ[-1] in ["d", "h", "t", "p", "m"]:
                    #    occ = occ[:-1]
                    sumStandardDPS += resultDict[occ][2]
                    
                for i in range(len(effectiveDPSList) - 1, -1, -1):  
                    line = effectiveDPSList[i]
                    occ = str(line[1])
                    if occ not in resultDict:
                        resultDict[occ] = ["xx", "xx", 50000]
                    #if occ[-1] in ["d", "h", "t", "p", "m"]:
                    #    occ = occ[:-1]
                    GORate = line[2] / sumDPS * sumStandardDPS / resultDict[occ][2]
                    
                    occDPS = resultDict[occ][2]
                    GODPS = sumDPS / sumStandardDPS * occDPS
                    DPSDetail = ["实际DPS：%d"%line[2], "心法平均DPS：%d"%occDPS, "团队-心法平均DPS：%d"%GODPS]
                
                    if GORate < self.qualifiedRate:
                        sumDPS -= line[2]
                        numDPS -= 1
                        sumStandardDPS -= resultDict[occ][2]
                        if GORate > 0.1:
                            self.potList.append([line[0],
                                                 line[1],
                                                 1,
                                                 self.bossNamePrint,
                                                 "团队-心法DPS未到及格线(%s%%/%s%%)" % (parseCent(GORate, 0), parseCent(self.qualifiedRate, 0)),
                                                 DPSDetail])
                    elif GORate < self.alertRate:
                        self.potList.append([line[0],
                                             line[1],
                                             0,
                                             self.bossNamePrint,
                                             "团队-心法DPS低于预警线(%s%%/%s%%)" % (parseCent(GORate, 0), parseCent(self.alertRate, 0)),
                                             DPSDetail])
                    elif GORate > self.bonusRate:
                        self.potList.append([line[0],
                                             line[1],
                                             3,
                                             self.bossNamePrint,
                                             "团队-心法DPS达到补贴线(%s%%/%s%%)" % (parseCent(GORate, 0), parseCent(self.bonusRate, 0)),
                                             DPSDetail])

        if self.firstHitList != {}:
            earliestHit = 0
            earliestTankHit = 0
            for name in self.firstHitList:
                if self.firstHitList[name] == 0:
                    continue
                if self.firstHitList[name][1][0] == "#" and self.firstHitList[name][2] == "":
                    continue
                if earliestHit == 0 or self.firstHitList[name][0] < self.firstHitList[earliestHit][0]:
                    earliestHit = name
                if occDetailList[name] in ["1t", "3t", "10t", "21t"]:
                    if earliestTankHit == 0 or self.firstHitList[name][0] < self.firstHitList[earliestTankHit][0]:
                        earliestTankHit = name

            # print(earliestHit, self.firstHitList[earliestHit])
            # if earliestTankHit != 0:
            #    print(earliestTankHit, self.firstHitList[earliestTankHit])

            if earliestHit != 0 and (earliestTankHit == 0 or self.firstHitList[earliestTankHit][0] - 500 > self.firstHitList[earliestHit][0]):
                if self.firstHitList[earliestHit][2] == "":
                    hitName = self.firstHitList[earliestHit][1]
                else:
                    hitName = self.firstHitList[earliestHit][2] + "(推测)"
                self.potList = [[namedict[earliestHit][0],
                                 occDetailList[earliestHit],
                                 0,
                                 self.bossNamePrint,
                                 "提前开怪：%s" % hitName]] + self.potList
                                 
        checkXiaoYao = 0
        for line in xiaoyaoCount:
            if sum(list(xiaoyaoCount[line].values())) == 4:
                checkXiaoYao = 1
        
        if checkXiaoYao:
            for line in xiaoyaoCount:
                if sum(list(xiaoyaoCount[line].values())) < 4 and occDetailList[line] not in ["1t", "3t", "10t", "21t", "2h", "5h", "6h", "22h"]:
                    self.potList = [[namedict[earliestHit][0],
                                     occDetailList[earliestHit],
                                     0,
                                     self.bossNamePrint,
                                     "小药数量错误：%d" % sum(list(xiaoyaoCount[line].values()))]] + self.potList

        self.data = data
        self.effectiveDPSList = effectiveDPSList
        
        #print(self.potList)
        if self.win:
            self.upload = 1
        if self.mapDetail in ["25人英雄达摩洞"]:
            self.upload = 1
        
        #print(self.potList)

    def __init__(self, filename, path="", rawdata={}, myname="", failThreshold=0, battleDate="", mask=0, dpsThreshold={}):
        self.myname = myname
        self.numTry = filename[1]
        self.lastTry = filename[2]
        self.failThreshold = failThreshold
        self.win = 0
        self.battleDate = battleDate
        self.mask = mask
        super().__init__(filename[0], path, rawdata)
        if self.numTry == 0:
            self.bossNamePrint = self.bossname
        else:
            self.bossNamePrint = "%s.%d" % (self.bossname, self.numTry)
        self.no1Hit = {}
        if dpsThreshold != {}:
            self.qualifiedRate = dpsThreshold["qualifiedRate"]
            self.alertRate = dpsThreshold["alertRate"]
            self.bonusRate = dpsThreshold["bonusRate"]
        self.getMap()
        
class ActorData():

    def addActorData(self, a2):
        for line in a2.deathCount:
            if line not in self.deathCount:
                self.deathCount[line] = a2.deathCount[line]
            else:
                self.deathCount[line] = plusList(self.deathCount[line], a2.deathCount[line])

        for line in a2.hitCount:
            if line not in self.hitCount:
                self.hitCount[line] = a2.hitCount[line]
            else:
                self.hitCount[line] = plusDict(self.hitCount[line], a2.hitCount[line])

        for line in a2.hitCountP2:
            if line not in self.hitCountP2:
                self.hitCountP2[line] = a2.hitCountP2[line]
            else:
                self.hitCountP2[line] = plusDict(self.hitCountP2[line], a2.hitCountP2[line])

        for line in a2.innerPlace:
            if line not in self.innerPlace:
                self.innerPlace[line] = a2.innerPlace[line]
            else:
                self.innerPlace[line] = plusList(self.innerPlace[line], a2.innerPlace[line])

        for line in a2.drawer:
            if line not in self.drawer:
                self.drawer[line] = a2.drawer[line]
            else:
                self.drawer[line] += a2.drawer[line]

    def __init__(self):
        self.deathCount = {}
        self.hitCount = {}
        self.hitCountP2 = {}
        self.innerPlace = {}
        self.drawer = {}
        
        
class ActorAnalysis():
    map = "敖龙岛"
    mapdetail = "未知"
    myname = ""
    generator = []
    generator2 = []
    battledate = ""
    mask = 0
    color = 1
    text = 0
    speed = 3770
    pastH = 0
    yanyeTable = {}
    yanyeActive = 0
    chizhuActive = 0
    baimouActive = 0
    anxiaofengActive = 0

    def getMaskName(self, name):
        s = name.strip('"')
        if self.mask == 0:
            return s
        else:
            return s[0] + '*' * (len(s) - 1)

    def getColor(self, occ):
        if self.color == 0:
            return (0, 0, 0)
        if occ[-1] in ['d', 't', 'h', 'p', 'm']:
            occ = occ[:-1]
        colorDict = {"0": (0, 0, 0),
                     "1": (210, 180, 0),  # 少林
                     "2": (127, 31, 223),  # 万花
                     "4": (56, 175, 255),  # 纯阳
                     "5": (255, 127, 255),  # 七秀
                     "3": (160, 0, 0),  # 天策
                     "8": (255, 255, 0),  # 藏剑
                     "9": (205, 133, 63),  # 丐帮
                     "10": (253, 84, 0),  # 明教
                     "6": (63, 31, 159),  # 五毒
                     "7": (0, 133, 144),  # 唐门
                     "21": (180, 60, 0),  # 苍云
                     "22": (100, 250, 180),  # 长歌
                     "23": (71, 73, 166),  # 霸刀
                     "24": (195, 171, 227),  # 蓬莱
                     "25": (161, 9, 34),  # 凌雪
                     "211": (166, 83, 251), # 衍天
                     }
        if occ not in colorDict:
            occ = "0"
        return colorDict[occ]

    def paint(self, filename):

        # data = self.data

        battleDate = self.battledate
        generateDate = time.strftime("%Y-%m-%d", time.localtime())

        width = 800
        height = 1200

        def paint(draw, content, posx, posy, font, fill):
            draw.text(
                (posx, posy),
                text=content,
                font=font,
                fill=fill
            )
            if self.text == 1:
                if posy != self.pastH:
                    self.f.write('\n')
                    self.pastH = posy
                else:
                    self.f.write('    ')
                self.f.write(content)

        def write(content):
            if self.text == 1:
                self.f.write(content)

        fontPath = 'C:\\Windows\\Fonts\\msyh.ttc'
        if not os.path.isfile(fontPath):
            print("系统中未找到字体文件，将在当前目录下查找msyh.ttc")
            fontPath = 'msyh.ttc'
            if not os.path.isfile(fontPath):
                print("当前目录下也没有，请尝试从群文件或Github上获取")
                raise Exception("找不到字体文件：msyh.ttc")

        fontTitle = ImageFont.truetype(font=fontPath, encoding="unic", size=24)
        fontText = ImageFont.truetype(font=fontPath, encoding="unic", size=14)
        fontSmall = ImageFont.truetype(font=fontPath, encoding="unic", size=8)
        fontBig = ImageFont.truetype(font=fontPath, encoding="unic", size=48)

        image = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
        fillcyan = (0, 255, 255)
        fillblack = (0, 0, 0)
        fillgray = (127, 127, 127)
        fillred = (255, 0, 0)
        fillblue = (0, 0, 255)
        draw = ImageDraw.Draw(image)

        if self.text == 1:
            self.f = open("result.txt", "w")

        paint(draw, "%s战斗记录-演员" % self.map, 290, 10, fontTitle, fillcyan)

        if self.yanyeActive:
            paint(draw, "[厌夜]的战斗时间为%s。" % parseTime(self.yanyeTime), 10, 60, fontText, fillblack)
            paint(draw, "“平血”表示未识别时对白云和小剑的伤害。", 20, 90, fontSmall, fillblack)
            paint(draw, "“RUSH”表示识别成功时对假厌夜和无面鬼的伤害。", 20, 100, fontSmall, fillblack)
            paint(draw, "“无效DPS”表示识别成功时对真厌夜的伤害。", 20, 110, fontSmall, fillblack)
            paint(draw, "“惩罚DPS”表示平血阶段血量差超过4%时的伤害。", 20, 120, fontSmall, fillblack)
            paint(draw, "“有效DPS”表示扣除无效与惩罚DPS的总伤害。", 20, 130, fontSmall, fillblack)
            write('\n')

            paint(draw, "厌夜战斗统计", 230, 75, fontSmall, fillblack)
            paint(draw, "有效DPS", 300, 75, fontSmall, fillblack)
            paint(draw, "平血-白云", 340, 75, fontSmall, fillblack)
            paint(draw, "平血-小剑", 380, 75, fontSmall, fillblack)
            paint(draw, "RUSH", 420, 75, fontSmall, fillblack)
            paint(draw, "无效DPS", 460, 75, fontSmall, fillblack)
            paint(draw, "惩罚DPS", 500, 75, fontSmall, fillblack)
            h = 75
            for line in self.yanyeTable:
                h += 10
                paint(draw, "%s" % self.getMaskName(line[0]), 230, h, fontSmall, self.getColor(line[1]))
                paint(draw, "%d" % line[2], 300, h, fontSmall, fillblack)
                paint(draw, "%d" % line[3], 343, h, fontSmall, fillblack)
                paint(draw, "%d" % line[4], 383, h, fontSmall, fillblack)
                paint(draw, "%d" % line[5], 420, h, fontSmall, fillblack)
                paint(draw, "%d" % line[6], 460, h, fontSmall, fillblack)
                paint(draw, "%d" % line[7], 500, h, fontSmall, fillblack)

        if self.chizhuActive:
            paint(draw, "[迟驻]的战斗时间为%s。" % parseTime(self.chizhuTime), 10, 300, fontText, fillblack)
            paint(draw, "“点名时间”表示扶桑、月落、一觞的点名总时间。", 20, 330, fontSmall, fillblack)
            paint(draw, "“无视debuff”表示[无视]的层数对时间取积分。", 20, 340, fontSmall, fillblack)
            paint(draw, "“原始DPS”表示实际的DPS。", 20, 350, fontSmall, fillblack)
            paint(draw, "“等效DPS”表示考虑上面两项后，折算的DPS。", 20, 360, fontSmall, fillblack)
            write('\n')

            paint(draw, "迟驻战斗统计", 230, 300, fontSmall, fillblack)
            paint(draw, "等效DPS", 300, 300, fontSmall, fillblack)
            paint(draw, "点名时间", 340, 300, fontSmall, fillblack)
            paint(draw, "无视debuff", 380, 300, fontSmall, fillblack)
            paint(draw, "原始DPS", 420, 300, fontSmall, fillblack)
            write('\n')

            h = 300
            for line in self.chizhuTable:
                h += 10
                paint(draw, "%s" % self.getMaskName(line[0]), 230, h, fontSmall, self.getColor(line[1]))
                paint(draw, "%d" % line[2], 300, h, fontSmall, fillblack)
                paint(draw, "%d" % line[3], 343, h, fontSmall, fillblack)
                paint(draw, "%d" % line[4], 380, h, fontSmall, fillblack)
                paint(draw, "%d" % line[5], 420, h, fontSmall, fillblack)

        if self.baimouActive:
            paint(draw, "[白某]的战斗时间为%s。" % parseTime(self.baimouTime), 10, 540, fontText, fillblack)
            paint(draw, "“单体DPS”表示在常规阶段，对BOSS的DPS。", 20, 570, fontSmall, fillblack)
            paint(draw, "“符灵DPS”表示在推命阶段，对符灵的DPS。", 20, 580, fontSmall, fillblack)
            paint(draw, "“水牢DPS”表示对水牢的DPS", 20, 590, fontSmall, fillblack)
            paint(draw, "“原始DPS”表示实际的DPS。", 20, 600, fontSmall, fillblack)
            paint(draw, "“点名时间”表示受[覆舟]影响的时间。", 20, 610, fontSmall, fillblack)
            paint(draw, "“有效DPS”表示排除点名及群攻之后的DPS。", 20, 620, fontSmall, fillblack)
            write('\n')

            paint(draw, "白某战斗统计", 230, 540, fontSmall, fillblack)
            paint(draw, "有效DPS", 300, 540, fontSmall, fillblack)
            paint(draw, "单体DPS", 340, 540, fontSmall, fillblack)
            paint(draw, "符灵DPS", 380, 540, fontSmall, fillblack)
            paint(draw, "水牢DPS", 420, 540, fontSmall, fillblack)
            paint(draw, "原始DPS", 460, 540, fontSmall, fillblack)
            paint(draw, "点名时间", 500, 540, fontSmall, fillblack)
            h = 540
            for line in self.baimouTable:
                h += 10
                paint(draw, "%s" % self.getMaskName(line[0]), 230, h, fontSmall, self.getColor(line[1]))
                paint(draw, "%d" % line[2], 300, h, fontSmall, fillblack)
                paint(draw, "%d" % line[3], 340, h, fontSmall, fillblack)
                paint(draw, "%d" % line[4], 380, h, fontSmall, fillblack)
                paint(draw, "%d" % line[5], 420, h, fontSmall, fillblack)
                paint(draw, "%d" % line[6], 460, h, fontSmall, fillblack)
                paint(draw, "%d" % line[7], 500, h, fontSmall, fillblack)

        if self.anxiaofengActive:
            paint(draw, "[安小逢]的战斗时间为%s。" % parseTime(self.anxiaofengTime), 10, 780, fontText, fillblack)
            paint(draw, "“原始DPS”表示游戏中插件统计的实际DPS。", 20, 810, fontSmall, fillblack)
            paint(draw, "“安小逢DPS”表示原始DPS中属于安小逢的部分。", 20, 820, fontSmall, fillblack)
            paint(draw, "“小怪DPS”表示对狼牙斧卫和水鬼的DPS，", 20, 830, fontSmall, fillblack)
            paint(draw, "其中，每个DPS被点名的时间段都不计算。", 20, 840, fontSmall, fillblack)
            paint(draw, "“鬼首DPS”表示对鬼首的DPS。", 20, 850, fontSmall, fillblack)
            paint(draw, "注意，小怪和鬼首的DPS中，时间为估算。", 20, 860, fontSmall, fillblack)
            paint(draw, "“P3DPS”表示在P3对安小逢的DPS。", 20, 870, fontSmall, fillblack)
            paint(draw, "“入魔治疗量”表示对[走火入魔]状态队友的治疗量。", 20, 880, fontSmall, fillblack)
            paint(draw, "“赤镰乱舞”表示[赤镰乱舞]的命中次数，三种累计。", 20, 890, fontSmall, fillblack)
            paint(draw, "“承伤记录”表示对[暗月血镰]技能的承伤在第几组。", 20, 900, fontSmall, fillblack)
            paint(draw, "“0”表示本次未承伤，“X”表示本次被[盯]点名。", 20, 910, fontSmall, fillblack)
            write('\n')

            paint(draw, "安小逢战斗统计", 230, 780, fontSmall, fillblack)
            paint(draw, "原始DPS", 300, 780, fontSmall, fillblack)
            paint(draw, "安小逢DPS", 340, 780, fontSmall, fillblack)
            paint(draw, "小怪DPS", 380, 780, fontSmall, fillblack)
            paint(draw, "鬼首DPS", 420, 780, fontSmall, fillblack)
            paint(draw, "P3DPS", 460, 780, fontSmall, fillblack)
            paint(draw, "入魔治疗量", 500, 780, fontSmall, fillblack)
            paint(draw, "赤镰乱舞", 540, 780, fontSmall, fillblack)
            paint(draw, "承伤记录", 580, 780, fontSmall, fillblack)
            h = 780
            for line in self.anxiaofengTable:
                h += 10
                paint(draw, "%s" % self.getMaskName(line[0]), 230, h, fontSmall, self.getColor(line[1]))
                paint(draw, "%d" % line[2], 300, h, fontSmall, fillblack)
                paint(draw, "%d" % line[3], 340, h, fontSmall, fillblack)
                paint(draw, "%d" % line[4], 380, h, fontSmall, fillblack)
                paint(draw, "%d" % line[5], 420, h, fontSmall, fillblack)
                paint(draw, "%d" % line[6], 460, h, fontSmall, fillblack)
                paint(draw, "%d" % line[7], 500, h, fontSmall, fillblack)
                paint(draw, "%s" % line[8], 540, h, fontSmall, fillblack)
                paint(draw, "%s" % line[9], 580, h, fontSmall, fillblack)

        write('\n')
        paint(draw, "事件记录", 550, 70, fontSmall, fillblack)
        h = 70
        for line in self.potList:
            h += 10
            paint(draw, "%s" % self.getMaskName(line[0]), 560, h, fontSmall, self.getColor(line[1]))
            fill = fillblack
            if line[2] == 0:
                fill = fillgray
            elif line[2] == 3:
                fill = fillblue
            paint(draw, "%s" % line[3], 610, h, fontSmall, fill)
            paint(draw, "%s" % line[4], 640, h, fontSmall, fill)

        write('\n')
        paint(draw, "进本时间：%s" % battleDate, 700, 40, fontSmall, fillblack)
        paint(draw, "生成时间：%s" % generateDate, 700, 50, fontSmall, fillblack)
        paint(draw, "难度：%s" % self.mapdetail, 700, 60, fontSmall, fillblack)
        paint(draw, "版本号：%s" % EDITION, 30, 1180, fontSmall, fillblack)
        paint(draw, "想要生成自己的战斗记录？加入QQ群：418483739，作者QQ：957685908", 100, 1180, fontSmall, fillblack)

        image.save(filename)

        if self.text == 1:
            self.f.close()

    def analysis(self):
        if self.map == "敖龙岛":
            mapid = self.generator[0].rawdata['20'][0]
            if mapid == "428":
                self.mapdetail = "25人英雄"
            elif mapid == "427":
                self.mapdetail = "25人普通"
            elif mapid == "426":
                self.mapdetail = "10人普通"
            else:
                self.mapdetail = "未知"

        if self.map == "范阳夜变":
            mapid = self.generator[0].rawdata['20'][0]
            if mapid == "454":
                self.mapdetail = "25人英雄"
            elif mapid == "453":
                self.mapdetail = "25人普通"
            elif mapid == "452":
                self.mapdetail = "10人普通"
            else:
                self.mapdetail = "未知"
                
        if self.map == "达摩洞":
            mapid = self.generator[0].rawdata['20'][0]
            if mapid == "484":
                self.mapdetail = "25人英雄"
            elif mapid == "483":
                self.mapdetail = "25人普通"
            elif mapid == "482":
                self.mapdetail = "10人普通"
            else:
                self.mapdetail = "未知"

        self.potList = []
        for line in self.generator:
            if line.bossname == "厌夜" and line.lastTry and line.yanyeActive:
                self.yanyeActive = 1
                self.yanyeTable = line.yanyeResult
                self.yanyeTime = line.battleTime
            if line.bossname == "迟驻" and line.lastTry and line.chizhuActive:
                self.chizhuActive = 1
                self.chizhuTable = line.chizhuResult
                self.chizhuTime = line.battleTime
            if line.bossname == "白某" and line.lastTry and line.baimouActive:
                self.baimouActive = 1
                self.baimouTable = line.baimouResult
                self.baimouTime = line.battleTime
            if line.bossname == "安小逢" and line.lastTry and line.anxiaofengActive:
                self.anxiaofengActive = 1
                self.anxiaofengTable = line.anxiaofengResult
                self.anxiaofengTime = line.battleTime
            self.potList += line.potList

    def loadData(self, fileList, path, raw):
        for filename in fileList:
            res = ActorStatGenerator(filename, path, rawdata=raw[filename[0]], failThreshold=self.failThreshold, 
                battleDate=self.battledate, mask=self.mask, dpsThreshold=self.dpsThreshold)
            res.firstStageAnalysis()
            res.secondStageAnalysis()
            if res.upload:
                res.prepareUpload()
            self.generator.append(res)

    def __init__(self, filelist, map, path, config, raw):
        self.myname = config.xiangzhiname
        self.mask = config.mask
        self.color = config.color
        self.text = config.text
        self.speed = config.speed
        self.failThreshold = config.failThreshold
        self.map = map
        self.battledate = '-'.join(filelist[0][0].split('-')[0:3])
        self.dpsThreshold = {"qualifiedRate": config.qualifiedRate,
                             "alertRate": config.alertRate,
                             "bonusRate": config.bonusRate}
        self.loadData(filelist, path, raw)
        