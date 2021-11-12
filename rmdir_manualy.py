import os
import glob
from tqdm import tqdm

def myget_name_right(text, target):
    # ${target}より後を抽出したい
    idx = text.find(target)
    t = text[idx+len(target):]
    return t

print("\n\033[32m...........program booting...........\033[0m\n")

# src/で実行
wd = os.getcwd()

repos = glob.glob(f"{wd}/out_for_issue/*")
for repo in repos:
    print(myget_name_right(repo,"out_for_issue/"))
    if repo == f"{wd}/out_for_issue/__logfile__":
        print("   ----->  pass")
    else:
        issues = glob.glob(f"{repo}/*")
        loop = len(issues)
        for i in tqdm(range(0,loop)):
            issue = issues[i]
            if issue == f"{repo}/parsing_issue_done_list.csv":
                pass
            else:
                items = glob.glob(f"{issue}/*")
                if len(items) == 0:
                    os.rmdir(issue)
                else:
                    pass

print("\n\n\033[32m...........all tasks done!!!...........\033[0m\n")


