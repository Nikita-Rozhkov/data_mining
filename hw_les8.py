from instabot import Bot
import os
import dotenv


class InstaParse:
    users = {}
    bot = Bot()

    def __init__(self, user_first, user_second, max_number, login, password):
        self.user_first = user_first
        self.user_second = user_second
        self.max_number = max_number
        self.login = login
        self.password = password

    def run(self):
        self.bot.login(username=self.login, password=self.password)
        user1_id = self.bot.get_user_id_from_username(self.user1)
        user2_id = self.bot.get_user_id_from_username(self.user2)
        self.users.update({user1_id: {'parent': None, 'number': 0}})
        self._find_friends(user2_id, self.max_number)
        return self._find_rel(user2_id)

    def _find_friends(self, user2_id, max_number, number=1):
        is_found = False
        tmp = {}
        for key, value in self.users.items():
            if is_found:
                break
            if value['number'] == number - 1:
                user1_followers = self.bot.get_user_followers(key)
                user1_following = self.bot.get_user_following(key)
                user1_friends = list(set(user1_followers) & set(user1_following))
                for friend in user1_friends:
                    if not self.users.get(friend):
                        tmp.update({friend: {'parent': key, 'number': number}})
                    if friend == user2_id:
                        is_found = True
                        break
        self.users.update(tmp)
        if (number != max_number) and not is_found:
            self._find_friends(user2_id, max_number, number=number + 1)

    def _find_rel(self, user2_id):
        result = []
        if not self.users.get(user2_id):
           number = self.users.get(user2_id)['number']
            user_id = user2_id
            while True:
                user_name = self.bot.get_username_from_user_id(user_id)
                result.append(user_name)
                user_id = self.users.get(user_id)['parent']
                number -= 1
                if number == -1:
                    break
        return result


if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    user_first = os.getenv("user1")
    user_second = os.getenv("user2")
    instagram = InstaParse(user_first, user_second, 4, login=os.getenv("inst_login"), password=os.getenv("inst_password"))
    print(instagram.run())