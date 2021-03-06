import json
import logging

import web

from mypinnings import database
from mypinnings import session
from mypinnings import template
from mypinnings import cached_models
from mypinnings.conf import settings
from mypinnings import auth


logger = logging.getLogger('mypinnings.categories')


class PageCategory:
    def GET(self, slug=None):
        self.db = database.get_db()
        self.sess = session.get_session()
        auth.force_login(self.sess)
        if slug:
            results = self.db.where('categories', slug=slug)
            for r in results:
                self.category = r
                break
            else:
                self.category = {'name':'Random', 'id': 0}
        else:
            self.category = {'name':'Random', 'id': 0}

        self.ajax = int(web.input(ajax=0).ajax)
        
        if self.ajax:
            return self.get_more_items_as_json()
        else:
            return self.template_for_showing_categories()
        
    def get_items_query(self):
        if self.category['id'] == 0:
            self.where = 'random() < 0.1'
        else:
            results = self.db.where(table='categories', parent=self.category['id'])
            subcategories_ids = [str(self.category['id']),]
            for row in results:
                subcategories_ids.append(str(row.id))
            subcategories_string = ','.join(subcategories_ids)
            self.where = 'categories.id in ({})'.format(subcategories_string)
        start = web.input(start=False).start
        if start:
            offset = 0
            self.sess['offset'] = 0
        else:
            offset = self.sess.get('offset', 0)
        self.query = '''
            select
                tags.tags, pins.*, categories.id as category, categories.name as cat_name, users.pic as user_pic,
                users.username as user_username, users.name as user_name,
                count(distinct p1) as repin_count,
                count(distinct l1) as like_count
            from pins
                left join tags on tags.pin_id = pins.id
                left join pins p1 on p1.repin = pins.id
                left join likes l1 on l1.pin_id = pins.id
                left join users on users.id = pins.user_id
                left join follows on follows.follow = users.id
                join pins_categories on pins.id=pins_categories.pin_id
                join categories on pins_categories.category_id = categories.id
            where ''' + self.where + '''
            group by tags.tags, categories.id, pins.id, users.id
            order by timestamp desc offset %d limit %d''' % (offset * settings.PIN_COUNT, settings.PIN_COUNT)
        return self.query

    def template_for_showing_categories(self):
        subcategories = self.db.where(table='categories', parent=self.category['id'], order='is_default_sub_category desc, name')
        results = self.db.where(table='categories', parent=self.category['parent'], order='is_default_sub_category desc, name')
        siblings_categories = []
        for row in results:
            if row.id != self.category['id']:
                siblings_categories.append(row)
        results = self.db.where(table='categories', id=self.category['parent'])
        for row in results:
            parent = row
            break
        else:
            parent = None
        boards = self.db.where(table='boards', order='name', user_id=self.sess.user_id)
        return template.ltpl('category', self.category, cached_models.all_categories, subcategories, boards, siblings_categories, parent)

    def get_more_items_as_json(self):
        self.get_items_query()
        pins = self.db.query(self.query)
        pin_list = []
        current_pin = None
        for pin in pins:
            if not current_pin or current_pin.id != pin.id:
                current_pin = pin
                tag = pin.tags
                current_pin.tags = []
                if tag:
                    current_pin.tags.append(tag)
                pin_list.append(pin)
                pin.price = str(pin.price)
            else:
                tag = pin.tags
                if tag and tag not in current_pin.tags:
                    current_pin.tags.append(tag)
        offset = self.sess.get('offset', 0)
        if len(pin_list) > 0:
            offset = offset + 1
        self.sess['offset'] = offset
        json_pins = json.dumps(pin_list)
        return json_pins
