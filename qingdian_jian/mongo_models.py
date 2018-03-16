import json
import logging

logger = logging.getLogger(__name__)


class BaseMongoModel:
    """
    所有mongo_models的基类,仿照django的baseModel制作
    """
    # 集合的名字
    collection_name = ''
    # 集合是否是单一结构, 一般一个集合使用一种结构,但有的时候为了方便可以使用多种结构.
    # 为了便于维护,要维护多种结构,请把singleStructure设为False
    single_structure = True

    @staticmethod
    def set_multi_record(db, name, value, json_dump=False):
        """
        如果single_structure=False的话,设置值
        :param db:
        :param name:
        :param value:
        :return:
        """
        if json_dump:
            value = json.dumps(value)
        data = {'name': name, 'value': value}
        db.update({'name': name}, data, upsert=True)
        logger.debug(f'存入mongo缓存 {name}')

    @staticmethod
    def get_multi_record(db, name, json_dump=False):
        """
        如果 single_structure=False的话,取值
        :param db:
        :param name:
        :return:
        """
        value = db.find_one({'name': name}, projection={'value': True, '_id': False}).get('value', {})
        if json_dump:
            value = json.loads(value)
        logger.debug(f'取出mongo缓存 {name}')
        return value
