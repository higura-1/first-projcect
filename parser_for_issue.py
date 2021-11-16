# for main
import sys
import csv
from github import Github
import os
import time
# for logfile
import my_log
import datetime
# for get_links
import re


print("\n\033[32m...........program booting...........\033[0m\n")

args = sys.argv

# using username and password or using an access token
if len(args) == 2:
    token = args[1]
    g = Github(f"{token}")
else:
    try:
        with open("github-token.txt", "r") as f:
            token = f.read()
            g = Github(f"{token}")
    except:
        print("github token = ",end="")
        token = input()
        g = Github(f"{token}")

def main():
    wd = os.getcwd()
    if os.getcwd()[-3:] == "src" or os.getcwd()[-4:] == "src/":
        pass
    else:
        os.chdir("./src")
        wd = os.getcwd()
    try:
        os.mkdir("./out_for_issue")
    except FileExistsError:
        pass
    try:
        os.mkdir("./out_for_issue/__logfile__")
    except FileExistsError:
        pass
    
    #ログ関係のインスタンス生成
    mylog = my_log.mylog(file_name = 'out_for_issue',
                        field_names = ["repo_id",
                                        "repo_org",
                                        "issue_id",
                                        "issue_title",
                                        "issue.number",
                                        "issue.etag",
                                        "issue_updated_at",
                                        "issue_created_at",
                                        "issue_closed_at",
                                        "issue_closed_by",
                                        "issue_labels",
                                        "issue_state",
                                        "pullrequest_id",
                                        "pullrequest_created_at",
                                        "pullrequest_closed_at",
                                        "pullrequest_merged_at",
                                        "pullrequest_state",
                                        "pullrequest_is_merged",
                                        "num_of_mov",
                                        "num_of_img",
                                        "datetime.datetime.now()",
                                        "issue.body"],
                        create_file = False)
    download_list = my_log.mylog(file_name = 'out_for_issue/__logfile__/download_list_issue.csv',
                                field_names = ['flag',
                                                'repo_name',
                                                'PR_id',
                                                'number',
                                                'url',
                                                'address',
                                                'img_or_mov'])
    movs_num_list = my_log.mylog(file_name = 'out_for_issue',
                                field_names = ['mov_number','mov_url'],
                                create_file = False)
    done_list = my_log.mylog(file_name = 'out_for_issue/__logfile__/logfile_parsing_issue_reponame.csv',
                            field_names = ['reponame_or_id','state'])

    # 選定済みリストの読み込み
    with open("results.csv", "r") as f:
        reader = csv.reader(f)
        l = [row for row in reader]
        my_repo_list = [row[0] for row in l[1:]]
    with open('out_for_issue/__logfile__/logfile_parsing_issue_reponame.csv', "r") as f:
        reader = csv.reader(f)
        l = [row for row in reader]
        my_repo_list2 = [row[0] for row in l[1:]]
        my_repo_list = list(set(my_repo_list) - set(my_repo_list2))

    for full_name_or_id in my_repo_list:
        try:
            r = g.get_repo(full_name_or_id)
        except Exception as e:
            r = None
            done_list.write([f'{full_name_or_id}', 'error'])
            done_list.export()
        print(f"get_repo = {r}")
        mov_exist = "n"

        # フォルダ作成
        abst_path = f"out_for_issue/{r.owner.login}_{r.name}"
        path = f"{wd}/{abst_path}"
        path_for_print = "src/"+myget_name_right(text=path, target="src/")
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        mylog.setup_file(f"{path}/parsing_issue_done_list.csv")

        repo_myorg = f"{r.owner.login}_{r.name}"
        repo_org = f"{r.owner.login}/{r.name}"
        total_count = 1

        for issue in r.get_issues(state="all"):
            issue_ID = issue.id
            # issue毎にid名のフォルダを作る
            f_path = f"out_for_issue/{repo_myorg}/{str(issue_ID)}"
            try:
                os.mkdir(f_path)
            except FileExistsError:
                pass

            # logを見て、実行済みなら以下の処理はしない
            if mylog.check_log(issue_ID, num1=2)[0] != -1:
                time.sleep(0.5)
                print(f"\033[2m{total_count:07}[{path_for_print}]({issue_ID})pass\033[0m")

            else:
                time_saver(3)
                mov_exist,mov_urls = get_mov_urls(issue.body)
                num_of_mov = 0
                img_exist,img_urls = get_img_urls(issue.body)
                num_of_img = 0
                if img_exist:
                    for i in img_urls:
                        num_of_img += 1
                if mov_exist:
                    counter = 1
                    movs_num_list.reset_buf()
                    movs_num_list.setup_file(f"{path}/{str(issue_ID)}/movs.csv")

                    for mov_url in mov_urls:
                        # img番号とURLの組を記述
                        download_list.write(["notDone",
                                            repo_org,
                                            issue_ID,
                                            counter,
                                            str(mov_url),
                                            f"{abst_path}/{str(issue_ID)}/mov{counter}{os.path.splitext(mov_url)[1]}",
                                            "mov"])
                        download_list.export()
                        movs_num_list.write([counter,
                                            str(mov_url)])
                        movs_num_list.export()
                        counter += 1
                    num_of_mov = counter - 1

                if mov_exist:
                    # 処理を表示
                    print(f"\033[32m{total_count:07}[{path_for_print}]({issue_ID})...done\033[0m")
                if mov_exist == False and img_exist == False:
                    print(f"{total_count:07}[{path_for_print}]({issue_ID})...done")
                pullrequest = issue.pull_request
                if pullrequest == None:
                    pullrequest_created_at = None
                    pullrequest_closed_at = None
                    pullrequest_merged_at = None
                    pullrequest_state = None
                    pullrequest_is_merged = None
                    pullrequest_id = None
                else:
                    pullrequest_id = int(myget_name_right(pullrequest.html_url,"/pull/"))
                    pullrequest = r.get_pull(number=pullrequest_id)
                    pullrequest_created_at = pullrequest.created_at
                    pullrequest_closed_at = pullrequest.closed_at
                    pullrequest_merged_at = pullrequest.merged_at
                    pullrequest_state = pullrequest.state
                    pullrequest_is_merged = pullrequest.merged
                mylog.write([r.id,
                            repo_org,
                            issue_ID,
                            issue.title,
                            issue.number,
                            issue.etag,
                            issue.updated_at,
                            issue.created_at,
                            issue.closed_at,
                            issue.closed_by,
                            [label.name for label in issue.labels],
                            issue.state,
                            pullrequest_id,
                            pullrequest_created_at,
                            pullrequest_closed_at,
                            pullrequest_merged_at,
                            pullrequest_state,
                            pullrequest_is_merged,
                            num_of_mov,
                            num_of_img,
                            datetime.datetime.now(),
                            issue.body])
                mylog.export()
                if mov_exist:
                    pass
                else:
                    os.rmdir(f_path)
            total_count += 1
                    
        # logのファイル出力
        mylog.export()
        done_list.write([f'{full_name_or_id}', 'success'])
        done_list.export()

    # 全処理終了
    download_list.export()
    print("\n\n\033[32m...........all tasks done!!...........\033[0m\n")




def time_saver(i):
    i = int(i)
    print("",end="",flush=True)
    print("[", end='', flush=True)
    for j in range(2*i):
        print("*", end='', flush=True)
        time.sleep(0.5)
    print("]", end='', flush=True)
    for j in range(2*i+2):
        print("\b", end='', flush=True)

def get_mov_urls(text):
    # gifまたはmov,mp4を含むかを判定
    mov_urls = None
    if type(text) == str:
        mov_urls = get_links_for_mov(text)

    if(mov_urls != None):# img_urlがあるかで判定
        return True, mov_urls
    else:
        return False, None

def get_img_urls(text):
    # jpg,pngを含むかを判定
    img_urls = None
    if type(text) == str:
        img_urls = get_links_for_img(text)

    if(img_urls != None):# img_urlがあるかで判定
        return True, img_urls
    else:
        return False, None

def get_links_for_mov(text):
    l_gif = re.findall(r"https://user-images.githubusercontent.com/[a-zA-Z_0-9/\-]+\.gif",  text)
    l_mp4 = re.findall(r"https://user-images.githubusercontent.com/[a-zA-Z_0-9/\-]+\.mp4",  text)
    l_mov = re.findall(r"https://user-images.githubusercontent.com/[a-zA-Z_0-9/\-]+\.mov",  text)
    l = l_gif + l_mp4 + l_mov
    if len(l) > 0:
        return l
    else:
        return None

def get_links_for_img(text):
    l_png = re.findall(r"/[a-zA-Z_0-9/\-]+\.png",  text)
    l_PNG = re.findall(r"/[a-zA-Z_0-9/\-]+\.PNG",  text)
    l_jpg = re.findall(r"/[a-zA-Z_0-9/\-]+\.jpg",  text)
    l_JPG = re.findall(r"/[a-zA-Z_0-9/\-]+\.JPG",  text)
    l_jpeg = re.findall(r"/[a-zA-Z_0-9/\-]+\.jpeg",  text)
    l = l_png + l_PNG + l_jpg + l_JPG + l_jpeg
    if len(l) > 0:
        return l
    else:
        return None

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

if(__name__=="__main__"):
    main()
