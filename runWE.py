from train.bureau.IntentWithEntity import Prediction,Preprocessing,LoadingData,DesignModel

pred_obj = Prediction()
while 1:
    print("Enter query, Press 0 to exit")
    phrase = input()
    if phrase == '0':
        break
    resulti, result = pred_obj.predict(phrase)
    print(result)
    print(resulti[result])