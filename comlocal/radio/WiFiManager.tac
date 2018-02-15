from twisted.spread import pb
from twisted.application import internet, service
from comlocal.radio.WiFiManager import WiFiManager, WiFiTransport

iface = "0.0.0.0"

topService = service.MultiService()

wifiManager = WiFiManager()
wifiTransport = WiFiTransport()
wifiManager.setTransport(wifiTransport)
wifiTransport.setManager(wifiManager)

pbService = internet.TCPServer(WiFiManager.myPort, pb.PBServerFactory(wifiManager))
pbService.setServiceParent(topService)

udpService = internet.UDPServer(WiFiTransport.myPort, wifiTransport)
udpService.setServiceParent(topService)

application = service.Application('wifimanager')
topService.setServiceParent(application)