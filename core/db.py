import motor.motor_asyncio

from core.config import MONGO_URL, MONGO_DB, MONGO_STUDENT_COLL, MONGO_SESSION_COLL, MONGO_INVOICE_COLL


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
        await self.db.cookies.delete_many({})
        await self.db.cookies.insert_one(cookies)

    async def get_cookies(self):
        cursor = self.db.cookies.find()
        cookies = []
        for document in await cursor.to_list(length=100):
            cookies.append(document)
        if cookies:
            return cookies[0]['PHPSESSID']
    # async def post_session(self, session: SessionOutputModel):
    #     if cursor := await self.db["sessions"].find_one({"id": session.id}):
    #         return False
    #     else:
    #         await self.db["sessions"].insert_one(session.dict())
    #         return True


mongodb = MongoDB(MONGO_URL, MONGO_DB, MONGO_STUDENT_COLL,
                  MONGO_SESSION_COLL, MONGO_INVOICE_COLL)
