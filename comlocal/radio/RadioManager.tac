from twisted.application import internet, service
from twisted.spread import pb
from comlocal.radio.RadioManager import RadioManager


port = RadioManager.myPort
iface = '127.0.0.1'

application = service.Application("RadioManager")
myService = internet.TCPServer(port, pb.PBServerFactory(RadioManager()), interface=iface)
myService.setServiceParent(application)