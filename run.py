from train.bureau.IntentWithoutEntity import Prediction as PredictionWOE
from train.bureau.IntentWithoutEntity import Preprocessing,LoadingData,DesignModel
from train.bureau.IntentWithEntity import Prediction as PredictionWE
from train.bureau.IntentWithEntity import Preprocessing,LoadingData,DesignModel

pred_objWOE = PredictionWOE()
pred_objWE = PredictionWE()



while 1:
    print("Enter query, Press 0 to exit")
    phrase = input()
    if phrase == '0':
        break
    final = {}
    intent = ""
    maximum = 0
    WOE,r = pred_objWOE.predict(phrase)
    WE,r = pred_objWE.predict(phrase)
    for key in WE:
        final[key] = WE[key] + WOE[key]
        if final[key]>maximum:
            intent = key
            maximum = final[key]
    print(intent)
    print(WOE[r])
    print(WE[r])
    print(maximum)
