from django.db import models
from core.models.donkey_user import DonkeyUser


class UserBoardConnector(models.Model):
    donkey_user = models.OneToOneField(DonkeyUser)
    bulletin_board_id_str = models.TextField(null=True)

    def set_bulletinboard_id(self, bulletinboard_id):
        value = self.bulletin_board_id_str
        if not value:
            value = format('{},'.format(bulletinboard_id))
        else:
            value += format('{},'.format(bulletinboard_id))

        id_list = list(map(int, value.split(',')[:-1]))
        id_list = sorted(set(id_list))
        value_to_db = ','.join(str(x) for x in id_list) + ','
        self.bulletin_board_id_str = value_to_db
        self.save()

    def get_bulletinboard_id(self):
        value = self.bulletin_board_id_str
        return list(map(int, value.split(',')[:-1]))

    def pop_bulletinboard_id(self, bulletinboard_id):
        value = self.bulletin_board_id_str
        id_list = list(map(int, value.split(',')[:-1]))
        if bulletinboard_id in id_list:
            id_list.remove(bulletinboard_id)
            value_to_db = ','.join(str(x) for x in id_list) + ','
            self.bulletin_board_id_str = value_to_db
            self.save()

    def check_bulletinboard_id(self, bulletinboard_id):
        bulletinboard_id = int(bulletinboard_id)

        value = self.bulletin_board_id_str
        if not value:
            return False
        else:
            id_list = list(map(int, value.split(',')[:-1]))

            return bulletinboard_id in id_list
