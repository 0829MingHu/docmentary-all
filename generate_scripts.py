from youtubesearchpython import *
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from math import ceil

proxy = 'socks5://127.0.0.1:10808'
# os.environ['HTTP_PROXY']=proxy
# os.environ['HTTPS_PROXY']=proxy
#频道ID
channels=['UCDPk9MG2RexnOMGTD-YnSnA']
if os.path.exists('videos.txt'):
    os.remove('videos.txt')

def get_all_channel_video(channel_id):
    playlist = Playlist(playlist_from_channel_id(channel_id))
    videos=playlist.videos
    print(f'Videos Retrieved: {len(playlist.videos)}')
    # videos={video['id']:video for video in videos}
    # get_video_infos(videos)
    while playlist.hasMoreVideos:
        print('Getting more videos...')
        playlist.getNextVideos()
        print(f'Videos Retrieved: {len(playlist.videos)}')
    print('get more videos info...')
    videos = playlist.videos
    videos = {video['id']: video for video in videos}
    videos = get_video_infos(videos)    

def get_video_infos(videos:dict):
    tasks=[]
    with ThreadPoolExecutor(max_workers=50) as executor:
        for video in videos:
            tasks.append(executor.submit(Video.getInfo,videos[video]['link']))
        for future in as_completed(tasks):
            info=future.result()
            videos[info['id']]['description']=info['description']
    with open('videos.txt','a',encoding='utf-8') as f:
        for video in videos:
            desc=videos[video]["description"].replace("\n","")
            f.write(f'{videos[video]["id"]}\t{videos[video]["title"]}\t{desc}\n')

def generate_script():
    out2 = open("all_qsub.sh","w")
    code_path='./code'
    os.makedirs(code_path,exist_ok=True)
    with open('videos.txt','r',encoding='utf-8') as f:
        #每100个视频一个任务
        video_nums=len(f.readlines())
        task_nums=ceil(video_nums/100)
        for i in range(task_nums):
            out = open(f'{code_path}/run_{i}.sh','w')
            out.write(f"""#!/bin/bash
#SBATCH -N 1
#SBATCH --partition=batch
#SBATCH -J {i}
#SBATCH -o {i}.%J.out
#SBATCH --mail-user=xiaoming-sudo@outlook.com
#SBATCH --mail-type=ALL
#SBATCH --time=24:00:00
#SBATCH --mem=50G
#SBATCH --ntasks-per-node=20\n""")
            out.write(f"""python down_main.py {i*100} {(i+1)*100}\n""")
            out2.write(f"sbatch {code_path}/run_{i}.sh\n")
            out.close()
    out2.close()



def main():
    for vid in channels:
        get_all_channel_video('UCDPk9MG2RexnOMGTD-YnSnA')
    # print('get all videos:',len(videos))
    generate_script()
    del os.environ['HTTP_PROXY']
    del os.environ['HTTPS_PROXY']