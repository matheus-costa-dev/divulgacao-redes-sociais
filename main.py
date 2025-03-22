from youtube import Yt
from keys import YOUTUBE, FACEBOOK
from post_socials import twitter_post, facebook_post
from instagram import Ig
from gemini import generate_text, transform_to_dict

# variables

channel_id = "UC52gcAONHi2DhPT2O1IwufQ"
video_path = "videos/video.mp4"
links = ["https://www.twitch.tv/kaijinlol1"]


youtube = Yt(YOUTUBE["API_KEY"], channel_id)
df = youtube.get_table()
# data = df[df["published_at"] == max(df["published_at"])].iloc[0]
data = df[df["is_shorts"]==True]
data = data.iloc[0]

if data["is_shorts"]:
    #youtube.download_short([data["url_shorts"]])
    opts = {
        "text": f"Faça um escrita de um video a ser publicado nas redes sociais cujo o titulo seja algo referente a {data["title"]}",
        "context": f"é um video shorts de duração de {data["duration"]} segundos referente ao jogo league of legends, a intenção é ter um texto chamativos com tags pra aumentar audiência no canal no youtbe a ser divulgado nos mais diversos meios socias",
        "instructions": f"crie 2 resposta 1 para o twitter e outra com a chave others pra ser publicado nas demais redes socias, a do twitter tem um limite de 250 caracters já as demais não, em ambas devem fazer referência aos links {",".join(links)}, retorne em formato json apenas o json cada um deve conter as chaves title, description"
    }
    text = generate_text(opts)
    text_dict = transform_to_dict(text)


    instagram = Ig(FACEBOOK["ACCESS_TOKEN"])

    instagram_opts = {
        "media_type":"REELS", 
        "upload_type":"resumable", 
        "caption":f"{text_dict["others"]["title"]}\n{text_dict["others"]["description"]}",
        "user_tags":str( [{"username": "dev.matheuspc"}])
    }
    instagram.post_resumable_media(instagram_opts, video_path)

    facebook_opts = {
        "title": text_dict["others"]["title"],
        "description":text_dict["others"]["description"],
        "media_file":video_path
        } 
    
    facebook_post(media=facebook_opts)


    twitter_post(text=f"{text_dict["twitter"]["title"]} {text_dict["twitter"]["description"]}", media_file=video_path)
    

    

else:
    opts = {
        "text": f"Faça um escrita de um video a ser publicado nas redes sociais cujo o titulo seja algo referente a {data["title"]} e tenha a seguinte url {data["url_video"]}",
        "context": f"é um video shorts de duração de {data["duration"]} segundos referente ao jogo league of legends, a intenção é ter um texto chamativos com tags pra aumentar audiência no canal no youtbe a ser divulgado nos mais diversos meios socias",
        "instructions": f"retorne apenas o texto e tenha emojis que será usado na publicação tendo ela uma limitação do texto de 250 caracteres"
    }
    text = generate_text(opts["text"], opts["context"], opts["instructions"])
    twitter_post(text=text)