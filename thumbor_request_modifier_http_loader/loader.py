#!/usr/bin/python
# -*- coding: utf-8 -*-


from thumbor.loaders import http_loader
from tornado.concurrent import return_future
from thumbor.utils import logger


def _url_contains(context, url, params):
    logger.debug(u"Checking if URL \"%s\" contains \"%s\"", url, params['cond_url_part'])
    return params['cond_url_part'] in url


condition_handlers = {
    'url_contains': _url_contains
}


def _set_header(context, url, params):
    logger.debug(u"Setting header \"%s\": \"%s\"", params['mod_header_name'], params['mod_header_value'])
    context.request_handler.request.headers[params['mod_header_name']] = params['mod_header_value']


modification_handlers = {
    'set_header': _set_header
}


def _modify_request(context, url):
    for modification in context.config.REQUEST_MODIFIER_HTTP_LOADER_MODIFICATIONS:
        modification_params = {
            key: value for (key, value) in zip(
                [modification[i] for i in range(0, len(modification), 2)],
                [modification[i] for i in range(1, len(modification), 2)],
            )
        }
        logger.debug(u"Applying modification with params: %s", str(modification_params))
        condition_handler = condition_handlers[modification_params['cond_type']]
        if condition_handler(context, url, modification_params):
            modification_handler = modification_handlers[modification_params['mod_type']]
            modification_handler(context, url, modification_params)
    logger.debug(u"Request headers after modification: %s", str(context.request_handler.request.headers))


@return_future
def load(context, url, callback):
    _modify_request(context, url)
    return http_loader.load_sync(context, url, callback, normalize_url_func=http_loader._normalize_url)
