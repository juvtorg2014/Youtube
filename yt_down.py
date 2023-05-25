import os
import re
import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import ffmpeg
from _datetime import datetime
import pytube
from pytube import Channel
from youtube_transcript_api import YouTubeTranscriptApi as Trans
from youtube_transcript_api.formatters import SRTFormatter


DOWNLOAD = 'D:\\Downloads'
resolution = ["4320", "2160", "1440", "1080", "720"]
interval_secs = 5


def find_res(vid, res, num):
    """Нахождение нужного разрешения видео или самого большого"""
    number = resolution.index(res)
    video_streams = vid.streams
    stream = video_streams.filter(type='video', res=res + "p")
    if num == 1 and stream is not None:
        return stream
    else:
        list_res = []
        try:
            if len(stream) == 0:
                print(f"Нет видео <<{vid.title}>> с разрешением {resol}p")
                list_res.append(video_streams.filter(type='video', res=resolution[0] + "p").__len__())
                list_res.append(video_streams.filter(type='video', res=resolution[1] + "p").__len__())
                list_res.append(video_streams.filter(type='video', res=resolution[2] + "p").__len__())
                list_res.append(video_streams.filter(type='video', res=resolution[3] + "p").__len__())
                list_res.append(video_streams.filter(type='video', res=resolution[4] + "p").__len__())
                for n, lis in enumerate(list_res):
                    if lis > 0 and n > number:
                        stream = video_streams.filter(type='video', res=resolution[n] + "p")
                        if stream.__len__():
                            return stream.first()
                        else:
                            return video_streams.filter(file_extension='mp4').order_by('resolution').desc().first()
            else:
                return stream.first()
        except Exception as e:
            print(f'Видео {video_streams.title}', e)
            return None


def change_name(name):
    new_name = re.sub(r'[^-a-zA-Z0-9а-яА-Я., ]', '', name).replace(' ', '_')
    return new_name

def download_video(vidos, number, res, lan):
    """Загрузка видео, аудио, субтитров или все вместе"""
    yt = ''
    try:
        yt = pytube.YouTube(vidos)
    except Exception as e:
        print(f'Видео {vidos} недоступно, пропускаем.', e)
        quit()
    download_dir = DOWNLOAD + '\\'
    name_video = change_name(yt.title) + '.mp4'
    name_audio = name_video.replace('.mp4', '.mp3')
    down_video = download_dir + name_video
    down_audio = download_dir + name_audio
    if number == "1":
        stream_video = find_res(yt, res)
        if stream_video is None:
            sys.exit()
        if not os.path.exists(download_dir + name_video):
            print("Загрузка видео", download_dir + name_video)
            stream_video.download(output_path=download_dir, filename=name_video)
        if not stream_video.is_progressive:
            stream_audio = yt.streams.get_audio_only()
            if not os.path.exists(download_dir + name_audio):
                print("Загрузка аудио", download_dir + name_audio)
                stream_audio.download(output_path=download_dir, filename=name_audio)
            down_file = download_dir + name_video.replace('.mp4', '_.mp4').strip()
            # ffmpeg.output(stream_audio, stream_video, download_dir + '\\' + down_file).run()
            os.system(f"ffmpeg.exe -i {down_video} -i {down_audio} -c:v copy {down_file}")
            if os.path.exists(down_file):
                if os.path.exists(download_dir + name_video):
                    os.remove(download_dir + name_video)
                if os.path.exists(download_dir + name_audio):
                    os.remove(download_dir + name_audio)
    elif number == "3":
        try:
            audio_file = yt.streams.get_audio_only()
            print("Качается такой поток аудио", audio_file)
            audio_file.download(output_path=download_dir, filename=name_audio)
        except Exception as e:
            print(f'Аудио {yt.title}', e)
    elif number == "2" or number == "4" or number == "5":
        try:
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            print("Загрузка видео ", name_video)
            stream.download(download_dir, name_video)
            if number == "4" or number == "5":
                audio_clip = yt.streams.get_audio_only()
                print("Загрузка аудио ", name_audio)
                audio_clip.download(output_path=download_dir, filename=name_audio)
            if number == "5":
                download_subtitle(download_dir, yt, name_video[:-4], lan)
        except Exception as e:
            print(f'Видео {yt.title} не загружено', e)
    elif number == "6":
        download_subtitle(download_dir, yt, name_video[:-4], lan)


def download_channel(play_channel, mode, res, lan):
    """Загрузка всего канала с плейлистами или без"""
    videos = []
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    if driver is None:
        print(f" Нет ответа от сервера {play_channel}")
        exit()
    driver.get(play_channel)
    driver.maximize_window()
    time.sleep(5)
    channel_name = change_name(driver.title)
    ht = driver.execute_script("return document.documentElement.scrollHeight;")
    while True:
        prev_ht = driver.execute_script("return         document.documentElement.scrollHeight;")
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        ht = driver.execute_script("return document.documentElement.scrollHeight;")
        if prev_ht == ht:
            break
    links = driver.find_elements(By.XPATH, '//*[@id="video-title-link"]')
    if len(links) > 0:
        for link in links:
            videos.append(link.get_attribute('href'))
    else:
        print("Не удалось получить список видео")
        exit()
    download_dir = DOWNLOAD + '\\' + channel_name
    if not os.path.exists(download_dir):
        os.mkdir(download_dir)
        print(f'Папка {download_dir} была создана:')

    for video in videos:
        yt = pytube.YouTube(video)
        hd_name = change_name(yt.title)
        hd = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        print(video)

    driver.quit()

def check_playlist(video_urls) -> list:
    """  Валидация видео из плейлиста """
    new_playlist = []
    yt = ''
    for url in video_urls:
        try:
            yt = pytube.YouTube(url)
            stream = yt.streams
            new_playlist.append(yt)
        except Exception as e:
            print(f'Видео <<{yt.title}>> недоступно, пропускаем.', e)
            continue
    return new_playlist


def download_playlist(play_list, number, res, lan):
    """ Загрузка плейлистов с мр3 и субтитрами"""
    pl = pytube.Playlist(play_list)
    pl_title = change_name(pl.title)
    if not os.path.isdir(DOWNLOAD):
        os.mkdir(DOWNLOAD)
        print('Папка была создана: ' + DOWNLOAD)

    download_dir = DOWNLOAD + '\\' + pl_title

    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)
        print(f'Папка {download_dir} была создана:')

    available_video = check_playlist(pl.video_urls)

    for video in available_video:
        time.sleep(interval_secs)
        try:
            video_stream = video.streams
        except Exception as e:
            print(f'Загрузка <<{video.title}>> невозможна, пропускаем.', e)
            continue
        if number == "1":
            stream_video = find_res(video, res, number)
            stream_title = change_name(stream_video.title)
            stream_video_title = ' '.join(stream_title.split())
            stream_video_title = stream_video_title.replace(' ', '_') + '.mp4'
            stream_audio_title = stream_video_title.replace('.mp4', '.mp3')
            video_title = stream_video_title.replace('.mp4', '_.mp4')
            v_stream = ''
            a_stream = ''
            if not os.path.exists(download_dir + '\\' + video_title):
                if not os.path.exists(download_dir + '\\' + stream_video_title):
                    stream_video.download(output_path=download_dir, filename=stream_video_title)
                else:
                    print(f"The file <<{stream_video_title}>> has already been downloaded")
                if not stream_video.is_progressive:
                    stream_audio = video_stream.get_audio_only()
                    if not os.path.exists(download_dir + '\\' + stream_audio_title):
                        stream_audio.download(download_dir, stream_audio_title)
                        v_stream = ffmpeg.input(download_dir + '\\' + stream_video_title)
                        a_stream = ffmpeg.input(download_dir + '\\' + stream_audio_title)
                        ffmpeg.output(a_stream, v_stream, download_dir + '\\' + video_title).run()
                        # cmd = f"ffmpeg -i {v_stream} -i {a_stream} -c:v copy {video_title}"
                        # os.system(cmd)
                    else:
                        # cmd = f"ffmpeg -i {v_stream} -i {a_stream} -c:v copy {video_title}"
                        # os.system(cmd)
                        ffmpeg.output(a_stream, v_stream, download_dir + '\\' + video_title).run()
                    if os.path.exists(download_dir + '\\' + stream_video_title):
                        os.remove(download_dir + '\\' + stream_video_title)
                    if os.path.exists(download_dir + '\\' + stream_audio_title):
                        os.remove(download_dir + '\\' + stream_audio_title)
        elif number == "3":
            audio_clip = video_stream.get_audio_only()
            audio_tittle = re.sub(r'[^-a-zA-Z0-9а-яА-Я., ]', '', video.title)
            audio_tittle = ' '.join(audio_tittle.split())
            audio_tittle = audio_tittle.replace(' ', '_') + '.mp3'
            print(f"Загрузка аудио <<{audio_tittle}>>")
            audio_clip.download(output_path=download_dir, filename=audio_tittle)
        elif number == "2" or number == "4" or number == "5":
            d_video = video_stream.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            video_title = change_name(d_video.title) + '.mp4'
            audio_tittle = video_title.replace('.mp4', '.mp3')
            try:
                if not os.path.exists(download_dir + '\\' + video_title):
                    print(f'Загрузка видео <<{video_title[:-4]}>>')
                    d_video.download(output_path=download_dir, filename=video_title)
                else:
                    print(f"The file <<{video_title[:-4]}>> has already been downloaded")
                if not number == "2":
                    if not os.path.exists(download_dir + '\\' + audio_tittle):
                        print('Загрузка аудио ', audio_tittle[:-4])
                        audio_clip = video_stream.get_audio_only()
                        audio_clip.download(output_path=download_dir, filename=audio_tittle)
                    else:
                        print(f"The file <<{audio_tittle[:-4]}>> has already been downloaded")
                if number == "5":
                    download_subtitle(download_dir, video, video_title[:-4], lan)
            except Exception as e:
                print(e)
                continue
        elif number == "6":
            vidos = video_stream.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            vid_title = change_name(vidos.title).replace(' ', '_')
            download_subtitle(download_dir, video, vid_title, lan)


def download_subtitle(down_dir, video, name_video, lan):
    srt_lang = ''
    srt_title = ''
    srt_name = ''
    if video.captions:
        if video.caption_tracks[0].code == lan or video.caption_tracks[0].code == 'a.' + lan:
            srt_lang = Trans.get_transcript(video.video_id, languages=[lan])
            srt_title = name_video + '_' + lan + '.srt'
        else:
            trans_list = Trans.list_transcripts(video.video_id)
            if not trans_list._manually_created_transcripts.__len__() == 0:
                if trans_list._manually_created_transcripts.get(lan).language_code == lan:
                    srt_lang = Trans.get_transcript(video.video_id, languages=[lan])
                    srt_title = name_video + '_' + lan + '.srt'
            else:
                trans_gen = str(trans_list._generated_transcripts).split("'")[1]
                if lan == trans_gen and trans_gen == 'en':
                    srt_lang = Trans.get_transcript(video.video_id, languages=['en'])
                    srt_title = name_video + '_en.srt'
                elif lan == trans_gen and trans_gen == 'ru':
                    srt_lang = Trans.get_transcript(video.video_id, languages=['ru'])
                    srt_title = name_video + '_ru.srt'
                else:
                    tr_lang = trans_list.find_transcript([trans_gen])
                    if lang in tr_lang._translation_languages_dict:
                        srt_lang = trans_list.find_transcript([tr_lang.language_code]).translate(lang).fetch()
                        srt_name = str(trans_list.find_transcript([tr_lang.language_code]).translate(lang)).split()[1]
                        srt_title = name_video + '_' + lang + '.srt'
                    else:
                        print("Нет субтитров такого языка", lan)
                        return

        formatter = SRTFormatter()
        srt_formatted = formatter.format_transcript(srt_lang)
        if lan == 'en':
            print(f"Скачиваются субтитры видео <<{name_video}>> на английском языке")
        elif lan == 'ru':
            print(f"Скачиваются субтитры видео <<{name_video}>> на русском языке")
        else:
            print(f"Скачиваются субтитры видео <<{name_video}>> на языке {srt_name}")
        try:
            with open(down_dir + '\\' + srt_title, "w", encoding='utf-8') as f:
                for stroki in srt_formatted:
                    f.write(stroki)
        except Exception as e:
            print(e)
    else:
        print(f"У видео <<{video.title}>> нет субтитров")


def input_all() -> tuple:
    resolut = '720'
    langus = ''
    type_id = input("Input type download: 1-8K,4K video, 2-video, 3-audio, 4-video+audio, 5-all, 6-subtitle\n")
    if type_id == "1":
        resolut = input("Input type of resolution: {4320} {2160} {1440} {1080} {720}\n")
        langus = "en"
        if resolut not in resolution:
            print("No such type of resolution as {}p".format(resolut))
            quit("Go again")
    elif type_id == "5":
        langus = input("Input lanquages subtitle ('ru', 'en')\n".lower())
    elif type_id == "2" or type_id == '3' or type_id == '4':
        langus = 'en'
    elif type_id == "6":
        langus = input("Input lanquages subtitle ('ru', 'en')\n")
    else:
        return None
    return type_id, resolut, langus.lower()


if __name__ == '__main__':
    play_smth = input("Input playlist, video or channel:\n")
    # канал без плейлистов
    #play_smth = 'https://www.youtube.com/playlist?list=PLn6O1S03KRbeNKrpcFSRwQrJZoTxqunYJ'
    '''Симкин-https://www.youtube.com/playlist?list=PLJPpvRGAVMhAQBPo2R9VDVrZTIYonrp4Y'''
    typed, resol, lang = input_all()
    if (typed, resol, lang) is None:
        print('Something is wrong !')
        quit('Start Over')
    start_time = datetime.now()
    if 'watch?' in play_smth:
        download_video(play_smth, typed, resol, lang)
    elif 'playlist' in play_smth:
        download_playlist(play_smth, typed, resol, lang)
    elif 'channel' or 'https://www.youtube.com/@' in play_smth:
        download_channel(play_smth, typed, resol, lang)
    else:
        print('Неправильный адрес уoutube-канала!')
        quit('Start Over')
    time_end = (datetime.now() - start_time).__str__().split('.')[0]
    print("All done for", time_end)
