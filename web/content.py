import bson
from functools import wraps
from flask import request, redirect, url_for
from connection import _content
from context.content import get_article
from context.nlp.classifier import classify_text
from context.nlp.entities import get_entities
from context.nlp.keywords import get_keywords
from auth import get_twitter_credentials
from stakeholders import find_stakeholder_twitter_users, stakeholder_tweets


class InvalidRequest(Exception):
    status_code = 400


def content_keywords(content):
    if not 'keywords' in content:
        content['keywords'] = [x for x in get_keywords(content['text'])
            if x['count'] > 2]      
        _content.save(content)
    return content['keywords']


def content_entities(content):
    if not 'entities' in content:
        content['entities'] = get_entities(content['text'])   
        _content.save(content)
    return content['entities']


def content_categories(content):
    if not 'categories' in content:
        content['categories'] = classify_text(content['text'])
        _content.save(content)
    return content['categories']


def content_stakeholders(content, app='stakeholder'):
    if not 'stakeholders' in content:
        entities = content_entities(content)
        kwargs = {
            'section': app,
            'credentials': get_twitter_credentials(app)
        }
        stakeholder_list = find_stakeholder_twitter_users(
            content['text'], entities, **kwargs)
        content['stakeholders'] = stakeholder_list
        _content.save(content)
    return content['stakeholders']


def cached_content(url=None, content_id=None):
    """Retrieve content from the cache or fetch it and cache it. Replaces
    Mongo's _id with id."""
    if url:
        r = _content.find_one({'url': url})
    elif content_id:
        r = _content.find_one({'_id': bson.ObjectId(content_id)})
    else:
        raise Exception('No Content Identifier') 
    if not r:
        data = get_article(url)
        r = {
            'url': url,
            'title': data['title'],
            'text': data['text']
        }
        _content.insert(r, manipulate=True)  # so id is set
    r['id'] = str(r['_id'])
    del r['_id']
    return r


def content_identifier_required(f):
    """Enforces url query parameter on a route."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        content_id = kwargs.get('content_id')
        if content_id is None:
            content_id = request.args.get('id')
        if not 'url' in request.args and content_id is None:
            if 'application/json' not in request.headers['Accept'] and \
                    request.args.get('_format') != 'json':
                return redirect(url_for('url_required') + \
                    '?next=%s' % request.script_root + request.path)
            else:
                raise InvalidRequest('url parameter is required')
        if content_id:
            r = cached_content(content_id=content_id)
        else:
            url = request.args.get('url')
            if not url:
                raise InvalidRequest('URL or content ID required.')
            r = cached_content(url=url)
        if not r:
            raise Exception('Could not find article content')
        request.content = r
        return f(*args, **kwargs)
    return wrapper
