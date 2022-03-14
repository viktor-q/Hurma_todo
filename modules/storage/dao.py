import datetime

from sqlalchemy import select, update

from modules.storage.task_storage import engine, user_lists, user_tasks


class DAO:
    def create_list(self, list_name: str, user_id: int) -> int:
        conn = engine.connect()
        with conn.begin():
            insert_query = user_lists.insert().values(
                list_name=list_name,
                user_id=user_id,
            )
            result = conn.execute(insert_query)
            new_list_id = result.inserted_primary_key[0]

        return new_list_id

    def create_task(self, list_id: int, data: str, priority: int, status: int) -> int:
        created_datetime = datetime.datetime.now().replace(microsecond=0)
        conn = engine.connect()
        with conn.begin():
            insert_query = user_tasks.insert().values(
                list_id=list_id,
                data=data,
                priority=priority,
                status=status,
                created_datetime=created_datetime,
                edite_datetime=None,
            )
            result = conn.execute(insert_query)
            new_task_id = result.inserted_primary_key[0]

        return new_task_id

    def read_lists_by_userid(self, userid: int):
        conn = engine.connect()
        query = select(
            [
                user_lists.c.list_id,
                user_lists.c.list_name,
            ]
        ).where(user_lists.c.user_id == userid)

        result = conn.execute(query).first()
        return dict(result)

    def read_tasks_by_list_id(self, list_id: int):
        conn = engine.connect()
        query = select([user_tasks]).where(user_tasks.c.list_id == list_id)

        list_all_tasks = []
        exec = conn.execute(query)

        for row in exec:
            list_all_tasks.append(row)

        all_dictonarys = []
        one_task_keys = [
            "task_id",
            "list_id",
            "data",
            "priority",
            "status",
            "created_datetime",
            "edite_datetime",
        ]
        for row in list_all_tasks:
            one_unit_dict = dict(zip(one_task_keys, row))
            all_dictonarys.append(one_unit_dict)

        return all_dictonarys
