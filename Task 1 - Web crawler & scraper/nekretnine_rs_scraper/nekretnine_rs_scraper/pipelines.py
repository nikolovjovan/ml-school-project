# ref: https://github.com/IaroslavR/scrapy-mysql-pipeline/blob/master/scrapy_mysql_pipeline/pipeline.py

import logging
import pprint

from itemadapter import is_item, ItemAdapter
from nekretnine_rs_scraper.items import Nekretnina

import pymysql

from pymysql.cursors import DictCursor

from pymysql import OperationalError
from pymysql.constants.CR import CR_SERVER_GONE_ERROR, CR_SERVER_LOST, CR_CONNECTION_ERROR
from scrapy.exceptions import NotConfigured
from twisted.internet import defer
from twisted.enterprise import adbapi

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

def get_param(params, key, default):
    if params is not None and key in params:
        return params[key]
    return default

class PyMySqlPipeline:
    stats_name = 'pymysql_pipeline'

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def __init__(self, crawler):
        self.stats = crawler.stats
        self.settings = crawler.settings
        params = self.settings.get('PYMYSQL_PARAMS')
        if not params:
            raise NotConfigured
        db_args = {
            'host': get_param(params, 'host', 'localhost'),
            'port': get_param(params, 'port', 3306),
            'user': get_param(params, 'user', 'root'),
            'password': get_param(params, 'pass', ''),
            'db': get_param(params, 'db', ''),
            'charset': get_param(params, 'charset', 'utf8'),
            'cursorclass': DictCursor,
            'cp_reconnect': True
        }
        self.retries = get_param(params, 'retries', 3)
        self.close_on_error = get_param(params, 'close_on_error', True)
        self.upsert = get_param(params, 'upsert', False)
        self.table = get_param(params, 'table', False)
        self.db = adbapi.ConnectionPool('pymysql', **db_args)

    def close_spider(self, spider):
        self.db.close()

    @defer.inlineCallbacks
    def process_item(self, item, spider):
        retries = self.retries
        while retries:
            try:
                yield self.db.runInteraction(self._process_item, item)
            except OperationalError as e:
                if e.args[0] in (
                        CR_SERVER_GONE_ERROR,
                        CR_SERVER_LOST,
                        CR_CONNECTION_ERROR,
                ):
                    retries -= 1
                    logger.info('%s %s attempts to reconnect left', e, retries)
                    self.stats.inc_value('{}/reconnects'.format(self.stats_name))
                    continue
                logger.exception('%s', pprint.pformat(item))
                self.stats.inc_value('{}/errors'.format(self.stats_name))
            except Exception:
                logger.exception('%s', pprint.pformat(item))
                self.stats.inc_value('{}/errors'.format(self.stats_name))
            break
        else:
            if self.close_on_error:  # Close spider if connection error happened and MYSQL_CLOSE_ON_ERROR = True
                spider.crawler.engine.close_spider(spider, '{}_fatal_error'.format(self.stats_name))
        yield item

    def _fetch_id(self, tx, tblname, value):
        tx.execute('SELECT id FROM `{}` WHERE naziv = "{}"'.format(tblname, value))
        res = tx.fetchone()
        return res['id'] if res is not None else None

    def _get_id(self, tx, tblname, value):
        res = self._fetch_id(tx, tblname, value)
        if res is not None:
            return res
        tx.execute('INSERT INTO `{}` (naziv) VALUES ("{}")'.format(tblname, value))
        return self._fetch_id(tx, tblname, value)

    def _get_key_value(self, adapter, keyname):
        return adapter[keyname][0] if keyname in adapter else None

    def _get_key_id(self, tx, tblname, adapter, keyname):
        return self._get_id(tx, tblname, adapter[keyname][0]) if keyname in adapter else None

    def _generate_insert_sql(self, data):
        columns = lambda d: ', '.join(['`{}`'.format(k) for k in d])
        placeholders = lambda d: ', '.join(['%s'] * len(d))
        values = lambda d: [v for v in d.values()]
        if self.upsert:
            sql_template = 'INSERT INTO `{}` ( {} ) VALUES ( {} ) ON DUPLICATE KEY UPDATE {}'
            on_duplicate_placeholders = lambda d: ', '.join(['`{}` = %s'.format(k) for k in d])
            return (
                sql_template.format(
                    self.table, columns(data),
                    placeholders(data), on_duplicate_placeholders(data)
                ),
                values(data) + values(data)
            )
        else:
            sql_template = 'INSERT INTO `{}` ( {} ) VALUES ( {} )'
            return (
                sql_template.format(self.table, columns(data), placeholders(data)),
                values(data)
            )

    def _generate_update_sql(self, data):
        sql_template = 'UPDATE `{}` SET udaljenost = {} WHERE id = "{}"'
        return sql_template.format(self.table, data['udaljenost'], data['id'])

    def _process_item(self, tx, item):
        if (is_item(item)):
            adapter = ItemAdapter(item)
            sqlItem = dict()
            sqlItem['id'] = self._get_key_value(adapter, 'id')
            if isinstance(item, Nekretnina):
                sqlItem['tip_id'] = self._get_key_id(tx, 'tip_nekretnine', adapter, 'tip')
                sqlItem['prodaja'] = self._get_key_value(adapter, 'prodaja')
                sqlItem['cena'] = self._get_key_value(adapter, 'cena')
                sqlItem['drzava_id'] = self._get_key_id(tx, 'drzava', adapter, 'drzava')
                sqlItem['grad_id'] = self._get_key_id(tx, 'grad', adapter, 'grad')
                sqlItem['deo_grada_id'] = self._get_key_id(tx, 'deo_grada', adapter, 'deo_grada')
                sqlItem['kvadratura'] = self._get_key_value(adapter, 'kvadratura')
                sqlItem['godina_izgradnje'] = self._get_key_value(adapter, 'godina_izgradnje')
                sqlItem['klasa_id'] = self._get_key_id(tx, 'klasa_izgradnje', adapter, 'klasa')
                sqlItem['povrsina_zemljista'] = self._get_key_value(adapter, 'povrsina_zemljista')
                sqlItem['ukupna_spratnost'] = self._get_key_value(adapter, 'ukupna_spratnost')
                sqlItem['sprat'] = self._get_key_value(adapter, 'sprat')
                sqlItem['uknjizenost'] = self._get_key_value(adapter, 'uknjizenost')
                sqlItem['tip_grejanja_id'] = self._get_key_id(tx, 'tip_grejanja', adapter, 'tip_grejanja')
                sqlItem['broj_soba'] = self._get_key_value(adapter, 'broj_soba')
                sqlItem['broj_kupatila'] = self._get_key_value(adapter, 'broj_kupatila')
                sqlItem['parking'] = self._get_key_value(adapter, 'parking')
                sqlItem['lift'] = self._get_key_value(adapter, 'lift')
                sqlItem['terasa'] = self._get_key_value(adapter, 'terasa')
                sql, data = self._generate_insert_sql(sqlItem)
            else:
                sqlItem['udaljenost'] = self._get_key_value(adapter, 'udaljenost')
                sql = self._generate_update_sql(sqlItem)
            try:
                if isinstance(item, Nekretnina):
                    tx.execute(sql, data)
                else:
                    tx.execute(sql)
            except pymysql.err.IntegrityError:
                # Duplicate entries are ignored...
                #
                pass
            except Exception:
                logger.error("SQL: %s", sql)
                raise
            self.stats.inc_value('{}/saved'.format(self.stats_name))