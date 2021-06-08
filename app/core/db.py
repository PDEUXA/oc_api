import motor.motor_asyncio

from app.core.config import settings


class MongoDB:
    def __init__(self, url: str, db_name: str, student_coll: str,
                 session_coll: str, invoice_coll: str):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(url)
        self.db = self.client[db_name]
        self.student_coll = self.db[student_coll]
        self.session_coll = self.db[session_coll]
        self.invoice_coll = self.db[invoice_coll]

    async def get_by_id(self, coll: str, id: int):
        if document := await self.db[coll].find_one({"id": id}):
            return document

    async def save_cookies(self, cookies):
        """
        Delete cookies and save the on in parameter in DB
        :param cookies: dict, cookies to be saved
        :return:
        """
        await self.db.cookies.delete_many({})
        await self.db.cookies.insert_one(cookies)

    async def get_cookies(self):
        """
        Retrieve cookies from DB
        :return: str
        """
        cursor = self.db.cookies.find()
        cookies = []
        for document in await cursor.to_list(length=100):
            cookies.append(document)
        if cookies:
            return cookies[0]['PHPSESSID']


mongodb = MongoDB(settings.MONGO_URL,
                  settings.MONGO_DB,
                  settings.MONGO_STUDENT_COLL,
                  settings.MONGO_SESSION_COLL,
                  settings.MONGO_INVOICE_COLL)
