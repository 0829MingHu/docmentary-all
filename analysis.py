import shutil
import webvtt
import os 
import pandas as pd


df = pd.read_excel("./1.xlsx")
df = df.dropna(axis=1,how="all")
df = df.fillna(method="ffill")
df = df.set_index("family")
df = df.drop_duplicates()
actions=["eat","drink","hunt/kill/chase","mate/mating/copulate/copulating/copulation/sex","feed baby/feed babies/feed cub","nurse/nursing/breastfeed","birth/give birth/childbirth","fight/battle/duel","sleep/nap","pee","vomit/throw up"]
action_dict={}
for action in actions:
    for s in action.split('/'):
        action_dict[s]=action

from_path='downloads'
to_path='result'

#vtt提取文字
def extract_vtt(vtt_path):
    vtt=webvtt.read(vtt_path)
    content=''
    for i in vtt:
        content+=i.text+'\n'
    return content

#建目录
def create_folders():
    #根据Excel目录建目录
    folder_dict={}
    for family,info in df.iterrows():
        genus=info['genus']
        animal=info['keyword']
        if family.endswith(' '):
            family=family[:-1]
        if genus.endswith(' '):
            genus=genus[:-1]
        if animal.endswith(' '):
            animal=animal[:-1]
        folder_animal=animal.split('/')[0]
        folder=f'{to_path}/{family}/{genus}/{folder_animal}'
        os.makedirs(folder,exist_ok=True)
        folder_dict[animal]=folder
    return folder_dict

#处理下载的文件
def handle_files(folder_dict,action_dict):
    for vid in os.listdir(from_path):
        for file in os.listdir(os.path.join(from_path,vid)):
            #分析txt文件
            content=''
            mp4_name=None 
            from_mp4_path=None 
            m4a_name=None 
            from_m4a_path=None
            vtt_name=None
            from_vtt_path=None
            if file.endswith('.txt'):
                with open(os.path.join(from_path,vid,file),encoding='utf-8') as f:
                    content+=f.read()+'\n'
            #分析webvtt文件
            if file.endswith('.vtt'):
                content+=extract_vtt(os.path.join(from_path,vid,file))
                vtt_name=file
                from_vtt_path=os.path.join(from_path,vid,file)
            if file.endswith('.mp4'):
                mp4_name=file
                from_mp4_path=os.path.join(from_path,vid,file)
            if file.endswith('.m4a'):
                m4a_name=file
                from_m4a_path=os.path.join(from_path,vid,file)
        #分析animal和action组合
        for animals in folder_dict:
            for animal in animals.split('/'):
                #动作
                for action in action_dict:
                    if animal in content and action in content:
                        #将mp4\m4a\vtt文件移动到对应的文件夹
                        target_folder=os.path.join(folder_dict[animals],action_dict[action])
                        print(f'找到组合{animals}和{action}->{target_folder}')
                        os.makedirs(target_folder,exist_ok=True)
                        if mp4_name:
                            target_mp4_path=os.path.join(target_folder,mp4_name)
                            if not os.path.exists(target_mp4_path):
                                #复制
                                shutil.copyfile(from_mp4_path,target_mp4_path)
                        if m4a_name:
                            target_m4a_path=os.path.join(target_folder,m4a_name)
                            if not os.path.exists(target_m4a_path):
                                #复制
                                shutil.copyfile(from_m4a_path,target_m4a_path)
                        if vtt_name:
                            target_vtt_path=os.path.join(target_folder,vtt_name)
                            if not os.path.exists(target_vtt_path):
                                #复制
                                shutil.copyfile(from_vtt_path,target_vtt_path)

        



if __name__=='__main__':
    folder_dict=create_folders()
    handle_files(folder_dict,action_dict)

