'''
Created on May 2, 2012

@package: superdesk source
@copyright: 2012 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

API specifications for source. A source provides content, the source type of a source dictates the format in which
the content is received from the source.
'''

from .type import SourceType
from ally.api.config import service, call, query
from ally.api.criteria import AsBoolean
from ally.api.type import Iter
from ally.support.api.entity import Entity, IEntityGetCRUDService, QEntity
from superdesk.api.domain_superdesk import modelSuperDesk

# --------------------------------------------------------------------

@modelSuperDesk
class Source(Entity):
    '''
    Provides the source model.
    '''
    Type = SourceType
    Name = str
    URI = str
    IsModifiable = bool

# --------------------------------------------------------------------

@query
class QSource(QEntity):
    '''
    Provides the query for source model.
    '''
    isModifiable = AsBoolean

# --------------------------------------------------------------------

@service((Entity, Source))
class ISourceService(IEntityGetCRUDService):
    '''
    Provides the service methods for the source.
    '''

    @call
    def getAll(self, typeKey:SourceType.Key=None, offset:int=None, limit:int=None, q:QSource=None) -> Iter(Source):
        '''
        Provides all the available sources.
        '''

