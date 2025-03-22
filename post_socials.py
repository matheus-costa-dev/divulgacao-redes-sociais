from keys import TWITTER, FACEBOOK
import tweepy
import requests
from typing import Dict, Optional


def twitter_post(text:str, media_file:str=None):
    client = tweepy.Client(access_token=TWITTER["ACCESS_TOKEN"],
                access_token_secret=TWITTER["ACCESS_TOKEN_SECRET"], 
                bearer_token=TWITTER["BEARER_TOKEN"], 
                consumer_key=TWITTER["API_KEY"],
                consumer_secret=TWITTER["API_KEY_SECRET"])
   
    auth = tweepy.OAuth1UserHandler(
            TWITTER["API_KEY"],
            TWITTER["API_KEY_SECRET"],
            TWITTER["ACCESS_TOKEN"],
            TWITTER["ACCESS_TOKEN_SECRET"],
             )
    
    try:
        if media_file: 
            api = tweepy.API(auth)
            media = api.media_upload(filename=media_file, media_category="tweet_video")       
            client.create_tweet(text=text, media_ids=[media.media_id])
        else:
            client.create_tweet(text=text)
        
        print("postagem publicada no twitter")
    except Exception as error:
        print(error)


def facebook_post(text:Optional[str]=None ,media:Optional[Dict[str,str] ]= None) -> str:
    """
    Publica uma mensagem no Facebook, caso queira publica somente texto use text apenas caso queira publicar com video use media ao invés de text

    Argumentos:
        text: O texto principal da publicação, caso for enviar video não precisa passsar, passe apenas message, media_file.
        media: Um dicionário contendo o título e a descrição da publicação.
                 Deve ter as seguintes chaves:
                 - 'title': O título da publicação (string).
                 - 'description': A descrição da publicação (string).
                 - "media_file": Caminho para um arquivo de mídia a ser incluído na publicação.
    Exemplo:
        postar publicação só texto: 
            facebook_post(text="meu texto a ser publicado")
        postar publicação com video: 
            facebook_post(media={
            "title":"titulo da minha publicação", 
            "description":"descrição do video para os outros usuarios verem",
            "media_file":"caminhodovideo/video.mp4"
            } )
    """


    
    try:
        url = f"https://graph.facebook.com/v22.0/me/accounts?access_token={FACEBOOK["ACCESS_TOKEN"]}"
        res = requests.get(url).json()
        data = res["data"][0]


        access_token_tmp = data["access_token"]
        page_id = data["id"]

        if media:
            assert isinstance(media,dict), "media deve ser um dicionário contendo os seguintes campos title, description, media_file"
            assert media["title"] and isinstance(media.get("title"),str), "Deve ser passado um titulo pra postagem em forma de string"
            assert media["description"] and isinstance(media.get("description"), str), "Deve ser passado uma descrição pra postagem em forma de string"
            assert media["media_file"] and isinstance(media.get("media_file"),str), "Deve ser passado o caminho do video pra postagem em forma de string"

            url = f"https://graph.facebook.com/v22.0/{page_id}/videos"
            with open(media["media_file"], "rb") as video_file:
                files = {"source": video_file}
                data = {
                    "title": media["title"],
                    "description": media["description"],
                    "access_token": access_token_tmp,
                }
                res = requests.post(url, files=files, data=data).json()
                print(f"postagem publicada no facebook page {res["id"]}")
            
            return res["id"]
        

        assert len(text) > 0, "deve ser fornecido um texto no campo text da função"


        url = f"https://graph.facebook.com/v22.0/{page_id}/feed"
        headers = {"Content-Type": "application/json" }
        data = {
            "message":text,
            "access_token":access_token_tmp
        }
        res = requests.post(url,headers=headers,data=data).json()
        print(f"postagem publicada no facebook page {page_id}")

        return res["id"]
    
    except Exception as error:
        print(f"houve o seguinte erro {error}")


def instagram_post():
    pass





