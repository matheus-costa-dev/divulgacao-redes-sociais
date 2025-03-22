import requests

class Ig:
    def __init__(self,access_token:str):
        self.access_token = access_token
        self.page_id = None
        self.instagram_id = None

    def get_page_id(self):
        url = f"https://graph.facebook.com/v22.0/me/accounts?access_token={self.access_token}"
        res = requests.get(url)
        res.raise_for_status()
        self.page_id = res.json().get("data")[0].get("id")

    def get_instagram_id(self):
        if not self.page_id:
            self.get_page_id()

        url = f"https://graph.facebook.com/v22.0/{self.page_id}?fields=instagram_business_account&access_token={self.access_token}"
        res = requests.get(url)
        res.raise_for_status()
   

        self.instagram_id = res.json().get("instagram_business_account").get("id")

        url = f"https://graph.facebook.com/v22.0/{self.instagram_id}/media?access_token={self.access_token}"
        res = requests.get(url)
        res.raise_for_status()

    def post_image(self,opts:dict):
        """
        # Resumo
        essa api se destina a apenas a imagem online que seja passado somente sua url caso queira upar um video use a função post_resumable_media()

        ## argumentos
            opts: é um dicionário contendo as informações, veja em https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/content-publishing algumas delas são 
                - image_url — (images only) The path to the image. We will cURL your image using the passed in URL so it must be on a public server.
                - media_type — (videos only) Set to VIDEO. Indicates media is a video.
                - video_url — (videos only) Path to the video. We will cURL your video using the passed in URL so it must be on a public server.

        ## exemplo
            opts = {
            "image_url": "https://picsum.photos/200/300",
            "caption": "BronzFonz",
            "alt_text":"This is an image for BronzFonz"
            }


        """

        # if not self.instagram_id:
        #     self.get_instagram_id()

        # ## cria o container
        
        # url = f"https://graph.facebook.com/v22.0/{self.instagram_id}/media"
        # headers = {
        #     "authorization" : f"OAuth {self.access_token}"
        # }


        # res=  requests.post(url, headers=headers,params=opts)
        # print(res.json())
        # res.raise_for_status()
        # container_id = res.json().get("id")

        container_id = self.creat_container_id(opts)    

        # ## publica o container
        # url = f"https://graph.facebook.com/v22.0/{self.instagram_id}/media_publish"
        # params= {
        #     "creation_id":container_id,
        #     "access_token":self.access_token
        # }

        # res=  requests.post(url, params=params)
        # res.raise_for_status()
        self.publish_container(container_id)
        status = self.get_media_status(container_id)
        
        return status
    

    def post_resumable_media(self, opts:dict, media_file=None):
        """
        # Resumo
        The Resumable upload protocol is a brand new flow for Instagram content publishing that supports video uploads for Reels, Video Stories, and Video Carousel Items media_types.

        This new protocol supports creating Instagram media from both local videos and public hosted url videos. The protocol lets you resume a local file upload operation after a network interruption or other 
        transmission failure, saving time and bandwidth in the event of network failures. It retains the same media specifications.

        ## exemplos de opts pra subir o video

        user_tags = [
            {"username": "dev.matheuspc"}, 
            {"username": "costa_matheus000"}, 
            ....
        ]

        opts = {
            "media_type":"REELS",
            "upload_type":"resumable",
            "caption":"subindo video para o insta via api\n#lol #gaming #python #api",
            "user_tags":str(user_tags)
        }


        veja todoas as opções em https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/content-publishing na seção Resumable Upload Protocol
        """
        # if not self.instagram_id:
        #     self.get_instagram_id()

        # url = f"https://graph.facebook.com/v22.0/{self.instagram_id}/media" 
        # headers = {
        #     "authorization" : f"OAuth {self.access_token}"
        # }


        # res = requests.post(url, headers=headers, data=opts)
        # print(res.json())
        # res.raise_for_status()
        
        # container_id, uri = res.json().values()
        data= self.creat_container_id(opts)
        container_id = data.get("id")
        uri = data.get("uri")

        # Step 2: Upload the Video using Resumable Upload Protocol
        with open(media_file,"rb") as video_file:
            video_file.seek(0,2)
            file_size = video_file.tell()
            video_file.seek(0)
            headers = {
            "authorization" : f"OAuth {self.access_token}",
            "offset": "0",
            "file_size": str(file_size),
            "Content-Type": "video/mp4"
            }
            res = requests.post(uri, headers=headers, data=video_file)
            res.raise_for_status()



        self.publish_container(container_id)
        status = self.get_media_status(container_id)

        print(f"postagem publicada no instagram {status["id"]}")

        return status
  

    def creat_container_id(self,opts):
        if not self.instagram_id:
            self.get_instagram_id()

        url = f"https://graph.facebook.com/v22.0/{self.instagram_id}/media" 
        headers = {
            "authorization" : f"OAuth {self.access_token}"
        }


        res = requests.post(url, headers=headers, data=opts)
        res.raise_for_status()

        return res.json()
    
    def publish_container(self, container_id):
        url = f"https://graph.facebook.com/v22.0/{self.instagram_id}/media_publish"
        headers = {
            "authorization" : f"OAuth {self.access_token}"
        }

        data = {
            "creation_id": container_id
        }

        res = requests.post(url,headers=headers,data=data)
        res.raise_for_status()
        res = res.json()
        return res.get("id")
    
    def get_media_status(self,container_id):
        # Step 5: Get Media Status

        # // GET status from graph.facebook.com
        # curl -X GET "https://graph.facebook.com/v19.0/{ig-container-id}?fields=id,status,status_code,video_status" \
        #     -H "Authorization: OAuth {access-token}"
        url = f"https://graph.facebook.com/v22.0/{container_id}?fields=id,status,status_code,video_status" 

        headers = {
            "authorization" : f"OAuth {self.access_token}"
        }
        res = requests.get(url,headers=headers)
        res.raise_for_status()
        return res.json()

    