import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import json
import os
import en_core_web_sm
from tensorflow import keras
from sklearn.metrics import roc_curve
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Input, Dense, GRU, Embedding, Bidirectional, Activation
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import SimpleRNN
from tensorflow.keras.layers import Conv1D
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import GlobalMaxPooling1D
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

class LoadingData():
            
    def __init__(self):
        train_file_path = os.path.join(os.getcwd(),"data")
        self.id2intent = {}
        self.intent2id = {}
        self.category_id=0
        print(train_file_path)
        data = {}
        for file in os.listdir(train_file_path):
            f = open(os.path.join(train_file_path,str(file)))
            # print(str(file))
            dat = json.load(f)
            for key in dat:
                data[key] = dat[key]
                self.intent2id[key] = self.category_id
                self.category_id+=1
        self.data = data
        training_data=self.data_helper()
        self.train_data_frame = pd.DataFrame(training_data, columns =['query', 'intent','category'])   
        for key in self.intent2id:
            self.id2intent[self.intent2id[key]]=key
        self.train_data_frame = self.train_data_frame.sample(frac = 1)
        # print(self.train_data_frame)

    def data_helper(self):
        # print(self.data)
        # for phrase in self.data["data"]:
        #     # print(phrase)
        #     if phrase["intent"] not in intent2id:   
        #         intent2id[phrase["intent"]] = category_id
        #         category_id+=1
        #     entities = []
        #     for entity in phrase["entities"]:
        #         entities.append(phrase["text"][entity["start"]:entity["end"]])
        #     for entity in entities:
        #         phrase["text"] = phrase["text"].replace(entity,"")
        #     sent_list.append((phrase["text"],phrase["intent"],intent2id[phrase["intent"]]))
        # self.category_id = category_id

        sent_list = list()
        for key in self.data:
            json_dict = self.data[key]
            for i in json_dict:
                each_list = i['data']
                sent =""
                for i in each_list:
                    if 'entity' not in i.keys():
                        sent = sent + i['text']+ " "
                sent =sent[:-1]
                for i in range(3):
                    sent = sent.replace("  "," ")
                sent_list.append((sent,key,self.intent2id[key]))
        return sent_list


class Preprocessing():
    def __init__(self):
        self.x_train = None
        self.y_train = None
        self.x_valid = None
        self.y_valid = None
        self.spacy_model = en_core_web_sm.load()
        self.tokenizer = None

    def createData(self, data):
        self.tokenizer = Tokenizer(num_words=None)
        self.max_len = 50
        self.x_train, self.x_valid, self.y_train, self.y_valid = train_test_split(data.train_data_frame['query'].tolist(),data.train_data_frame['category'].tolist(),test_size=0.1)
        self.tokenizer.fit_on_texts(list(self.x_train) + list(self.x_valid))
        self.x_train = self.tokenizer.texts_to_sequences(self.x_train)
        self.x_valid = self.tokenizer.texts_to_sequences(self.x_valid)

        #zero pad the sequences
        self.x_train = pad_sequences(self.x_train, maxlen=self.max_len)
        self.x_valid = pad_sequences(self.x_valid, maxlen=self.max_len)
        self.y_train = to_categorical(self.y_train)
        self.y_valid = to_categorical(self.y_valid)
        self.word_index = self.tokenizer.word_index
        
    def getSpacyEmbeddings(self,sentneces):
        sentences_vectors = list()
        for item in sentneces:
            query_vec = self.spacy_model(item) 
            sentences_vectors.append(query_vec.vector)
        return sentences_vectors
    


class DesignModel():
    def __init__(self,preprocess_obj):
        self.model = None
        self.x_train = preprocess_obj.x_train
        self.y_train = preprocess_obj.y_train
        self.x_valid = preprocess_obj.x_valid
        self.y_valid = preprocess_obj.y_valid
        
    def simple_rnn(self,preprocess_obj,classes):
        
        self.model = Sequential()
        self.model.add(Embedding(len(preprocess_obj.word_index) + 1,100,input_length=preprocess_obj.max_len))
        self.model.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
        self.model.add(Dense(100, activation='relu'))
        self.model.add(Dense(classes, activation='softmax'))
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        
        
    def model_train(self,batch_size,num_epoch):
        print("Fitting to model")
        self.model.fit(self.x_train, self.y_train, batch_size=batch_size, epochs=num_epoch, validation_split=0.1)
        print("Model Training complete.")
        self.model.save("models/IntentWithoutEntity"+".h5")




class Prediction():
    def __init__(self):
        # print("INIT___________________")
        with open("models/preprocess_obj.pkl","rb") as f1:
            preprocess_obj = pickle.load(f1)
        print("preprocess loaded-----------------")
        model= keras.models.load_model("models/IntentWithoutEntity"+".h5")
        self.model = model
        self.tokenizer = preprocess_obj.tokenizer
        self.max_len = preprocess_obj.max_len
        
    
    def predict(self,query):
        # print("PREDICT__________________")
        with open("models/id2intent.pkl","rb") as f3:
            id2intent = pickle.load(f3)
        query_seq = self.tokenizer.texts_to_sequences([query])
        query_pad = pad_sequences(query_seq, maxlen=self.max_len)
        pred = self.model.predict(query_pad)
        predi = np.argmax(pred)
        # print("--------------------------")
        # print(pred)
        # print(pred[0][predi])
        # if  pred[0][predi]<0.5:
        #     return "Sorry, I don't understand!!"
        result = id2intent[predi]
        resulti = {}
        for i in range(len(pred[0])):
            resulti[id2intent[i]] = pred[0][i]
        return resulti, result

if __name__ == '__main__':
    data = LoadingData()
    preprocess_obj = Preprocessing()
    preprocess_obj.createData(data)
    model_obj = DesignModel(preprocess_obj)
    model_obj.simple_rnn(preprocess_obj,data.category_id)
    model_obj.model_train(64,5)

    with open("models/preprocess_obj.pkl","wb") as f:
        pickle.dump(preprocess_obj,f)

    with open("models/id2intent.pkl","wb") as f3:
        pickle.dump(data.id2intent,f3)

