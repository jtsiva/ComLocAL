from twisted.application import internet, service
from twisted.spread import pb
from comlocal.radio.Dummy import Dummy


port = Dummy.myPort
iface = '127.0.0.1'

application = service.Application("Dummy")
myService = internet.TCPServer(port, pb.PBServerFactory(Dummy()), interface=iface)
myService.setServiceParent(application)