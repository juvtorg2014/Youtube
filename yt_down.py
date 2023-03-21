import os
import re
import sys
import ffmpeg
from _datetime import datetime
import pytube
from youtube_transcript_api import YouTubeTranscriptApi as Trans
from youtube_transcript_api.formatters import SRTFormatter


DOWNLOAD = 'D:\\Downloads'
resolution = ["4320", "2160", "1440", "1080"]


def find_res(video, res):
    number = resolution.index(res)
    try:
        stream = video.streams.filter(type='video', res=res + "p")
        list_res = []
        if len(stream) == 0:
            print(f"Нет видео с разрешением {resol}p")
            list_res.append(video.streams.filter(type='video', res=resolution[0] + "p").__len__())
            list_res.append(video.streams.filter(type='video', res=resolution[1] + "p").__len__())
            list_res.append(video.streams.filter(type='video', res=resolution[2] + "p").__len__())
            list_res.append(video.streams.filter(type='video', res=resolution[3] + "p").__len__())
            for n, lis in enumerate(list_res):
                if lis > 0 and n > number:
                    stream = video.streams.filter(type='video', res=resolution[n] + "p")
                    if stream.__len__():
                        return stream.first()
                    else:
                        return video.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
        else:
            return stream.first()
    except Exception as e:
        print(f'Видео {video.title}', e)
        return None


def download_video(vidos, number, res, lan):
    try:
        yt = pytube.YouTube(vidos)
    except Exception as e:
        print(f'Видео {vidos} недоступно, пропускаем.', e)
    else:
        download_dir = DOWNLOAD + '\\'
        name_video = re.sub(r'[^-a-zA-Z0-9а-яА-Я. ]', '', yt.title) + '.mp4'
        name_video = name_video.replace(" ", "_")
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
        elif number == 3:
            try:
                audio_file = yt.streams.get_audio_only()
                print("Качается такой поток аудио", audio_file)
                audio_file.download(output_path=download_dir, filename=name_audio)
            except Exception as e:
                print(f'Аудио {yt.title}', e)
        elif number == 2 or number == 4 or number == 5:
            try:
                stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                print("Загрузка видео ", name_video)
                stream.download(download_dir, name_video)
                if number == 4 or number == 5:
                    audio_clip = yt.streams.get_audio_only()
                    print("Загрузка аудио ", name_audio)
                    audio_clip.download(output_path=download_dir, filename=name_audio)
                if number == 5:
                    download_subtitle(download_dir, yt, name_video[:-4], lan)
            except Exception as e:
                print(f'Видео {yt.title} не загружено', e)
        elif number == 6:
            download_subtitle(download_dir, yt, name_video[:-4], lan)


def download_channel():
    pass
    # channel = pytube.Channel(play_channel)
    # channel_id = channel.channel_id
    # video_Search = VideosSearch('NoCopyrightSounds', limit=2)
    # videosResult = VideosSearch.next(channel_id)
    #
    # print(videosResult)
    # channel_name = re.sub(r'["@|&$*?:]', '', channel_name)
    # channel_name = re.sub('@','_')
    # DOWNLOAD_DIR = DOWNLOAD + '\\' + channel_name
    # if not os.path.exists(DOWNLOAD_DIR):
    #     os.mkdir(DOWNLOAD_DIR)
    #     print('Папка {} была создана: '.format(DOWNLOAD_DIR))


# Загрузка плейлиста с мр3 и субтитрами
def download_playlist(play_list, number, res, lan):
    pl = pytube.Playlist(play_list)
    pl_title = re.sub(r'[^-a-zA-Z0-9а-яА-Я., ]', '', pl.title).replace(" ", "_")

    if not os.path.isdir(DOWNLOAD):
        os.mkdir(DOWNLOAD)
        print('Папка была создана: ' + DOWNLOAD)

    download_dir = DOWNLOAD + '\\' + pl_title

    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)
        print(f'Папка {download_dir} была создана:')

    for url in pl.video_urls:
        try:
            yt = pytube.YouTube(url)
        except Exception as e:
            print(f'Видео <<{url}>> недоступно, пропускаем.', e)
        else:
            try:
                video = yt.streams
            except Exception as e:
                print(f'Видео <<{yt.title}>> недоступно, пропускаем.', e)
                continue
            else:
                if number == "1":
                    stream_video = find_res(yt, res)
                    stream_video_title = re.sub(r'[^-a-zA-Z0-9а-яА-Я., ]', '', stream_video.title) + '.mp4'
                    stream_video_title = stream_video_title.replace(' ', '_')
                    stream_audio_title = stream_video_title.replace('.mp4', '.mp3')
                    video_title = stream_video_title.replace('.mp4', '_.mp4')
                    video_stream = ''
                    audio_stream = ''
                    if not os.path.exists(download_dir + '\\' + video_title):
                        if not os.path.exists(download_dir + '\\' + stream_video_title):
                            stream_video.download(output_path=download_dir, filename=stream_video_title)
                        if not stream_video.is_progressive:
                            stream_audio = video.get_audio_only()
                            if not os.path.exists(download_dir + '\\' + stream_audio_title):
                                stream_audio.download(download_dir, stream_audio_title)
                                video_stream = ffmpeg.input(download_dir + '\\' + stream_video_title)
                                audio_stream = ffmpeg.input(download_dir + '\\' + stream_audio_title)
                                ffmpeg.output(audio_stream, video_stream, download_dir + '\\' + video_title).run()
                                # cmd = f"ffmpeg -i {video_stream} -i {audio_stream} -c:v copy {video_title}"
                                # os.system(cmd)
                            else:
                                # cmd = f"ffmpeg -i {video_stream} -i {audio_stream} -c:v copy {video_title}"
                                # os.system(cmd)
                                ffmpeg.output(audio_stream, video_stream, download_dir + '\\' + video_title).run()
                            if os.path.exists(download_dir + '\\' + stream_video_title):
                                os.remove(download_dir + '\\' + stream_video_title)
                            if os.path.exists(download_dir + '\\' + stream_audio_title):
                                os.remove(download_dir + '\\' + stream_audio_title)
                elif number == 3:
                    audio_clip = video.get_audio_only()
                    audio_tittle = re.sub(r'[^-a-zA-Z0-9а-яА-Я., ]', '', yt.title) + '.mp3'
                    print('Загрузка аудио ', audio_tittle)
                    audio_clip.download(output_path=download_dir, filename=audio_tittle)
                elif number == 2 or number == 4 or number == 5:
                    d_video = video.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                    video_title = re.sub(r'[^-a-zA-Z0-9а-яА-Я., ]', '', d_video.title) + '.mp4'
                    video_title = video_title.replace(' ', '_')
                    audio_tittle = video_title.replace('.mp4', '.mp3')
                    try:
                        d_video.download(output_path=download_dir, filename=video_title)
                        print(f'Загрузка видео <<{video_title}>>')
                        if not os.path.exists(download_dir + '\\' + video_title):
                            d_video.download(output_path=download_dir, filename=video_title)
                        if not number == 2:
                            if not os.path.exists(download_dir + '\\' + audio_tittle):
                                print('Загрузка аудио ', audio_tittle)
                                audio_clip = video.get_audio_only()
                                audio_clip.download(output_path=download_dir, filename=audio_tittle)
                        if number == 5:
                            download_subtitle(download_dir, yt, video_title[:-4], lan)
                    except Exception as e:
                        print(e)
                        continue
                elif number == 6:
                    try:
                        video = yt.streams
                    except Exception as e:
                        print(f'Видео <<{yt.title}>> недоступно, пропускаем.', e)
                        continue
                    else:
                        vid = video.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                        video_title = re.sub(r'[^-a-zA-Z0-9а-яА-Я., ]', '', vid.title).replace(' ', '_')
                        download_subtitle(download_dir, yt, video_title, lan)


def download_subtitle(down_dir, video, name_video, lan):
    if video.captions:
        transcripts_list = Trans.list_transcripts(video.video_id)
        trans_gen = str(transcripts_list._generated_transcripts).split("'")[1]
        if lan == trans_gen and trans_gen == 'en':
            srt_lang = Trans.get_transcript(video.video_id, languages=['en'])
            srt_title = name_video + '_en.srt'
        elif lan == trans_gen and trans_gen == 'ru':
            srt_lang = Trans.get_transcript(video.video_id, languages=['ru'])
            srt_title = name_video + '_ru.srt'
        else:
            tr_lang = transcripts_list.find_transcript([trans_gen])
            if lang in tr_lang._translation_languages_dict:
                srt_lang = transcripts_list.find_transcript([tr_lang.language_code]).translate(lang).fetch()
                srt_name = str(transcripts_list.find_transcript([tr_lang.language_code]).translate(lang)).split()[1]
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


def input_all():
    resolut = ''
    langus = ''
    type_id = input("Введите тип загрузки: 1-8K,4K видео, 2-видео, 3-аудио, 4-видео+аудио, 5-все, 6-субтитры\n")
    if type_id == "1":
        resolut = input("Введите тип разрешения: {4320} {2160} {1440} {1080}\n")
        langus = "en"
        if resolut not in resolution:
            print("Нет таких разрешений как {}p".format(resolut))
            quit("Начните заново")
    elif type_id == "5":
        langus = input("Введите язык субтитров ('ru', 'en')\n".lower())
        type_id = int(type_id)
        resolut = '720'
    elif type_id == "2" or type_id == '3' or type_id == '4':
        type_id = int(type_id)
        resolut = '720'
        langus = 'en'
    elif type_id == "6":
        langus = input("Введите язык субтитров ('ru', 'en')\n".lower())
        resolut = '720'
        type_id = int(type_id)
    return type_id, resolut, langus


if __name__ == '__main__':
    play_smth = input("Введите плейлист, видео или канал:\n")
    typed, resol, lang = input_all()
    start_time = datetime.now()
    if 'watch?' in play_smth:
        download_video(play_smth, typed, resol, lang)
    elif 'playlist' in play_smth:
        download_playlist(play_smth, typed, resol, lang)
    else:
        download_channel()
    time_end = (datetime.now() - start_time).__str__().split('.')[0]
    print("Все скачано за", time_end)
