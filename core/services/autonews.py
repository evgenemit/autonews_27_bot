import aiohttp
import aiofiles
import aiofiles.os
import requests
from environs import Env
from bs4 import BeautifulSoup
from PIL import Image

from core.services.logs import add_logs


class AutoNews:

    def __init__(self):
        self.debug = True
        self.session_id = None
        self.viewstate = None
        self.eventvalidation = None
        self.vsgen = None
        self.guid_session = None
        self.expandstate = None
        self.guid_classifier = None
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'wp.edu.by',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Sec-Ch-Ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"'
        }


    async def __aenter__(self):
        return self


    async def __aexit__(self, exception_type, exception_value, exception_traceback):
        await self.logout()


    def update_cookies(self):
        """Обновляет cookie запросов"""
        self.headers['Cookie'] = f'ASP.NET_SessionId={self.session_id}; WJG=ListSecurity=Hight'


    def update_asp_info(self, text: str):
        """Обновляет необходиме для запроса данные"""
        try:
            sub = text[text.index('__VIEWSTATE') + 12:]
            self.viewstate = sub[:sub.index('|')]
            sub = text[text.index('__EVENTVALIDATION') + 18:]
            self.eventvalidation = sub[:sub.index('|')]
        except:
            pass
        soup = BeautifulSoup(text, 'lxml')
        res = soup.find(attrs={'id': '__VIEWSTATE'})
        if res:
            self.viewstate = res.attrs.get('value')
        res = soup.find(attrs={'id': '__EVENTVALIDATION'})
        if res:
            self.eventvalidation = res.attrs.get('value')
        vsgen = soup.find(attrs={'id': '__VIEWSTATEGENERATOR'})
        if vsgen:
            self.vsgen = vsgen.attrs.get('value')
        guid_session = soup.find(attrs={'id': 'GuidSession'})
        if guid_session:
            self.guid_session = guid_session.attrs.get('value')
        expandstate = soup.find(attrs={'id': 'ctl00_Main_Left_TreeClassifier_ExpandState'})
        if expandstate:
            self.expandstate = 'e' + expandstate.attrs['value'][1:]
        guid_classifier = soup.find(attrs={'id': 'GUID_CLASSIFIER'})
        if guid_classifier:
            self.guid_classifier = guid_classifier.attrs.get('value')


    async def prepare_imges(self):
        """Сжимает картинки до 300 кб"""
        images = await aiofiles.os.listdir('data')
        i = 0
        for image in images:
            i += 1
            im = Image.open(f'data/{image}')
            new_name = f'data/prepared_{i}.jpg'
            im.save(new_name, quality=100)
            await aiofiles.os.remove(f'data/{image}')
            q = 100
            while (await aiofiles.os.stat(new_name)).st_size > 300_000:
                im.save(new_name, quality=q, optimize=True, progressive=True)
                q -= 1


    async def login(self):
        """Авторизация"""
        env = Env()
        env.read_env('.env')
        site_name = env.str('SITE_NAME')
        site_username = env.str('SITE_USERNAME')
        site_password = env.str('SITE_PASSWORD')
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://wp.edu.by/',
                headers=self.headers
            ) as response:
                set_cookies = response.headers.get('Set-Cookie')
                if not set_cookies:
                    return {'status': False, 'message': 'Ответ не содержит SessionId.'}
                self.session_id = set_cookies[set_cookies.index('=') + 1:set_cookies.index(';')]
                self.update_cookies()
                text = await response.text()
            soup = BeautifulSoup(text, 'lxml')
            pin = soup.find(attrs={'id': 'ImagePin'}).attrs['src'][21:26]
            self.update_asp_info(text)

            data = {
                'ctl00$ScriptManagerWindow': 'ctl00$ScriptManagerWindow|ctl00$ContentMain$LoginStart',
                '__VIEWSTATE': self.viewstate,
                '__VIEWSTATEGENERATOR': self.vsgen,
                '__EVENTVALIDATION': self.eventvalidation,
                'ctl00$ContentMain$SiteName': site_name,
                'ctl00$ContentMain$UserName': site_username,
                'ctl00$ContentMain$UserPwd': site_password,
                'ctl00$ContentMain$TextBoxPin': pin,
                'ctl00$ContentMain$ListSecurity': 'Hight',
                '__ASYNCPOST': 'true',
                'ctl00$ContentMain$LoginStart': 'Авторизация'
            }
            async with session.post(
                'https://wp.edu.by/',
                headers=self.headers,
                data=data
            ) as response:
                text = await response.text()
            if 'pageRedirect' in text:
                await add_logs(f'session_id={self.session_id} OPEN')
                return {'status': True}
            soup = BeautifulSoup(text, 'lxml')
            status_work = soup.find(attrs={'id': 'StatusWork'})
            if status_work:
                return {'status': False, 'message': status_work.attrs.get('value', None)}
        return {'status': False, 'message': 'Ответ не содержит редирект.'}


    async def open_tree(self, path: list):
        """Открывает классификаторы по цепочке"""
        guid = None
        data = {}
        eventargument = 'sNodeClassifier'
        for path_element in path:
            r = requests.post(
                'https://wp.edu.by/explorer.aspx',
                headers=self.headers,
                data=data
            )
            text = r.text
            self.update_asp_info(text)
            selectednode = None
            soup = BeautifulSoup(text, 'lxml')
            data = soup.find_all('a')
            for element in data:
                if element.text == path_element:
                    guid = element.find('img').attrs['guid']
                    eventargument += f'\\{guid}'
                    selectednode = element.attrs['id']
                    break
            else:
                break
            data = {
                'ctl00$ScriptManagerWindow': 'ctl00$Main_Left$UpdatePanel1|ctl00$Main_Left$TreeClassifier',
                '__EVENTTARGET': 'ctl00$Main_Left$TreeClassifier',
                '__EVENTARGUMENT': eventargument,
                'ctl00_Main_Left_TreeClassifier_ExpandState': self.expandstate,
                'ctl00_Main_Left_TreeClassifier_SelectedNode': selectednode,
                '__VIEWSTATE': self.viewstate,
                '__VIEWSTATEGENERATOR': self.vsgen,
                '__EVENTVALIDATION': self.eventvalidation,
                'ctl00$Main_Left$GUID_CLASSIFIER': self.guid_classifier,
                'ctl00$Main_Right$ST_pages': 10,
                'ctl00$GuidSession': self.guid_session,
                '__ASYNCPOST': 'true'
            }
        if guid:
            return {'status': True, 'guid': guid}
        return {'status': False, 'message': 'Не удалось открыть классификатор.'}


    async def add_object(self, guid: str, obj_type: str, n: int = 1):
        """
        Создает новый объект
        304 - изображение, 534 - новость, 524 - блок html
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'https://wp.edu.by/G_Data/AddObject.aspx?guid={guid}',
                headers={'Cookie': self.headers['Cookie']}
            ) as response:
                text = await response.text()

            self.update_asp_info(text)
            data = {
                'ctl00$ScriptManagerDialog': 'ctl00$ScriptManagerDialog|ctl00$AddButton$ButtonMake',
                '__VIEWSTATE': self.viewstate,
                '__VIEWSTATEGENERATOR': self.vsgen,
                '__EVENTVALIDATION': self.eventvalidation,
                'ctl00$Main$Classifier': guid,
                'ctl00$Main$SelType': obj_type,
                'ctl00$Main$N_Count': str(n),
                'ctl00$GuidSession': self.guid_session,
                '__ASYNCPOST': 'true',
                'ctl00$AddButton$ButtonMake': 'Создать'
            }
            async with session.post(
                f'https://wp.edu.by/G_Data/AddObject.aspx?guid={guid}',
                headers=self.headers,
                data=data
            ) as response:
                text = await response.text()

            soup = BeautifulSoup(text, 'lxml')
            objs_id = soup.find(attrs={'id': 'Result_Value_1'})
            objs_id = objs_id.attrs.get('value', '').split(';')
            objs_id = list(filter(lambda x: x, objs_id))
            return {'status': True, 'objs_id': objs_id}
        return {'status': False, 'message': 'Не удалось создать новый объект.'}


    async def add_img(self, obj_id: str):
        """Загружает изображение в созданный графический объект"""
        img_path = 'data/' + (await aiofiles.os.listdir('data'))[0]
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'https://wp.edu.by/G_All/SelectImage.aspx?guid={obj_id}',
                headers=self.headers
            ) as response:
                text = await response.text()
            self.update_asp_info(text)
            soup = BeautifulSoup(text, 'lxml')
            selectednode = soup.find(
                attrs={'id': 'ctl00_Main_TreeClassifier_SelectedNode'}
            ).attrs.get('value')
            data = {
                'ctl00_Main_TreeClassifier_ExpandState': self.expandstate,
                'ctl00_Main_TreeClassifier_SelectedNode': selectednode,
                '__VIEWSTATE': self.viewstate,
                '__VIEWSTATEGENERATOR': self.vsgen,
                '__EVENTVALIDATION': self.eventvalidation,
                'ctl00$Main$ButtonSaveBinary': 'Загрузить',
                'ctl00$GuidSession': self.guid_session
            }
            async with aiofiles.open(img_path, mode='rb') as f:
                im_bytes = await f.read()
            files = {
                'ctl00$Main$FileUploadIco': (img_path, im_bytes, 'image/jpeg')
            }
            requests.post(
                f'https://wp.edu.by/G_All/SelectImage.aspx?guid={obj_id}',
                headers=self.headers,
                data=data,
                files=files
            )
        await aiofiles.os.remove(img_path)
        return {'status': True}


    async def add_news_text(
            self,
            guid: str,
            obj_id: str,
            caption: str,
            title: str,
            date: str
        ):
        """Добавляет данные в объект новости"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'https://wp.edu.by/G_Data/ObjectEditor.aspx?guid={obj_id}',
                headers=self.headers
            ) as response:
                text = await response.text()
        self.update_asp_info(text)
        caption = caption.replace('\n', '<br />')

        data = {
            'ctl00$ScriptManagerDialog': 'ctl00$ScriptManagerDialog|ctl00$ButtonSave',
            '__VIEWSTATE': self.viewstate,
            '__VIEWSTATEGENERATOR': self.vsgen,
            '__EVENTVALIDATION': self.eventvalidation,
            'ctl00$Main$CheckBoxStatusObject': 'on',
            'ctl00$Main$ListLang$0': 'on',
            'ctl00$Main$Classifier': str(guid),
            'ctl00$Main$dt_text': date,
            'ctl00$Main$zag': title,
            'ctl00$Main$txt': f'<p>{caption}</p>',
            'ctl00$GuidSession': self.guid_session,
            '__ASYNCPOST': 'true',
            'ctl00$ButtonSave': 'Сохранить и остаться'
        }
        if self.debug:
            del data['ctl00$Main$CheckBoxStatusObject']
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'https://wp.edu.by/G_Data/ObjectEditor.aspx?guid={obj_id}',
                headers=self.headers,
                data=data
            ) as response:
                soup = BeautifulSoup(await response.text(), 'lxml')
                status = soup.find(attrs={'id': 'Result_Status'})
                if status:
                    status_text = status.attrs.get('value')
                    if status_text == 'Save':
                        return {'status': True}
                return {
                    'status': False,
                    'message': 'Новость не создана'
                }


    async def logout(self):
        """Закрывает сессию"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://wp.edu.by/login_end.aspx?status=end',
                headers=self.headers
            ):
                await add_logs(f'session_id={self.session_id} CLOSED')


    async def create_news(
            self,
            images_count: int,
            caption: str,
            title: str,
            date: str
        ):
        """Создает новость"""
        await add_logs('login')
        res = await self.login()
        if not res['status']:
            return res

        await add_logs('open tree')
        res = await self.open_tree(['Актуально', 'Сервисы', 'Архив новостей'])
        if not res['status']:
            return res
        guid = res['guid']

        await add_logs(f'create images ({images_count})')
        res = await self.add_object(guid, '304', images_count)
        if not res['status']:
            return res
        images_objs_id = res['objs_id']
        await add_logs(f'созданы картинки {images_objs_id}')

        await add_logs('prepare images')
        await self.prepare_imges()

        await add_logs('load images')
        for obj_id in images_objs_id:
            await self.add_img(obj_id)

        await add_logs('create news object')
        res = await self.add_object(guid, '534')
        if not res['status']:
            return res
        news_obj_id = res['objs_id'][0]
        await add_logs(f'создана новость {news_obj_id}')

        await add_logs('add news data')
        res = await self.add_news_text(
            guid,
            news_obj_id,
            caption,
            title,
            date
        )
        if not res['status']:
            return res
        return {'status': True}
