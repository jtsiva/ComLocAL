from comlocal.core.Com import Com
from twisted.spread import pb
from twisted.application import internet, service


port = Com.myPort
iface = "127.0.0.1"
configFile = 'default.conf'


application = service.Application("Com")
myService = internet.TCPServer(port, pb.PBServerFactory(Com(configFile=configFile)), interface=iface)
myService.setServiceParent(application)