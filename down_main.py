from yt_dlp import YoutubeDL
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import sys
import shutil



YL_OPTIONS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'writeautomaticsub': True,
    # 'skip_download': True,
    'writesubtitles': True,
    # "nooverwrites": True,
    "extractor-args":"youtube:player-client=web",
    # 'proxy':'socks5://127.0.0.1:10808'
}
YDL_OPTIONS_EXTRACT = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'writeautomaticsub': True,
    # 'skip_download': True,
    'writesubtitles': True,
    # "nooverwrites": True,
    "extractor-args":"youtube:player-client=web",
    # 'proxy':'socks5://127.0.0.1:10808'
    #"age-limit":12,
}



YDL_OPTIONS_AUDIO_ONLY = {
    'format': 'bestaudio[ext=m4a]',
    # "nooverwrites": True,
}
download_root_path='downloads'
os.makedirs(download_root_path,exist_ok=True)


def download(video):
    #写txt文件
    download_path=os.path.join(download_root_path,video['id'])
    os.makedirs(download_path,exist_ok=True)
    with open(f'{download_path}/{video["id"]}.txt','w',encoding='utf-8') as f:
        f.write(f"{video['title']}\n{video['description']}")
    #下载
    # YL_OPTIONS['outtmpl'] = str(path / (arg + ".mp4"))
    YL_OPTIONS['outtmpl'] = os.path.join(download_path,video['id']+'.mp4')
    with YoutubeDL(YL_OPTIONS) as ydl:
        try:
            if not os.path.exists(os.path.join(download_path,video['id']+'.mp4')):
                v = ydl.extract_info("https://www.youtube.com/watch?v={}".format(video['id']), download=True)
            YDL_OPTIONS_AUDIO_ONLY['outtmpl'] = os.path.join(download_path,video['id']+'.m4a')
            if not os.path.exists(os.path.join(download_path,video['id']+'.m4a')):
                with YoutubeDL(YDL_OPTIONS_AUDIO_ONLY) as ydl_audio:
                    audio = ydl_audio.extract_info("https://www.youtube.com/watch?v={}".format(video['id']), download=True)
            
        except Exception:
            if not os.path.exists(os.path.join(download_path,video['id']+'.mp4')):
                v = ydl.extract_info("https://www.youtube.com/watch?v={}".format(video['id']), download=False)
        try:
            #重命名
            for file in os.listdir(download_path):
                if file.endswith('.f137.mp4'):
                    shutil.move(os.path.join(download_path,file),os.path.join(download_path,video['id']+'.mp4'))
                if file.endswith('.f140.m4a'):
                    shutil.move(os.path.join(download_path,file),os.path.join(download_path,video['id']+'.m4a'))
                if file.endswith('.f137.mp4.part'):
                    shutil.move(os.path.join(download_path,file),os.path.join(download_path,video['id']+'.mp4'))
                if file.endswith('.temp.mp4'):
                    #删除
                    os.remove(os.path.join(download_path,file))
                if file.endswith('.temp.m4a'):
                    #删除
                    os.remove(os.path.join(download_path,file))
        except Exception as e:
            print(e)
        return video['id']+' done'

def main():
    
    start_idx,end_idx=int(sys.argv[1]),int(sys.argv[2])
    with open('videos.txt','r',encoding='utf-8') as f:
        videos=f.readlines()[start_idx:end_idx]
        videos=[video.strip().split('\t') for video in videos]
        videos=[{'id':video[0],'title':video[1],'description':video[2]} for video in videos]
    tasks=[]
    with ThreadPoolExecutor(max_workers=1) as executor:
        for video in videos:
            tasks.append(executor.submit(download,video))
        for task in as_completed(tasks):
            print(task.result())
        

if __name__ == "__main__":
    main()