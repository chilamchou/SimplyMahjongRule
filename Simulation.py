# -*- coding: utf-8 -*-
__author__ = 'chilamchou'

import traceback
import time
import simplejson as json
import MahjongConstData as MCD
from SimplyMahjongRule import SimplyMahjongRule

########################################################################################################################

def loadJsonFile(filePath):
    try:
        with open(filePath, 'r') as file:
            data = json.load(file)
            file.close()
            return data
    except Exception as e:
        raise Exception('loadJsonFile :' + str(traceback.format_exc()))

########################################################################################################################

def simu_display_argument_error():
    """
    執行模擬快測需要的參數不合法 , 藉由console輸出相關資訊
    """
    print("Error : simulation argument !!")
    print("example : python Simulation.py SimulationConfig.json")

########################################################################################################################





########################################################################################################################

if __name__ == '__main__':

    start_clock = time.perf_counter()       # python3 停用 time.clock() 改用 time.perf_counter()

    # 手上牌13張   
    #test_onHandMahjong = ['A01','A01','A01','A02','A03','A04','C01','C01','W04','W04','W04','JK1','JK2']
    #test_OpenMahjongInfo = []
    #test_takeMahjong = 'W01'

    # 手上牌13張
    #test_onHandMahjong = ['A01','A01','A01','A02','A02','A02','W01','W01','JK1','JK1','JK1','JK2','JK2']
    #test_OpenMahjongInfo = []
    #test_takeMahjong = 'W01'    

    # 手上牌13張 .. 多賴子
    #test_onHandMahjong = ['JK1','JK1','JK1','JK1','JK2','JK2','JK2','JK2','JK3','JK3','JK3','JK3','W01']
    #test_OpenMahjongInfo = []
    #test_takeMahjong = 'W02'        

    # 手上牌13張 .. 多賴子
    #test_onHandMahjong = ['JK1','JK1','JK1','JK1','JK2','JK2','JK2','JK2','JK3','JK3','JK3','JK3','W01']
    #test_OpenMahjongInfo = []
    #test_takeMahjong = 'JK1'            

    # 手上牌13張 .. 多賴子
    #test_onHandMahjong = ['A01','A01','A02','A02','A03','JK1','JK1','JK1','JK2','JK2','JK2','JK3','JK3']
    #test_OpenMahjongInfo = []
    #test_takeMahjong = 'W02'                


    # 手上牌13張 .. 多賴子
    test_onHandMahjong = ['A01','A01','A02','A02','A03','C01','C02','C02','C03','JK2','JK2','JK3','JK3']
    test_OpenMahjongInfo = []
    test_takeMahjong = 'JK1'    

    # 手上牌10張   
    #test_onHandMahjong = ['A01','A01','A01','A02','A03','A04','C01','C01','JK1','JK2']
    #test_OpenMahjongInfo = [ {'openType':MCD.OPEN_PONG, 'mahjong':'W04'} ]
    #test_takeMahjong = 'W01'
    
    # 手上牌10張   
    #test_onHandMahjong = ['A01','A01','A01','A02','A03','A04','C01','C01','JK1','JK2']
    #test_OpenMahjongInfo = [ {'openType':MCD.OPEN_KONG, 'mahjong':'W04'} ]
    #test_takeMahjong = 'W01'

    # 手上牌10張   
    #test_onHandMahjong = ['A01','A01','A01','A02','A03','A04','C01','C01','JK1','JK2']
    #test_OpenMahjongInfo = [ {'openType':MCD.OPEN_CONCEALED_KONG, 'mahjong':'W04'} ]
    #test_takeMahjong = 'W01'    

    # 手上牌7張   
    #test_onHandMahjong = ['A01','A01','A01','C01','C01','JK1','JK2']
    #test_OpenMahjongInfo = [ 
    #    { 'openType':MCD.OPEN_CONCEALED_KONG, 'mahjong':'W04'},
    #    { 'openType':MCD.OPEN_CHOW, 'sequence':'B02', 'mahjong':'A05' }
    #    ]
    #test_takeMahjong = 'W01'        

    # 手上牌7張   
    #test_onHandMahjong = ['A01','A01','A01','C01','C01','JK1','JK2']
    #test_OpenMahjongInfo = [ 
    #    { 'openType':MCD.OPEN_CONCEALED_KONG, 'mahjong':'W04'},
    #    { 'openType':MCD.OPEN_CHOW, 'sequence':'A02', 'mahjong':'A04' },
    #    { 'openType':MCD.OPEN_CHOW, 'sequence':'A02', 'mahjong':'A04' },
    #    { 'openType':MCD.OPEN_CHOW, 'sequence':'A02', 'mahjong':'A04' }
    #    ]
    #test_takeMahjong = 'W01'            


    # 手上牌13張 .. 多賴子
    #test_start_onHandMahjong = ['A01','A01','A02','A02','A03','C01','C02','C02','C03','JK2','JK2','JK3','JK3']
    #test_OpenMahjongInfo = []
    #test_takeMahjong_List = [ 'JK1', 'C07', 'C01' ]

    test_start_onHandMahjong = ['A01','A01','A01','A04','A04','C06','C07','C08','C09','JK1','JK1','JK1','JK1']
    test_OpenMahjongInfo = []
    test_takeMahjong_List = [ 'JK2', 'A04', 'C06' ]    

    
    simplyMahjongRule = SimplyMahjongRule()

    simplyMahjongRule.setRuleName('CrazyGoldHook')      # 設定本次要執行的玩法名稱 - 金勾釣, 方便後續擴充支援其他玩法

    #desertRetData = simplyMahjongRule.checkSelfDesertMahjong( test_onHandMahjong, test_takeMahjong, test_OpenMahjongInfo )
    #print("DesertRetData : ", desertRetData)

    '''
    for takeIndex in range( len(test_takeMahjong_List) ):

        mahjong = test_takeMahjong_List[takeIndex]

        print("onHandMahjong : ", test_start_onHandMahjong , mahjong )

        desertRetData = simplyMahjongRule.checkSelfDesertMahjong( test_start_onHandMahjong, mahjong, test_OpenMahjongInfo )

        print("DesertRetData : ", desertRetData)        

        if desertRetData['errFlag'] == 0:

            if desertRetData['actType'] == MCD.EXECUTE_DISCARD:

                actMahjongName = desertRetData['actMahjongName']

                if mahjong == actMahjongName:
                    pass
                else:
                    test_start_onHandMahjong.remove( actMahjongName )
                    test_start_onHandMahjong.append( mahjong )
    '''

    ret = simplyMahjongRule.checkOtherDiscardMahjong( test_start_onHandMahjong, 'A01', test_OpenMahjongInfo )

    print("ret : ", ret)

    end_clock = time.perf_counter()

    print("Elapsed time: {:.8f} seconds".format(end_clock - start_clock))



