from __future__ import absolute_import
import re
import json
from collections import OrderedDict

from .base import Code, CodeGenerator
import six

SUPPORT_METHODS = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']


class Router(Code):
    template = 'wxapp/routers.tpl'
    dest_template = '%(package)s/model/%(view)s.js'
    override = True


class View(Code):
    template = 'wxapp/view.tpl'
    dest_template = '%(package)s/model/%(module)s/%(view)s.js'
    override = True


class Core(Code):
    template = 'wxapp/core.tpl'
    dest_template = '%(package)s/http/base.js'


def _swagger_to_js_url(url, swagger_path_node):
    types = {
        'integer': 'int',
        'long': 'int',
        'float': 'float',
        'double': 'float'
    }
    node = swagger_path_node
    params = re.findall(r'\{([^\}]+?)\}', url)
    url = re.sub(r'{(.*?)}', '<<\\1>>', url)

    def _type(parameters):
        for p in parameters:
            if p.get('in') != 'path':
                continue

            yield '<<%s>>' % p['name'], '" + obj.%s + "' % p['name']

    for old, new in _type(node.get('parameters', [])):
        url = url.replace(old, new) + '"'

    for k in SUPPORT_METHODS:
        if k in node:
            for old, new in _type(node[k].get('parameters', [])):
                url = url.replace(old, new)
    url = '"' + url + '"'
    return url, params


if six.PY3:
    def _remove_characters(text, deletechars):
        return text.translate({ord(x): None for x in deletechars})
else:
    def _remove_characters(text, deletechars):
        return text.translate(None, deletechars)


def _path_to_endpoint(swagger_path):
    name = _remove_characters(swagger_path.title(), '{}/_-')
    return name[0].lower() + name[1:]


def _path_to_resource_name(swagger_path):
    return _remove_characters(swagger_path.title(), '{}/_-')


def _location(swagger_location):
    location_map = {
        'body': 'json',
        'header': 'headers',
        'formData': 'form',
        'query': 'args'
    }
    return location_map.get(swagger_location)


def _process_param(param, type='normal'):
    def _param_dict(k, v, _requeied):
        res = {'name': k,
               'type': v.get('type', 'ref'),
               'required': True if k in _requeied else False}
        if 'description' in v:
            res['description'] = v.get('description')
        if 'default' in v:
            res['default'] = v.get('default')
        return res
    if type == 'body':
        _body = param['schema']['properties']
        _requeied = param['schema'].get('required', [])
        return [_param_dict(k, v, _requeied) for k, v in _body.iteritems()]

    elif type == 'response':
        if 'properties' in param['schema']:
            _body = param['schema']['properties']
            _requeied = param['schema'].get('required', [])
            return {'properties': [_param_dict(k, v, _requeied)
                                   for k, v in _body.iteritems()],
                    'type': 'object'}
        else:
            _type = param['schema']['type']
            if _type == 'array':
                _items = param['schema']['items']
                if 'properties' in _items:
                    _body = _items['properties']
                    _requeied = param['schema']['items'].get('required', [])
                    return {'items': [_param_dict(k, v, _requeied)
                                      for k, v in _body.iteritems()],
                            'type': _type}
                else:
                    return {'items': [param['schema']['items']],
                            'type': _type}
            else:
                return {'type': 'object'}
    else:
        res = {'name': param['name'],
               'type': param['type'],
               'required': param.get('required', False)}
        if 'description' in param:
            res['description'] = param.get('description')
        if 'default' in param:
            res['default'] = param.get('default')
        return res



class WxAppGenerator(CodeGenerator):
    def __init__(self, swagger):
        super(WxAppGenerator, self).__init__(swagger)
        self.with_spec = False
        self.with_ui = False
        self.build_data()

    def build_data(self):

        pass

    def _process_data(self):

        views = []  # [{'endpoint':, 'name':, url: '', params: [], methods: {'get': {'requests': [], 'response'}}}, ..]
        tags = OrderedDict()

        for paths, data in self.swagger.search(['paths', '*']):

            swagger_path = paths[-1]
            url, params = _swagger_to_js_url(swagger_path, data)
            endpoint = _path_to_endpoint(swagger_path)
            name = _path_to_resource_name(swagger_path)

            methods = OrderedDict()
            for method in SUPPORT_METHODS:
                if method not in data:
                    continue
                _method_data = {}
                method_params = data[method].get('parameters')
                if method_params:
                    _params = []
                    _headers = []
                    _path_params = []
                    for _p in method_params:
                        if _p['in'] == 'header':
                            _headers.append(_process_param(_p))
                        elif _p['in'] == 'path':
                            _path_params.append(_process_param(_p))
                        elif _p['in'] == 'query':
                            _params.append(_process_param(_p))
                        else:  # in body
                            _params.extend(_process_param(_p, 'body'))
                    _method_data['headers'] = _headers
                    _method_data['params'] = _params
                    _method_data['path'] = _path_params
                method_responses = data[method].get('responses')
                _responses = {}
                for _st, _resp in method_responses.iteritems():
                    if _st == 'default':
                        continue
                    _responses[_st] = _process_param(_resp, 'response')
                _method_data['response'] = _responses
                methods[method] = _method_data
                for tag in data[method]['tags']:
                    d = dict(
                        url=url,
                        endpoint=endpoint,
                        name=name,
                    )
                    if tag.title() in tags:
                        if d not in tags[tag.title()]:
                            tags[tag.title()].append(d)
                    else:
                        tags[tag.title()] = [d]

            views.append(dict(
                url=url,
                params=params,
                endpoint=endpoint,
                methods=methods,
                name=name,
                base_path=self.swagger.base_path
            ))

        return views, tags

    def _get_oauth_scopes(self):
        for path, scopes in self.swagger.search(
                ('securityDefinitions', '*', 'scopes')):
            return scopes
        return None

    def _process(self):
        views, tags = self._process_data()
        for tag, vs in tags.iteritems():
            filename = self.swagger.module_name + tag + 'Api'
            yield Router(dict(views=vs,
                              base_path=self.swagger.module_name,
                              tag_name=tag), dist_env=dict(view=filename))
        for view in views:
            yield View(view, dist_env=dict(view=view['endpoint']))

        yield Core()