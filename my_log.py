import requests
import os
import csv
slackTOKEN = 'xoxp-2252449405863-2273375697380-2264166547429-e76b6ec75e8fc5ba14204624b8637d6e'
slackCHANNEL = 'api-nortification'
slackURL = "https://slack.com/api/chat.postMessage"
headers = {"Authorization": "Bearer "+slackTOKEN}

class mylog():
    def __init__(self, file_name, field_names, create_file=True):
        self.field_names = field_names
        self.csv_file = file_name
        self.body = []
        if create_file == True:
            if os.path.exists(file_name):
                pass
            else:
                self.csv_file = file_name
                os.system("touch {}".format(file_name))
                self.body.append(self.field_names)
                self.export()
        elif create_file == False:
            pass

    def setup_file(self, file_name):
        if self.body != []:
            self.export()
        self.csv_file = file_name
        if os.path.exists(file_name):
            pass
        else:
            self.csv_file = file_name
            os.system("touch {}".format(file_name))
            self.body.append(self.field_names)
            self.export()

    def check_log(self,target, num1, num2=None):
        # 各行の(num1)項目を先頭から調べて、(target)に一致する行が見つかったらそこの行番号(idx)を返す
        # オプション：(num2)を指定すれば、(idx)行の(num2)項目を返す

        # ファイル読み込み
        with open(self.csv_file, mode='r') as f_in:
            reader = csv.reader(f_in)
            l = [row for row in reader]
            data_array = [row[num1] for row in l[1:]]
        # 行の検索
        index_position = None
        for idx in range(len(data_array)):
            if str(target) == str(data_array[idx]):
                index_position = idx
                break
        if index_position == None:
            return -1, None
        else:
            if num2 != None:
                return idx, l[idx][num2]
            else:
                return idx, None

    def write(self, dict):
        self.body.append(dict)
    
    def rewrite(self,dict,idx):# idx : 0〜
        if self.body != []:
            self.export()
        # idx番目のcsvを書き換える
        with open(self.csv_file, mode='r') as f_in:
            reader = csv.reader(f_in)
            l = [row for row in reader]
            if len(l) <= 1:
                print(f"\033[31mDataFile( {self.csv_file} ) is empty, so you should execute mylog.write(~) not mylog.rewrite(~).\033[0m)")
            l[idx+1]=dict
        with open(self.csv_file, 'w') as f_out:
            writer = csv.writer(f_out)
            writer.writerows(l)


    def export(self):
        with open(self.csv_file, 'a') as f:
            writer = csv.writer(f)
            writer.writerows(self.body)
            self.body = []

    def reset_buf(self):
        self.body =[]

    def info(self, message):
        if self.body != []:
            self.export()
        self.slack_do(message)

    def slack_do(self, message):
        slackData  = {
            'channel': slackCHANNEL,
            'text': message
            }
        r = requests.post(slackURL, headers=headers, data=slackData)