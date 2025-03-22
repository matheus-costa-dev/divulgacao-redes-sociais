from youtube import Yt
from keys import YOUTUBE, FACEBOOK
from post_socials import twitter_post, facebook_post
from instagram import Ig
from gemini import generate_text, transform_to_dict
from pandas import read_excel

channel_id = "UC52gcAONHi2DhPT2O1IwufQ"
df = read_excel(f"tbls/{channel_id}.xlsx")
data = df[df["is_shorts"]==True]
data = data.iloc[0]

opts = {
    "text": f"Faça um escrita de um video a ser publicado nas redes sociais cujo o titulo seja algo referente a {data["title"]}",
    "context": f"é um video shorts de duração de {data["duration"]} segundos referente ao jogo league of legends, a intenção é ter um texto chamativos com tags pra aumentar audiência no canal no youtbe a ser divulgado nos mais diversos meios socias",
    "instructions": "crie 2 resposta 1 para o twitter e outra com a chave others pra ser publicado nas demais redes socias, a do twitter tem um limite de 250 caracters já as demais não, retorne em formato json apenas o json {...} cada um deve conter as chaves title, description"
}
text = generate_text(opts)
text_dict = transform_to_dict(text)

with open("apagar.json","r") as f:
    from json import loads
    text_dict = loads(f.read())

instagram = Ig(FACEBOOK["ACCESS_TOKEN"])

instagram_opts = {
"media_type":"REELS", "upload_type":"resumable", 
"caption":f"{text_dict["others"]["title"]}\n{text_dict["others"]["description"]}",
"user_tags":str( [{"username": "dev.matheuspc"}])
}
instagram.post_resumable_media(instagram_opts, "videos/video.mp4")