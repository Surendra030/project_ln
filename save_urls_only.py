import json
from mega import Mega

def login_data(title,index,data):
    email = 'afg154007@gmail.com'
    password = 'megaMac02335!'
    mega = Mega()
    m = mega.login(email,password)
    title = f"{index}_title"
    folder = m.create_folder(title)
    folder_handle = folder.get(title)
    m.upload(f"{title}.json",folder_handle)
def main_fun(data, title,index):
    with open(title,'w',encoding='utf-8')as f:
        json.dump(data,f,indent=4)
    login_data(title,index,data)
    
    


