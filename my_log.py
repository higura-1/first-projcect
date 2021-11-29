from re import L
import requests
import os
import sys
import csv
import chardet

# 動作条件
# カンマ区切り形式のcsv形式であること
# export()した時に、初めて実ファイルに書き出される


class mylog():
    def __init__(self, file_name, field_names=None,create_file=True,encoding=None):
        self.field_names = field_names
        self.csv_file = file_name
        self.encoding = encoding
        self.list = []
        if create_file == True:
            self.setup_file(file_name=file_name,encoding=encoding)
        elif create_file == False:
            pass
        self.slackTOKEN = None
        self.slackCHANNEL = None
        self.slackURL = None
        self.headers = None

    def setup_file(self, file_name,encoding=None):
        self.csv_file = file_name
        self.encoding = encoding
        if os.path.exists(file_name):
            if self.field_names == None:
                with open(file_name, mode='r',encoding=self.encoding) as f:
                    reader = csv.reader(f)
                    l = [row for row in reader]
                    if l == []:
                        self.list.append(self.field_names)
                        self.export()
                    else:
                        self.field_names = l[0]
                        if len(l) > 1: self.list = l[1:]
                        else: self.list = []
            else:# field_names != None
                with open(file_name, mode='r',encoding=self.encoding) as f:
                    reader = csv.reader(f)
                    l = [row for row in reader]
                    if len(l) > 0: 
                        self.field_names = l[0]
                        if len(l) > 1: self.list = l[1:]
                        else: self.list = []
        else:
            os.system("touch {}".format(file_name))
            if self.field_names == None:
                raise Exception("Error: my_log needs field_names when my_log.setup_file() execute make_new_file.")
            self.export()

    def set_field_names(self,dict):
        self.field_names = dict

    def change_field_names(self,item1,item2,export=False):
        colm = self.get_collumn_id(item1)
        if colm == None:
            return None
        else:
            self.field_names[colm] = item2
        if export == True:
            self.export()
        return True

    def set_charset(self, charset=None):
        if charset == None:
            with open(self.csv_file, 'rb') as f:  # バイナリファイルとしてファイルをオープン
                b = f.read()
            try:
                encode_tmp = chardet.detect(b)['encoding']
            except Exception as e:
                print("Error:-------my_log set_charset error-------")
                return False
            if encode_tmp == None:
                self.encoding = charset
            else:
                self.encoding = encode_tmp
        else:
            self.encoding = charset
        return self.encoding

    def get_charset(self):# Noneの場合もある(ファイルが存在しない時)
        return self.encoding
    
    def get_collumn_id(self, target):
        i = 0
        for name in self.field_names:
            if name == target:
                return i
            i += 1
        return None

    def get_namefield(self,number):
        if type(number) == int and number <= len(self.field_names)-1:
            return self.field_names[number]
        else :
            return None
    
    def get_namefields(self):
        return self.field_names

    def get_len(self, include_name_field=True):
        if include_name_field == True:
            return len(self.list)+1
        else:
            return len(self.list)

    def get_rows(self, include_name_field=True):
        if include_name_field == True:
            if self.list == []:
                return self.field_names
            else:
                return self.field_names + self.list
        else:
            return self.list

    def get_specific_row(self,index):
        if type(index) == int and 0 == index:
            return self.field_names
        if type(index) == int and 0 < index and index <= len(self.list):
            return self.list[index-1]
        else:
            return False
    
    def get_columns(self,column_id,include_name_field=False):
        # cation: column_id -> dict (not list)
        out_dict = {}
        if include_name_field == True:
            out_dict.setdefault(0,self.field_names[column_id])
        out_dict_setdefault = out_dict.setdefault
        for i in range(0, len(self.list)):
            out_dict_setdefault(i+1, self.list[i][column_id])
        return out_dict

    def get_specific_item(self,index,column_id):
        if type(index)==int and 0==index:
            return self.field_names[column_id]
        elif type(index)==int and 0<index and index < self.get_len():
            return self.list[index-1][column_id]
        else:
            return False


    def is_include(self,target,column_id):
        # 各行の(column1)項目を先頭から調べて、(target)に一致する行が見つかったらTrueを返す
        # ファイル読み込み
        data_array = [row[column_id] for row in self.list[1:]]
        data_array = set(data_array)
        return target in data_array

    def search_target(self,target, column1, column2=None):
        # 各行の(column1)項目を先頭から調べて、(target)に一致する行が見つかったらそこの行番号(idx)を返す
        # オプション：(column2)を指定すれば、(idx)行の(column2)項目を返す

        # ファイル読み込み
        data_array = [row[column1] for row in self.list]
        # 行の検索
        index_position = None
        for idx in range(len(data_array)):
            if str(target) == str(data_array[idx]):
                index_position = idx+1
                break
        if column2==None and index_position == None:
            return -1
        elif column2!=None and index_position == None:
            return -1,None
        else :# index_position == int
            if column2 == None:
                return index_position
            else:# column2 == int
                return index_position, self.list[idx][column2]

    def write_row(self, dict, export=False):
        self.list.append(dict)

        if export == True:
            self.export()

    def rewrite_row(self, dict, idx, export=False):
        # idx番目のcsvを書き換える
        if idx == 0:
            self.field_names = dict
        elif idx > 0 and len(self.list) < 1:
            print(f"\033[31mDataFile( {self.csv_file} ) is empty, so you should execute mylog.write(~) not mylog.rewrite(~).\033[0m)")
        else:
            self.list[idx-1]=dict

        if export == True:
            self.export()

    def rewrite_specific_item(self,idx,column_id,new_data,mode="w", export=False):
        if mode == "w":
            self.list[idx-1][column_id] = new_data
        elif mode == "a":
            self.list[idx-1][column_id] += new_data

        if export == True:
            self.export()

    def export(self):
        with open(self.csv_file, mode="w",newline="",encoding=self.encoding) as f:
            writer = csv.writer(f)
            l = []
            l.append(self.field_names)
            for i in self.list:
                l.append(i)
            writer.writerows(l)

    def reset_file(self):
        self.list = []
        self.export()


    def setup_slack(self, offset="",charset="ascii"):
        with open(f"slack_nortification_token{offset}.config", mode='r',encoding=charset) as conf:
            self.slackTOKEN = conf.read().split()[0]
        with open(f"slack_nortification_channel{offset}.config",mode="r",encoding=charset) as conf:
            self.slackCHANNEL = conf.read().split()[0]
        self.slackURL = "https://slack.com/api/chat.postMessage"
        self.headers = {"Authorization": "Bearer "+self.slackTOKEN}

    def slack(self, message):
        if self.slackTOKEN == None:
            return False
        else :
            slackData  = {
                'channel': self.slackCHANNEL,
                'text': message}
            r = requests.post(self.slackURL, headers=self.headers, data=slackData)
            if r == None:
                return False
            else :
                return True
