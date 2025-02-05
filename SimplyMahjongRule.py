# -*- coding: utf-8 -*-
# Update Date: 2024/12/19
__author__ = 'chilamchou'

import copy
import random

from pprint import pprint
import MahjongConstData as MCD


class SimplyMahjongRule(object):
    
    def __init__( self ):

        self.ruleName = ''

        #self.mahjongBox = None
        self.mahjongBoxName = None

        self.jokerDefineNameGroup = None

        self.normalSuitGroup = None

        self.openTypeGroup = None

        self.mahjongBoxLimitNum = -1

        self.mahjongListenLimitNum = -1

    # 設定玩法名稱
    # ruleName: 玩法名稱
    # return: 0:成功, -1:失敗
    def setRuleName( self, ruleName ):
        
        if ruleName not in MCD.conGameRuleMap:
            # 玩法名稱不合法, 目前只支援 CrazyGoldHook (金勾釣)
            return  -1

        self.ruleName = ruleName

        self.mahjongBoxName = MCD.conGameRuleMap[ self.ruleName ][ 'mahjongBoxName' ]
        
        self.jokerDefineNameGroup = MCD.conGameRuleMap[ self.ruleName ][ 'jokerDefineNameGroup' ]

        self.normalSuitGroup = MCD.conGameRuleMap[ self.ruleName ][ 'normalSuitGroup' ]

        self.openTypeGroup = MCD.conGameRuleMap[ self.ruleName ][ 'openTypeGroup' ]

        return  0


    # 設定其他運作參數
    def setParameter( self, mahjongBoxLimitNum, mahjongListenLimitNum ):
        # 牌盒剩下多少張時 , 能胡就胡
        self.mahjongBoxLimitNum = mahjongBoxLimitNum

        self.mahjongListenLimitNum = mahjongListenLimitNum

        return  0
        

    # 判斷麻將牌章是否合法
    def checkMahjongNameIsLegal( self, mahjongName, allowEmptyFlag ):

        if allowEmptyFlag == True:
            if mahjongName == 'EMPTY':
                # 允許空牌
                return  0

        if mahjongName in self.mahjongBoxName:
            # 合法牌章
            return  0
        
        # 不合法牌章
        return  -1
    
    # 判斷吃碰槓的細部資訊是否合法
    def checkOpenMahjongDataIsLegal( self, openMahjongData ):

        openType = openMahjongData['openType']

        if openType not in self.openTypeGroup:
            return  -1

        mahjong = openMahjongData['mahjong']

        if self.checkMahjongNameIsLegal( mahjong, False ) < 0:
            return  -2
        
        if openType == MCD.OPEN_CHOW:

            sequence = openMahjongData['sequence']

            # 檢查吃牌3張組合 的起始麻將牌 是否合法
            if self.checkMahjongNameIsLegal( sequence, False ) < 0:
                return  -3

            # 吃牌3張組合花色
            seqSuit = self.getMahjongSuitType( sequence )

            # 檢查吃牌3張組合的花色 是否合法
            if seqSuit not in self.normalSuitGroup:
                return  -4

            # 吃那張牌花色
            mjSuit = self.getMahjongSuitType( mahjong )

            # 檢查吃牌的花色 是否合法
            if mjSuit not in self.normalSuitGroup:
                return  -5
            
            # 檢查吃牌組合花色與吃那張牌花色是否一致
            if seqSuit != mjSuit:
                return  -6
            
            # 吃牌3張 要包含 吃牌麻將那張牌
            seqHex = MCD.mapMahjongNameToHex[ sequence ]
            mjHex = MCD.mapMahjongNameToHex[ mahjong ]

            if (seqHex & 0x0F) >= 7:        # 吃牌三張的起始值, 不能超過序號8以上 ex 89萬 89筒 89索
                return  -7
                    
            # 檢查吃牌組合 是否 有包含 吃牌牌章
            if mjHex == (seqHex+0) or mjHex == (seqHex+1) or mjHex == (seqHex+2):
                pass
            else:
                return  -8
            

        return  0

    
    # 判斷手上牌與吃碰槓的資訊是否合法
    def checkOnHandAndOpenMahjongIsLegal( self, onHandMahjong, openMahjong ):

        retData = { 'errFlag':0, 'errMsg':None }

        totalMahjongNum = 0

        # ----------------------------------------------------------------------

        # onHandMahjong 為List型態, 代表手上的牌
        # 合法張數為 [ 1 , 4 , 7 , 10 , 13 ]        
        if len( onHandMahjong ) not in MCD.conOnHandLegalNum:
            retData['errFlag'] = -1000
            retData['errMsg'] = 'onHandMahjong number is illegal.'
            return  retData
        
        # 判斷手上牌的牌章是否合法
        for mahjong in onHandMahjong:
            if self.checkMahjongNameIsLegal( mahjong, False ) < 0:
                retData['errFlag'] = -1001
                retData['errMsg'] = 'onHandMahjong name is illegal.'
                return  retData
            
        # ----------------------------------------------------------------------
            
        totalMahjongNum += len( onHandMahjong )

        # ----------------------------------------------------------------------
        
        # openMahjong 為List型態, 代表吃碰槓的資訊
        # 合法數量為4組
        if len( openMahjong ) >= 5:
            retData['errFlag'] = -1100
            retData['errMsg'] = 'openMahjong number is illegal.'
            return  retData

        for openMahjongData in openMahjong:

            detail = self.checkOpenMahjongDataIsLegal( openMahjongData )
            if detail < 0:
                retData['errFlag'] = -1101

                msg = f'openMahjong data is illegal. detail:{detail}'

                retData['errMsg'] = msg
                return  retData
            
        # ----------------------------------------------------------------------

        totalMahjongNum += len( openMahjong ) * 3

        if totalMahjongNum != 13:
            retData['errFlag'] = -1200
            retData['errMsg'] = 'totalMahjongNum illegal.'
            return  retData            

        # ----------------------------------------------------------------------
        
        return  retData

    # 依據傳入的麻將List , 來取得計數張數的資訊
    def getMahjongCountGroup( self, mahjongNameList, includeJokerFlag ):

        mahjongCountGroup = []
        jokerNum = 0

        for i in range( len( MCD.AryToMj ) ):

            mahjongHex = MCD.AryToMj[ i ]

            mahjongName = MCD.mapMahjongHexToName[ mahjongHex ]
        
            cnt = 0
            if mahjongName not in self.mahjongBoxName:
                cnt = -1
            else:
                cnt = mahjongNameList.count( mahjongName )

                # 判斷是否Joker
                if mahjongName in self.jokerDefineNameGroup:        

                    jokerNum += cnt

                    # 判斷是否要納入Joker的計算
                    if includeJokerFlag == False:
                        cnt = -1                

            mahjongCountGroup.append( cnt )    # 紀錄此牌章的數量
                   
        return  mahjongCountGroup, jokerNum
    

    def getMahjongSuitType( self, mahjongName ):
        for key, value in MCD.conSuitMahjongNameMap.items():
            if mahjongName in value:
                return  key

        return  -1
    

    def choiceOneMahjong( self, mahjongIndexList ):

        length = len( mahjongIndexList )

        if length == 0:
            return  -1
       
        # 回傳值 包含 start ~ end 之間的正整數
        index = random.randint( 0 , length-1 )

        return  mahjongIndexList[ index ]

            



    
    #################################################################################################
    #################################################################################################
    #################################################################################################

    # 確認是否滿足全刻搭
    #def checkAllThreeMahjong( self, mahjongCountGroup, jokerNum ):



    # 尋找手上牌是否有能槓就槓的牌章(暗槓或碰牌加槓)(只限萬筒索與字牌)
    def findOnHandKongMahjong( self, mahjongCountGroup, openMahjongInfo=None ):

        retData = { 'actType':None, 'actMahjongName':None }

        # ----------------------------------------------------------------------
        # 檢查手上牌是否可以暗槓
        for i in range( len( mahjongCountGroup ) ):

            mahjongName = MCD.IndexToMjName[ i ]

            mahjongSuit = self.getMahjongSuitType( mahjongName )

            # 麻將花色必須為 萬筒索 或 字牌
            if mahjongSuit == MCD.MJ_SUIT_JOKER:
                continue

            if mahjongCountGroup[ i ] == 4:
                retData[ 'actType' ] = MCD.OPEN_CONCEALED_KONG      # 暗槓
                retData[ 'actMahjongName' ] = mahjongName
                return  retData

        # ----------------------------------------------------------------------
        # 檢查手上牌是否可以碰牌加槓
        for openMahjongData in openMahjongInfo:

            openType = openMahjongData['openType']

            if openType == MCD.OPEN_PONG:   # 碰牌

                pongMahjong = openMahjongData['mahjong']

                index = MCD.mapMahjongNameToIndex[ pongMahjong ]

                if mahjongCountGroup[ index ] > 0:
                    retData[ 'actType' ] = MCD.OPEN_ADD_KONG        # 碰牌加槓
                    retData[ 'actMahjongName' ] = pongMahjong
                    return  retData

        # ----------------------------------------------------------------------

        return  retData
    
    

    # 確認自身摸進牌後, 要進行何種動作 (捨牌/槓牌/碰牌加槓/胡牌)
    # 內部判斷 : 能槓就槓, 摸進牌後, 能進行碰牌加槓或暗槓 , 就先執行
    # onHandMahjong: 手上的牌
    # takeMahjong: 摸進的牌
    # openMahjongInfo: 吃碰槓的資訊(List)
    # [
    #    { openType:OPEN_PONG, mahjong:'A01' },                 -- 碰1萬
    #    { openType:OPEN_KONG, mahjong:'A02' },                 -- 明槓2萬
    #    { openType:OPEN_CONCEALED_KONG, mahjong:'B05' },       -- 暗槓5筒
    #    { openType:OPEN_CHOW, sequence:'C01', mahjong:'C02' }, -- 吃牌組合為 123索, 用13索,吃2索
    # ] 
    # mahjongBoxNum: 牌盒剩餘的張數, 若牌局快打完時, 能胡就胡
    # listenMahjongNum: 可以胡牌的牌種數量, 例: 1萬, 2萬, 3萬, 5索, 6索 -- 則傳入 5
    def checkSelfDiscardMahjong( self, onHandMahjong, takeMahjong, openMahjongInfo, mahjongBoxNum=-1, listenMahjongNum=-1 ):

        traceLog = 1

        # 複製一份手上的牌, 後續都操作此資料
        saveOnHandMahjong = copy.copy( onHandMahjong )

        # 複製一份吃碰槓的牌, 後續都操作此資料
        saveOpenMahjong = copy.copy( openMahjongInfo )     

        returnData = { 'errFlag':0, 'errMsg':None, 'actType':None, 'actMahjongName':None }

        #----------------------------------------------------------------------

        # 檢查手上牌與吃碰槓的資訊是否合法
        retInfo = self.checkOnHandAndOpenMahjongIsLegal( saveOnHandMahjong, saveOpenMahjong )

        if retInfo['errFlag'] < 0:
            returnData[ 'errFlag' ] = retInfo[ 'errFlag' ]
            returnData[ 'errMsg' ] = retInfo[ 'errMsg' ]
            return  returnData
        
        # 檢查摸進來的牌是否合法
        if self.checkMahjongNameIsLegal( takeMahjong, False ) < 0:
            returnData[ 'errFlag' ] = -1500
            returnData[ 'errMsg' ] = 'takeMahjong name is illegal.'
            return  returnData            
       
        #----------------------------------------------------------------------
        # 執行到這邊, 代表傳進來的參數都合法
        #----------------------------------------------------------------------        

        saveOnHandMahjong.append( takeMahjong )     # 將摸進的牌加入手上牌
        #print("saveOnHandMahjong :", saveOnHandMahjong)

        # 計算各牌章的數量
        mahjongCountGroup, jokerNum = self.getMahjongCountGroup( saveOnHandMahjong, False )

        if traceLog == 1:
            print("mahjongCountGroup :", mahjongCountGroup)
            print("jokerNum :", jokerNum)
            print("mahjongBoxNum :", mahjongBoxNum)
            print("listenMahjongNum :", listenMahjongNum)

             

        #----------------------------------------------------------------------

        # 計數手上牌後, 判斷是否能槓就槓, 賴子不會納入判斷
        resultKong = self.findOnHandKongMahjong( mahjongCountGroup, saveOpenMahjong )

        if resultKong[ 'actType' ] != None:
            # 能槓就槓, 直接回傳執行槓牌動作
            returnData[ 'actType' ] = resultKong[ 'actType' ]
            returnData[ 'actMahjongName' ] = resultKong[ 'actMahjongName' ]
            return  returnData
        
        #----------------------------------------------------------------------   

        # 將所有牌章積分都先設為0,積分越低,越不會被選到
        mahjongPointList = [ 0 for i in range( len( mahjongCountGroup ) ) ]

        # 紀錄湊搭的牌組
        splitMahjongInfo = []

        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------                  


        '''
        判斷順序:
            字牌刻搭                            -- 積分10
            萬筒索刻搭                          -- 積分50            

            字牌對子(可以用賴子湊成刻搭)          -- 積分20
            字牌對子(無法用賴子湊成刻搭)          -- 積分100

            字牌單張(可以用賴子湊成刻搭)          -- 積分30
            字牌單張(無法用賴子湊成刻搭)          -- 積分200

            萬筒索對子(可以用賴子湊成刻搭)        -- 積分60
            萬筒索對子(無法用賴子湊成刻搭)        -- 積分150

            萬筒索單張(可以用賴子湊成刻搭)        -- 積分80
            萬筒索單張(可以湊成順搭)              -- 積分300
            萬筒索單張(無法用賴子湊成刻搭)         -- 積分500
        '''

        AAA_Num = len( openMahjongInfo )    # 刻搭初始值 -- 為吃碰槓組數
        Pair_Num = 0   # 對子數量
        
        if traceLog:
            print("@@@@ SRC @@@@")
            self.debugMahjongListCountGroup( mahjongCountGroup, 'mahjongCountGroup' )
            self.debugMahjongListCountGroup( mahjongPointList, 'mahjongPointList' )

        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------           

        # Step 1 : 判斷(字牌)(刻搭) .. 直接給積分
        bFlag = False
        for i in range( len( MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_WORD] ) ):
            index = MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_WORD][ i ]
            if mahjongCountGroup[ index ] == 3:
                mahjongCountGroup[ index ] -= 3
                mahjongPointList[ index ] = 10      # 此牌章積分
                AAA_Num += 1    # 刻搭數量+1

                tempMahjong = MCD.IndexToMjName[ index ]
                splitMahjongInfo.append( ['Step1-AAA',tempMahjong,tempMahjong,tempMahjong] )
                bFlag = True

        if traceLog and bFlag == True:
            print("@@@@ Step 1 @@@@ 字牌刻搭")
            self.debugMahjongListCountGroup( mahjongCountGroup, 'mahjongCountGroup' )
            self.debugMahjongListCountGroup( mahjongPointList, 'mahjongPointList' )
            print("AAA_Num :", AAA_Num)
            print("Pair_Num :", Pair_Num)        
            print("splitMahjongInfo : ", splitMahjongInfo)

        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------          

        # Step 2 : 判斷(萬筒索)(刻搭) .. 直接給積分
        bFlag = False
        for i in range( len( MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_CHAR] ) ):
            index1 = MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_CHAR][ i ]
            index2 = MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_DOT][ i ]
            index3 = MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_BAMBOO][ i ]

            indexList = [ index1, index2, index3 ]

            for index in indexList:
                if mahjongCountGroup[ index ] == 3:
                    mahjongCountGroup[ index ] -= 3
                    mahjongPointList[ index ] = 30    # 此牌章積分
                    AAA_Num += 1    # 刻搭數量+1

                    tempMahjong = MCD.IndexToMjName[ index ]
                    splitMahjongInfo.append( ['Step2-AAA',tempMahjong,tempMahjong,tempMahjong] )
                    bFlag = True

        if traceLog and bFlag == True:
            print("@@@@ Step 2 @@@@ 萬筒索刻搭")
            self.debugMahjongListCountGroup( mahjongCountGroup, 'mahjongCountGroup' )
            self.debugMahjongListCountGroup( mahjongPointList, 'mahjongPointList' )   
            print("AAA_Num :", AAA_Num)
            print("Pair_Num :", Pair_Num)        
            print("splitMahjongInfo : ", splitMahjongInfo)    

        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------                      

        # Step 3 : 判斷(字牌)(對子) .. 會判斷 當下賴子數量足夠湊成刻搭 , 不足就當字牌對子
        bFlag = False
        for i in range( len( MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_WORD] ) ):
            index = MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_WORD][ i ]
            if mahjongCountGroup[ index ] == 2:
                bFlag = True
                mahjongCountGroup[ index ] -= 2
                if jokerNum > 0:
                    jokerNum -= 1
                    mahjongPointList[ index ] = 50      # 此牌章積分, 賴子可以湊成刻搭
                    AAA_Num += 1    # 刻搭數量+1

                    tempMahjong = MCD.IndexToMjName[ index ]
                    splitMahjongInfo.append( ['Step3-AAA',tempMahjong,tempMahjong,'JK'] )

                else:
                    mahjongPointList[ index ] = 100      # 此牌章積分, 賴子不足, 只能當對子(字牌)
                    Pair_Num += 1   # 對子數量+1

                    tempMahjong = MCD.IndexToMjName[ index ]
                    splitMahjongInfo.append( ['Step3-Pair',tempMahjong,tempMahjong] )                    

        if traceLog and bFlag == True:
            print("@@@@ Step 3 @@@@ 字牌對子")
            self.debugMahjongListCountGroup( mahjongCountGroup, 'mahjongCountGroup' )
            self.debugMahjongListCountGroup( mahjongPointList, 'mahjongPointList' )   
            print("AAA_Num :", AAA_Num)
            print("Pair_Num :", Pair_Num) 
            print("splitMahjongInfo : ", splitMahjongInfo)        

        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------

        # Step 4 : 判斷(萬筒索)(對子) .. 會判斷 當下賴子數量足夠湊成刻搭 , 不足就當一般對子
        bFlag = False
        for i in range( len( MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_CHAR] ) ):
            index1 = MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_CHAR][ i ]
            index2 = MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_DOT][ i ]
            index3 = MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_BAMBOO][ i ]

            indexList = [ index1, index2, index3 ]

            for index in indexList:
                if mahjongCountGroup[ index ] == 2:
                    bFlag = True
                    mahjongCountGroup[ index ] -= 2
                    if jokerNum > 0:
                        jokerNum -= 1
                        mahjongPointList[ index ] = 80      # 賴子可以湊成刻搭
                        AAA_Num += 1    # 刻搭數量+1

                        tempMahjong = MCD.IndexToMjName[ index ]
                        splitMahjongInfo.append( ['Step4-AAA',tempMahjong,tempMahjong,'JK'] )
                    else:
                        mahjongPointList[ index ] = 150      # 賴子不足, 只能當對子(萬筒索)                                  
                        Pair_Num += 1   # 對子數量+1

                        tempMahjong = MCD.IndexToMjName[ index ]
                        splitMahjongInfo.append( ['Step4-Pair',tempMahjong,tempMahjong] )                        

        if traceLog and bFlag == True:
            print("@@@@ Step 4 @@@@ 萬筒索對子")
            self.debugMahjongListCountGroup( mahjongCountGroup, 'mahjongCountGroup' )
            self.debugMahjongListCountGroup( mahjongPointList, 'mahjongPointList' )
            print("AAA_Num :", AAA_Num)
            print("Pair_Num :", Pair_Num)
            print("splitMahjongInfo : ", splitMahjongInfo)

        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------

        # Step 5 : 判斷(字牌)(單張) .. 會判斷 當下賴子數量足夠湊成刻搭 或 對子 , 不足就當單張
        bFlag = False
        for i in range( len( MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_WORD] ) ):
            index = MCD.conSuitMahjongRangeMap[MCD.MJ_SUIT_WORD][ i ]
            if mahjongCountGroup[ index ] == 1:
                bFlag = True               
                mahjongCountGroup[ index ] -= 1
                mahjongPointList[ index ] = 500
                tempMahjong = MCD.IndexToMjName[ index ]

                matchFlag = False
                if matchFlag == False and jokerNum >= 2:
                    jokerNum -= 2
                    mahjongPointList[ index ] = 80
                    splitMahjongInfo.append( ['Step5-AAA',tempMahjong,'JK','JK'] )
                    AAA_Num += 1
                    matchFlag = True

                if matchFlag == False and jokerNum >= 1:
                    jokerNum -= 1
                    mahjongPointList[ index ] = 180
                    splitMahjongInfo.append( ['Step5-Pair',tempMahjong,'JK'] )                    
                    Pair_Num += 1
                    matchFlag = True

                if matchFlag == False:                    
                    splitMahjongInfo.append( ['Step5-Single',tempMahjong] )
        
        if traceLog and bFlag == True:
            print("@@@@ Step 5 @@@@ 字牌單張")
            self.debugMahjongListCountGroup( mahjongCountGroup, 'mahjongCountGroup' )
            self.debugMahjongListCountGroup( mahjongPointList, 'mahjongPointList' )
            print("AAA_Num :", AAA_Num)
            print("Pair_Num :", Pair_Num)        
            print("splitMahjongInfo : ", splitMahjongInfo)         
        
        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------

        # Step 6 : 判斷(萬筒索)(單張) .. 依序順子靠牌程度來給積分
        bFlag = False
        for i in range( len( mahjongCountGroup ) ):

            if mahjongCountGroup[ i ] <= 0:
                continue

            mahjongName = MCD.IndexToMjName[ i ]

            mahjongSuit = self.getMahjongSuitType( mahjongName )

            #print("mahjongName :", mahjongName)

            # 字牌或百搭
            if mahjongSuit == MCD.MJ_SUIT_WORD or mahjongSuit == MCD.MJ_SUIT_JOKER:
                continue

            # 單張一般花色
            if mahjongCountGroup[ i ] == 1:

                bFlag = True

                mahjongPointList[ i ] = 550
                # 取得此牌章可以成順搭的組合
                # ex : 二筒  [一二三筒]  [二三四筒]
                # ex : 三萬  [一二三萬]  [二三四萬]  [三四五萬]
                ABC_Data = MCD.conMapMahjongNameABC[ mahjongName ]

                #print("ABC_Data : ", ABC_Data)
                #print("mahjongCountGroup : ", mahjongCountGroup)

                for si in range( len( ABC_Data ) ):

                    if si == 2:     # 這個位置的牌 就是 mahjongCountGroup[ i ] 的牌章 , 所以不用判斷
                        continue

                    if ABC_Data[ si ] == -1:    # 沒有順靠牌的定義位址, 直接跳過
                        continue

                    #print("si :", si)

                    # 判斷是否有鄰近的牌章
                    if mahjongCountGroup[ ABC_Data[ si ] ] > 0:

                        if si == 1 or si == 3:  # 順跳一
                            #print("si :", si , -20, mahjongName )
                            mahjongPointList[ i ] -= 100

                        if si == 0 or si == 4:  # 順跳二
                            #print("si :", si , -10, mahjongName )
                            mahjongPointList[ i ] -= 20


                tempMahjong = MCD.IndexToMjName[ i ]
                matchFlag = False
                if matchFlag == False and jokerNum >= 2:
                    jokerNum -= 2
                    mahjongPointList[ i ] = 150
                    splitMahjongInfo.append( ['Step6-AAA',tempMahjong,'JK','JK'] )
                    AAA_Num += 1
                    matchFlag = True

                if matchFlag == False and jokerNum >= 1:
                    jokerNum -= 1
                    mahjongPointList[ i ] = 280
                    splitMahjongInfo.append( ['Step6-Pair',tempMahjong,'JK'] )     
                    Pair_Num += 1               
                    matchFlag = True

                if matchFlag == False:                    
                    splitMahjongInfo.append( ['Step6-Single',tempMahjong] )             

        # 清空萬筒索單張的計數值(因為算順搭靠牌時, 不能同時扣除張數)
        for i in range( len( mahjongCountGroup ) ):

            if mahjongCountGroup[ i ] <= 0:
                continue

            mahjongSuit = self.getMahjongSuitType( mahjongName )

            # 字牌或百搭
            if mahjongSuit == MCD.MJ_SUIT_WORD or mahjongSuit == MCD.MJ_SUIT_JOKER:
                continue

            # 單張一般花色
            if mahjongCountGroup[ i ] == 1:
                mahjongCountGroup[ i ] = 0

        if traceLog and bFlag == True:  
            print("@@@@ Step 6 @@@@ 萬筒索單張")
            self.debugMahjongListCountGroup( mahjongCountGroup, 'mahjongCountGroup' )
            self.debugMahjongListCountGroup( mahjongPointList, 'mahjongPointList' )
            print("AAA_Num :", AAA_Num)
            print("Pair_Num :", Pair_Num)  
            print("splitMahjongInfo : ", splitMahjongInfo)                         

        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------

        # Step 7 : 判斷是否還有剩下賴子牌, 直接兜成刻搭或對子
        bFlag = False
        if AAA_Num < 4:
            #jokerNum = 5       # 測試
            canAAA_Num = int( jokerNum / 3 )
            #print("canAAA_Num :", canAAA_Num)    

                    
            for i in range( canAAA_Num ):
                bFlag = True
                splitMahjongInfo.append( ['Step7-AAA','JK','JK','JK'] )

            AAA_Num += canAAA_Num
            jokerNum -= ( canAAA_Num * 3 )

        if Pair_Num == 0:
            singleMahjongCnt = mahjongCountGroup.count( 1 )
            #print("singleMahjongCnt :", singleMahjongCnt)

            if singleMahjongCnt == 0 and jokerNum >= 2:
                bFlag = True
                jokerNum -= 2
                Pair_Num += 1                
                splitMahjongInfo.append( ['Step7-Pair','JK','JK'] )

            #if singleMahjongCnt == 1 and jokerNum >= 1:
            #    jokerNum -= 1
            #    Pair_Num += 1

        if traceLog and bFlag == True:  
            print("@@@@ Step 7 @@@@ joker補滿")
            print("AAA_Num :", AAA_Num)
            print("Pair_Num :", Pair_Num)   
            print("splitMahjongInfo : ", splitMahjongInfo)

        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------

        if traceLog:  
            print("Final - splitMahjongInfo : ", splitMahjongInfo)

        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------

        # 最終檢查, 是否滿足可以胡牌的搭子條件 (1個眼睛+4個刻搭)
        if AAA_Num == 4 and Pair_Num == 1:

            bExecuteSelfWho = False

            # 當下聽牌的牌章種類 超過 設定值要求, 可以胡牌
            if listenMahjongNum >= self.mahjongListenLimitNum:
                bExecuteSelfWho = True

            # 沒有設定聽牌數量的限制, 可以直接胡牌
            if listenMahjongNum == -1:
                bExecuteSelfWho = True          

            # 當下牌盒剩餘張數, 若沒設定下, 允許直接胡牌
            if mahjongBoxNum == -1:
                bExecuteSelfWho = True

            # 有傳入牌盒剩餘張數, 已經達到數量不足的認定, 允許直接胡牌
            if mahjongBoxNum >= 0 and mahjongBoxNum <= self.mahjongBoxLimitNum:
                bExecuteSelfWho = True                

            if bExecuteSelfWho == True:
                returnData[ 'actType' ] = MCD.EXECUTE_SELF_WHO
                returnData[ 'actMahjongName' ] = takeMahjong
                return  returnData
        
        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------           
        #----------------------------------------------------------------------

        # 選一張積分最高的牌, 並回傳(捨牌)
        maxPoint = max( mahjongPointList )
        #print("maxPoint :", maxPoint)

        maxIndexGroup = []

        for i in range(len(mahjongPointList)):
            if mahjongPointList[ i ] == maxPoint:
                maxIndexGroup.append( i )

        #print("maxIndexGroup :", maxIndexGroup)

        choiceMahjongIndex = self.choiceOneMahjong( maxIndexGroup )

        #print("choiceMahjongIndex :", choiceMahjongIndex)

        discardMahjongName = MCD.IndexToMjName[ choiceMahjongIndex ]

        returnData[ 'actType' ] = MCD.EXECUTE_DISCARD
        returnData[ 'actMahjongName' ] = discardMahjongName
        return  returnData                




    # 前提:能槓就槓, 別人打出的牌若可以明槓, 就先槓
    # 別家打出的牌, 要進行何種動作
    def checkOtherDiscardMahjong( self, onHandMahjong, discardMahjong, openMahjongInfo ):

        # 複製一份手上的牌, 後續都操作此資料
        saveOnHandMahjong = copy.copy( onHandMahjong )

        returnData = { 'errFlag':0, 'errMsg':None, 'actType':None, 'actMahjongName':None }

        #----------------------------------------------------------------------

        # 檢查手上牌與吃碰槓的資訊是否合法
        retInfo = self.checkOnHandAndOpenMahjongIsLegal( saveOnHandMahjong, openMahjongInfo )

        if retInfo['errFlag'] < 0:
            returnData[ 'errFlag' ] = retInfo[ 'errFlag' ]
            returnData[ 'errMsg' ] = retInfo[ 'errMsg' ]
            return  returnData
        
        # 檢查別家捨牌是否合法
        if self.checkMahjongNameIsLegal( discardMahjong, False ) < 0:
            returnData[ 'errFlag' ] = -1500
            returnData[ 'errMsg' ] = 'discardMahjong name is illegal.'
            return  returnData            
        
        #----------------------------------------------------------------------
               




    def debugMahjongListCountGroup( self, countGroup, titleName ):
        '''
        conSuitMahjongRangeMap = {
            MJ_SUIT_CHAR : ( 0, 1, 2, 3, 4, 5, 6, 7, 8 ),
            MJ_SUIT_DOT : ( 9, 10, 11, 12, 13, 14, 15, 16, 17 ),
            MJ_SUIT_BAMBOO : ( 18, 19, 20, 21, 22, 23, 24, 25, 26 ),
            MJ_SUIT_WORD : ( 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38 ),
            MJ_SUIT_JOKER : ( 39, 40, 41, 42, 43, 44, 45, 46 )
        '''
        data1 = '萬{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}'.format(countGroup[0],countGroup[1],countGroup[2],countGroup[3],countGroup[4],countGroup[5],countGroup[6],countGroup[7],countGroup[8])
        data2 = '筒{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}'.format(countGroup[9],countGroup[10],countGroup[11],countGroup[12],countGroup[13],countGroup[14],countGroup[15],countGroup[16],countGroup[17])
        data3 = '索{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}'.format(countGroup[18],countGroup[19],countGroup[20],countGroup[21],countGroup[22],countGroup[23],countGroup[24],countGroup[25],countGroup[26])        
        data4 = '字{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}{:4d}'.format(countGroup[27],countGroup[28],countGroup[29],countGroup[30],countGroup[31],countGroup[32],countGroup[33],countGroup[34],countGroup[35],countGroup[36],countGroup[37],countGroup[38])                

        print(titleName)
        print(data1)
        print(data2)
        print(data3)
        print(data4)


        



        





