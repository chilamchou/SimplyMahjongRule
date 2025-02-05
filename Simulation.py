# -*- coding: utf-8 -*-
__author__ = 'chilamchou'

import sys
import traceback
import time

import copy

import simplejson as json
import MahjongConstData as MCD
from SimplyMahjongRule import SimplyMahjongRule

########################################################################################################################

def loadJsonFile(filePath):
    try:
        with open(filePath, 'r', encoding="utf-8") as file:
            data = json.load(file)
            file.close()
            return data
    except Exception as e:
        raise Exception('loadJsonFile :' + str(traceback.format_exc()))

########################################################################################################################

def simu_display_argument_error():
    """
    執行檢測的參數不合法 , 藉由console輸出相關資訊
    """
    print("Error : simulation argument , exit(0)")
    print("example : python Simulation.py ./SimuConfig/SimuConfig.json")

########################################################################################################################

if __name__ == '__main__':

    # 判斷傳入參數數量是否合法
    argument_flag = True    
    if len(sys.argv) != 2:
        argument_flag = False

    if argument_flag == False:
        # 顯示錯誤資訊 , 並中止程序
        simu_display_argument_error()
        exit(0)

    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------

    # 讀取外部設定檔(json)
    config_file = sys.argv[1]
    config_data = loadJsonFile(config_file)
    print("read json config :", config_file)
    #print("config_data : ", config_data)

    SimuRuleName = config_data['SimuRuleName']

    SimuOnHandMahjong = config_data['SimuOnHandMahjong']

    SimuOpenMahjongInfo = config_data['SimuOpenMahjongInfo']

    SimuTakeType = config_data['SimuTakeType']  

    SimuTakeMahjong = config_data['SimuTakeMahjong']

    SimuMahjongBoxNum = config_data['SimuMahjongBoxNum']
    SimuNowListenNum = config_data['SimuNowListenNum']

    SimuDiscardMahjong = config_data['SimuDiscardMahjong']

    SimuMahjongBoxLimitNum = config_data['SimuMahjongBoxLimitNum']

    SimuMahjongListenLimitNum = config_data['SimuMahjongListenLimitNum']

    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------    

    start_clock = time.perf_counter()       # python3 停用 time.clock() 改用 time.perf_counter()

    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------    

    #test_start_onHandMahjong = ['A01','A01','A01','A04','A04','C06','C07','C08','C09','JK1','JK1','JK1','JK1']
    #test_OpenMahjongInfo = []
    #test_takeMahjong_List = [ 'JK2', 'A04', 'C06' ]

   
    simplyMahjongRule = SimplyMahjongRule()
    simplyMahjongRule.setRuleName( SimuRuleName )       # 設定本次要執行的玩法名稱 - 金勾釣, 方便後續擴充支援其他玩法

    simplyMahjongRule.setParameter( SimuMahjongBoxLimitNum, SimuMahjongListenLimitNum )

    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------    

    

    if SimuTakeType == 'ByOneSelf':     # 每次摸牌都是獨立驗證 , 不會隨著捨牌替換

        runTimeOnHandMahjong = copy.copy( SimuOnHandMahjong )    

        for i in range( len(SimuTakeMahjong) ):

            takeMahjong = SimuTakeMahjong[ i ]
            mahjongBoxNum = SimuMahjongBoxNum[ i ]
            mahjongListenNum = SimuNowListenNum[ i ]

            # 取得摸進這張牌後 , 要執行的動作
            desertRetData = simplyMahjongRule.checkSelfDiscardMahjong( runTimeOnHandMahjong, takeMahjong, SimuOpenMahjongInfo, mahjongBoxNum, mahjongListenNum )

            if desertRetData[ 'errFlag' ] != 0:
                print("****** Error ******")
                print(desertRetData)
                exit(0)
           
            print("DesertRetData : ", desertRetData)

    if SimuTakeType == 'BySequence':    # 每次手上牌都會隨著捨牌變化

        runTimeOnHandMahjong = copy.copy( SimuOnHandMahjong )

        for i in range( len(SimuTakeMahjong) ):

            takeMahjong = SimuTakeMahjong[ i ]
            mahjongBoxNum = SimuMahjongBoxNum[ i ]
            mahjongListenNum = SimuNowListenNum[ i ]

            desertRetData = simplyMahjongRule.checkSelfDiscardMahjong( runTimeOnHandMahjong, takeMahjong, SimuOpenMahjongInfo, mahjongBoxNum, mahjongListenNum )        

            if desertRetData[ 'errFlag' ] != 0:
                print("****** Error ******")
                print(desertRetData)
                exit(0)            

            if desertRetData[ 'actType' ] != MCD.EXECUTE_DISCARD:

                discardMahjong = 








    exit(0)
    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------        

    #desertRetData = simplyMahjongRule.checkSelfDesertMahjong( test_onHandMahjong, test_takeMahjong, test_OpenMahjongInfo )
    #print("DesertRetData : ", desertRetData)

    ret = simplyMahjongRule.checkOtherDiscardMahjong( test_start_onHandMahjong, 'A01', test_OpenMahjongInfo )

    print("ret : ", ret)

    end_clock = time.perf_counter()

    print("Elapsed time: {:.8f} seconds".format(end_clock - start_clock))



