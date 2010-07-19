from twisted.words.xish import domish
from wokkel.xmppim import MessageProtocol, AvailablePresence

from eizzek.lib.registry import registry

class EizzekProtocol(MessageProtocol):
    
    @property
    def _my_jid(self):
        return self.parent.jid.full()
    
    def connectionMade(self):
        print 'Connected'
        self.send(AvailablePresence())
    
    def connectionLost(self, reason):
        print 'Disconnected'
    
    def onMessage(self, msg):
        if msg["type"] == 'chat' and hasattr(msg, "body") and msg.body:
            self.answer(msg)
    
    def answer(self, message):
        body = self.match( str(message.body) )
        reply = self.build_response( to=message['from'], body=body )
        self.send(reply)
    
    # FIXME: this logic should go to PluginRegistry
    def match(self, body):
        for name, (regex, func) in registry.plugins.items():
            match = regex.match(body)
            if not match:
                continue
            
            # TODO: for now, it's not possible to mix args and kwargs
            kwargs = match.groupdict()
            if kwargs:
                return func(**kwargs)
            
            args = match.groups()
            if args:
                return func(*args)
            
            return func()
        
        return u"I can't understand..."
    
    def build_response(self, to, body):
        reply = domish.Element((None, "message"))
        reply["to"] = to
        reply["from"] = self._my_jid
        reply["type"] = 'chat'
        reply.addElement("body", content=body)
        return reply

