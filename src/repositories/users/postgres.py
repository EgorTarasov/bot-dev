import psycopg2
import typing as tp
import datetime as dt
from .base import UserRepositoryBase
from .models import TelegramUser, UserProfile


class UserRepositoryPostgres(UserRepositoryBase):
    def __init__(self, connection: psycopg2.extensions.connection) -> None:
        self.conn = connection

    def get_user(
        self, tg_id: int, include_profile: bool = False
    ) -> TelegramUser | None:
        cur = self.conn.cursor()
        #  select user data if include_profile is True select profile data too
        if include_profile:
            cur.execute(
                """
                    select
                        tg.id,
                        tg.first_name,
                        tg.last_name,
                        tg.username,
                        tg.is_premium,
                        tg.language_code,
                        tg.is_admin,
                        pr.fio,
                        pr.email,
                        pr.educational_group,
                        pr.portfolio_link,
                        pr.majors,
                        pr.external_links,
                        pr.skills,
                        pr.mentor,
                        pr.company
                    from telegram_users as tg
                    left join profiles as pr on tg.id = pr.user_id
                    where tg.id = %s;
                """,
                (tg_id,),
            )
            result = cur.fetchone()
            if result is None:
                return None
            (
                tg_id,
                first_name,
                last_name,
                username,
                is_premium,
                language_code,
                is_admin,
                fio,
                email,
                educational_group,
                portfolio_link,
                majors,
                external_links,
                skills,
                mentor_status,
                company,
            ) = result

            return TelegramUser(
                tg_id=tg_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                is_premium=is_premium,
                language_code=language_code,
                is_admin=is_admin if is_admin else False,
                profile=UserProfile(
                    fio=fio,
                    email=email,
                    educational_group=educational_group,
                    portfolio_link=portfolio_link,
                    majors=majors,
                    external_links=external_links,
                    skills=skills,
                    mentor_status=mentor_status,
                    company=company,
                ),
            )
        # select only user data
        else:
            cur.execute(
                """
                    select
                        id,
                        first_name,
                        last_name,
                        username,
                        is_premium,
                        language_code,
                        is_admin
                    from telegram_users
                    where id = %s;
                """,
                (tg_id,),
            )
        result = cur.fetchone()
        if result is None:
            return None
        (
            tg_id,
            first_name,
            last_name,
            username,
            is_premium,
            language_code,
            is_admin,
        ) = result
        cur.close()
        return TelegramUser(
            tg_id=tg_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            is_premium=is_premium,
            language_code=language_code,
            is_admin=is_admin,
        )

    def get_users(self, limit: int = 10, offset: int = 0) -> list[TelegramUser]:
        cur = self.conn.cursor()
        cur.execute(
            """
                select
                    tg.id,
                    tg.first_name,
                    tg.last_name,
                    tg.username,
                    tg.is_premium,
                    tg.language_code,
                    tg.is_admin,
                    pr.fio,
                    pr.email,
                    pr.educational_group,
                    pr.portfolio_link,
                    pr.majors,
                    pr.external_links,
                    pr.skills,
                    pr.mentor,
                    pr.company
                from telegram_users as tg
                left join profiles as pr on tg.id = pr.user_id
                limit %s offset %s;
            """,
            (limit, offset),
        )
        result = cur.fetchall()
        cur.close()
        return [
            TelegramUser(
                tg_id=tg_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                is_premium=is_premium,
                language_code=language_code,
                is_admin=is_admin if is_admin else False,
                profile=UserProfile(
                    fio=fio,
                    email=email,
                    educational_group=educational_group,
                    portfolio_link=portfolio_link,
                    majors=majors,
                    external_links=external_links,
                    skills=skills,
                    mentor_status=mentor_status,
                    company=company,
                ),
            )
            for (
                tg_id,
                first_name,
                last_name,
                username,
                is_premium,
                language_code,
                is_admin,
                fio,
                email,
                educational_group,
                portfolio_link,
                majors,
                external_links,
                skills,
                mentor_status,
                company,
            ) in result
        ]

    def save_user(
        self,
        tg_id: int,
        first_name: str,
        last_name: str | None,
        username: str | None,
        is_premium: bool = False,
        language_code: str = "ru",
    ) -> None:
        """
        replace old user data with new one if user already exists other wise create new user
        """
        cur = self.conn.cursor()
        # check if user has record in db if not create new one
        cur.execute(
            """
                select id
                from telegram_users
                where id = %s;
            """,
            (tg_id,),
        )
        result = cur.fetchone()
        if result is None:
            cur.execute(
                """
                    insert into telegram_users (
                        id,
                        first_name,
                        last_name,
                        username,
                        is_premium,
                        language_code
                    ) values (%s, %s, %s, %s, %s, %s);
                """,
                (tg_id, first_name, last_name, username, is_premium, language_code),
            )
            cur.execute(
                """
                    insert into subscriptions (id) values (%s);
                """,
                (tg_id,),
            )
        else:
            # update user data
            cur.execute(
                """
                    update telegram_users
                    set first_name = %s,
                        last_name = %s,
                        username = %s,
                        is_premium = %s,
                        language_code = %s
                    where id = %s;
                """,
                (first_name, last_name, username, is_premium, language_code, tg_id),
            )
        self.conn.commit()
        cur.close()

    def is_admin(self, tg_id: int) -> bool:
        cur = self.conn.cursor()
        cur.execute(
            """
                select is_admin
                from telegram_users
                where id = %s;
            """,
            (tg_id,),
        )
        result = cur.fetchone()
        if result is None:
            return False
        is_admin = result[0]
        cur.close()
        return is_admin

    def get_admins(self) -> list[int]:
        cur = self.conn.cursor()
        cur.execute(
            """
                select id
                from telegram_users
                where is_admin = true;
            """
        )
        result = cur.fetchall()
        cur.close()
        return [row[0] for row in result]

    def create_invite_code(self, code: str, admin_id: int) -> None:
        # insert into admin_invite_codes(code, admin_id) values ('testcode', 499114263);
        cur = self.conn.cursor()
        cur.execute(
            """
                    insert into admin_invite_codes(admin_id, code) values (%s, %s)
                    """,
            (admin_id, code),
        )

        self.conn.commit()
        cur.close()

    def use_invite_code(self, code: str, user_id: int) -> int:
        # update  admin_invite_codes set user_id=297150550, activated_at=CURRENT_TIMESTAMP where code = 'testcode';
        # update telegram_users  set is_admin = true where id =  297150550;
        cur = self.conn.cursor()
        cur.execute(
            """
            select id, admin_id, user_id, created_at, activated_at from admin_invite_codes where code = %s;
            """,
            (code,),
        )
        result = cur.fetchone()

        if result is None:
            raise ValueError
        code_id, admin_id, used_by, created_at, activated_at = result
        if activated_at != None:
            raise Exception(f"Code already activated by {used_by}")

        cur.execute(
            """
                    update admin_invite_codes set user_id = %s, activated_at=CURRENT_TIMESTAMP where code = %s;
                    """,
            (
                user_id,
                code,
            ),
        )
        cur.execute(
            """
                update telegram_users set is_admin = true where id = %s;
            """,
            (user_id,),
        )
        self.conn.commit()
        cur.execute(
            """select admin_id from admin_invite_codes where code = %s;""", (code,)
        )
        result = cur.fetchone()
        cur.close()
        if result:
            return result[0]
        # TODO: решить, что может пойти не так
        return -1

    def save_profile_data(
        self,
        tg_id: int,
        fio: str | None = None,
        email: str | None = None,
        educational_group: str | None = None,
        portfolio_link: str | None = None,
        majors: list[str] | None = None,
        external_links: list[str] | None = None,
        skills: list[str] | None = None,
        mentor_status: bool = False,
        company: str | None = None,
    ) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            select user_id
            from profiles
            where user_id = %s;
            """,
            (tg_id,),
        )
        result = cur.fetchone()
        if result is None:
            cur.execute(
                """
                insert into profiles (
                    user_id,
                    fio,
                    email,
                    educational_group,
                    portfolio_link,
                    majors,
                    external_links,
                    skills,
                    mentor,
                    company
                ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    tg_id,
                    fio,
                    email,
                    educational_group,
                    portfolio_link,
                    majors,
                    external_links,
                    skills,
                    mentor_status,
                    company,
                ),
            )
        else:
            # update user data
            cur.execute(
                """
                update profiles
                set fio = %s,
                    email = %s,
                    educational_group = %s,
                    portfolio_link = %s,
                    majors = %s,
                    external_links = %s,
                    skills = %s,
                    mentor = %s,
                    company = %s
                where user_id = %s;
                """,
                (
                    fio,
                    email,
                    educational_group,
                    portfolio_link,
                    majors,
                    external_links,
                    skills,
                    mentor_status,
                    company,
                    tg_id,
                ),
            )
        self.conn.commit()
        cur.close()


