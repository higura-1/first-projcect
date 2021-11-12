import sys
import csv 
import os
from tqdm import tqdm
import time

print("\n\033[32m...........program booting...........\033[0m\n")

def myget_name_left(text, target):
    # ${target}より前を抽出したい
    idx = text.find(target)
    t = text[:idx]
    return t
def myget_name_right(text, target):
    # ${target}より後を抽出したい
    idx = text.find(target)
    t = text[idx+len(target):]
    return t

with open("./results.csv", mode='r') as f_in:
    reader = csv.reader(f_in)
    l = [row for row in reader]
    l = l[1:]
    l = [row[0] for row in l]

wd = os.getcwd()

for repo in l:
    dir_name = myget_name_left(repo,"/")+"_"+myget_name_right(repo,"/")
    file_name = f"{wd}/out_for_issue/{dir_name}/parsing_issue_done_list.csv"
    x = 0
    x2 = 0
    y = 0
    y2 = 0
    with open(file_name, mode='r') as f_in:
        reader = csv.reader(f_in)
        l = [row for row in reader]

        for i in tqdm(range(1,len(l))):
            temp = l[i]
            numofimg = int(temp[19])
            numofmov = int(temp[18])

            if numofimg == 0:
                x += 1
            if numofimg >= 1:
                x2 += 1

            if numofmov == 0:
                y += 1
            if numofmov >= 1:
                y2 += 1

    print(f"num_of_issues (total) = {len(l)-1}")
    print(f"num_of_issues (including_img) = {x2:3}({round(100*x2/(len(l)-1), 2)}%)")
    print(f"num_of_issues (including_mov) = {y2:3}({round(100*y2/(len(l)-1), 2)}%)")

print("\n\n\033[32m...........all tasks done!!...........\033[0m\n")