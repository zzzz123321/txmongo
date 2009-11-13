# coding: utf-8
# Copyright 2009 Alexandre Fiori
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pymonga import wire
from pymonga.tracker import Tracker
from pymonga._pymongo.objectid import ObjectId
from twisted.internet import reactor, protocol
from twisted.internet.defer import Deferred

"""An asynchronous Mongo driver for Python."""


class MongoFactory(protocol.ReconnectingClientFactory):
    protocol = wire.MongoProtocol

    def __init__(self, deferred):
        self.tracker = Tracker()
        self.deferred = deferred

    def buildProtocol(self, addr):
        p = self.protocol()
        p.factory = self
        self.tracker.append(p)
        if self.deferred is not None:
            reactor.callLater(0, self.deferred.callback, self.tracker)
            self.deferred = None
        return p


def ConnectionPool(host="localhost", port=27017, reconnect=True, size=5, defer=True):
    """Open a new connection to a Mongo instance at host:port.

    The resulting object is a deferred, which will be fired after the
    connection is made, unless defer=False is set.

    :Parameters:
     - `host` (optional, default=localhost): hostname or IPv4 of the Mongo instance
     - `port` (optional, default=27017): port number on which to connect
     - `reconnect` (optional, default=True): auto-reconnect when necessary
     - `size` (optional, default=5): number of connections to Mongo instance
     - `defer` (optional, default=True): when False, the deferred returned by
       Connection will be fired immediately, even if not connected.
       This is useful for using pymonga within web frameworks such as Twisted-web
       or Cyclone.
    """

    d = Deferred()
    factory = MongoFactory(d)
    factory.continueTrying = reconnect
    for x in xrange(size):
        reactor.connectTCP(host, port, factory)
    return defer and d or factory.tracker


def Connection(host="localhost", port=27017, reconnect=True, defer=True):
    """Open a new connection to a Mongo instance at host:port.

    The resulting object is a deferred, which will be fired after the
    connection is made, unless defer=False is set.

    :Parameters:
     - `host` (optional, default=localhost): hostname or IPv4 of the Mongo instance
     - `port` (optional, default=27017): port number on which to connect
     - `reconnect` (optional, default=True): auto-reconnect when necessary
     - `defer` (optional, default=True): when False, the deferred returned by
       Connection will be fired immediately, even if not connected.
       This is useful for using pymonga within web frameworks such as Twisted-web
       or Cyclone.
    """
    return ConnectionPool(host, port, reconnect, size=1, defer=defer)
