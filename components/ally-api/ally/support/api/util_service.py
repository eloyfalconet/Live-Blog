'''
Created on Feb 28, 2012

@package: ally api
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides utility methods for service implementations.
'''

from ally.type_legacy import Iterable, Iterator
import re
from ally.api.type import typeFor
from ally.api.operator.type import TypeQuery, TypeContainer, TypeModel
from inspect import isclass
from ally.api.criteria import AsBoolean, AsLike, AsEqual, AsOrdered
from itertools import chain

# --------------------------------------------------------------------

def namesForQuery(query):
    '''
    Provides the criteria names for the provided query object or class.
    
    @param query: query object|class
        The query to provide the criteria names for.
    @return: Iterator(string)
        The iterator containing the criteria names
    '''
    assert query is not None, 'A query object is required'
    if not isclass(query): qclazz = query.__class__
    else: qclazz = query
    queryType = typeFor(qclazz)
    assert isinstance(queryType, TypeQuery), 'Invalid query %s' % query
    return iter(queryType.query.criterias)

def namesForContainer(container):
    '''
    Provides the properties names for the provided container object or class.
    
    @param container: container object|class
        The container to provide the properties names for.
    @return: Iterator(string)
        The iterator containing the properties names
    '''
    assert container is not None, 'A container object is required'
    if not isclass(container): qcontainer = container.__class__
    else: qcontainer = container
    containerType = typeFor(qcontainer)
    assert isinstance(containerType, TypeContainer), 'Invalid container %s' % container
    return iter(containerType.container.properties)

def namesForModel(model):
    '''
    Provides the properties names for the provided model object or class.
    
    @param model: model object|class
        The model to provide the properties names for.
    @return: Iterator(string)
        The iterator containing the properties names
    '''
    assert model is not None, 'A model object is required'
    if not isclass(model): qmodel = model.__class__
    else: qmodel = model
    modelrType = typeFor(qmodel)
    assert isinstance(modelrType, TypeModel), 'Invalid model %s' % model
    return iter(modelrType.container.properties)

# --------------------------------------------------------------------

def trimIter(collection, size=None, offset=None, limit=None):
    '''
    Trims the provided iterator based on the offset and limit.
    
    @param collection: list|Iterable|Iterator|Sized
        The iterator to be trimmed.
    @param size: integer|None
        The size of the iterator, None if the collection is a list.
    @param offset: integer
        The offset to trim from
    @param limit: integer
        The limit to trim to.
    @return: generator
        A generator that will provide the trimmed iterator.
    '''
    assert offset is None or isinstance(offset, int), 'Invalid offset %s' % offset
    assert limit is None or isinstance(limit, int), 'Invalid limit %s' % limit
    if isinstance(collection, list):
        if not offset or offset < 0: offset = 0
        if offset > len(collection): offset = len(collection)
        if not limit or limit < 0: limit = 0
        delta = len(collection) - offset
        if limit > delta: limit = delta
        return (collection[k] for k in range(offset, offset + limit))

    assert isinstance(size, int), 'Invalid size %s' % size
    if isinstance(collection, Iterable): collection = iter(collection)
    assert isinstance(collection, Iterator), 'Invalid iterator %s' % collection

    if offset is None: offset = 0
    else: assert isinstance(offset, int), 'Invalid offset %s' % offset
    if limit is None: limit = size
    else: assert isinstance(limit, int), 'Invalid limit %s' % limit
    for _k in zip(range(0, offset), collection): pass
    return (v for v, _k in zip(collection, range(0, limit)))

def processQuery(objects, query, clazz):
    '''
    Filters the iterable of entities based on the provided query.
    
    @param objects: Iterable(model object of clazz)
        The entities objects iterator to be processed.
    @param query: query
        The query object to provide filtering on.
    @param clazz: class
        The model class to use the query on.
    @return: list[model object of clazz]
        The list of processed entities.
    '''
    assert isinstance(objects, Iterable), 'Invalid entities objects iterable %s' % objects
    assert query is not None, 'A query object is required'
    qclazz = query.__class__

    filtered = list(objects)
    ordered, unordered = [], []
    properties = {prop.lower(): prop for prop in namesForModel(clazz)}
    for criteria in namesForQuery(qclazz):
        prop = properties.get(criteria.lower())
        if prop is not None and getattr(qclazz, criteria) in query:
            crt = getattr(query, criteria)
            if isinstance(crt, AsBoolean):
                assert isinstance(crt, AsBoolean)
                if AsBoolean.value in crt:
                    filtered = [obj for obj in filtered if crt.value == getattr(obj, prop)]
            elif isinstance(crt, AsLike):
                assert isinstance(crt, AsLike)
                if AsLike.like in crt:
                    regex = likeAsRegex(crt.like, not crt.caseSensitive)
                    filtered = ((obj, getattr(obj, prop)) for obj in filtered)
                    filtered = [obj for obj, value in filtered if value is not None and regex.match(value)]
            elif isinstance(crt, AsEqual):
                assert isinstance(crt, AsEqual)
                if AsEqual.equal in crt:
                    filtered = [obj for obj in filtered if crt.equal == getattr(obj, prop)]
            if isinstance(crt, AsOrdered):
                assert isinstance(crt, AsOrdered)
                if AsOrdered.ascending in crt:
                    if AsOrdered.priority in crt and crt.priority:
                        ordered.append((prop, crt.ascending, crt.priority))
                    else:
                        unordered.append((prop, crt.ascending, None))

            ordered.sort(key=lambda pack: pack[2])
            for prop, asc, __ in reversed(list(chain(ordered, unordered))):
                filtered.sort(key=lambda obj: getattr(obj, prop), reverse=not asc)

    return filtered

# --------------------------------------------------------------------

def likeAsRegex(like, caseInsensitive=True):
    '''
    Transform a like pattern (ex: heloo%world) resembling a database form, to an actual regex that can be used to
    compare strings.
    
    @param like: string
        The like pattern to convert to regex.
    @param caseInsensitive: boolean
        Flag indicating that the regex should be case insensitive.
    @return: regex
        The regex pattern to use.
    '''
    assert isinstance(like, str), 'Invalid like %s' % like
    assert isinstance(caseInsensitive, bool), 'Invalid case insensitive %s' % caseInsensitive
    likeRegex = like.split('%')
    likeRegex = '.*'.join(re.escape(n) for n in likeRegex)
    likeRegex += '$'
    if caseInsensitive: likeRegex = re.compile(likeRegex, re.IGNORECASE)
    else: likeRegex = re.compile(likeRegex)
    return likeRegex