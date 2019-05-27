from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink

#
# http://csie.nqu.edu.tw/smallko/sdn/mininet_simple_router.htm
# 
#       r1
#      /  \
#    s1    s2
#   /  \  /  \
#  h1 h2 h3  h4
# 

def topology():
    net = Mininet( controller=RemoteController, link=TCLink, switch=OVSKernelSwitch )
    c0 = net.addController( 'c0', controller=RemoteController, ip='127.0.0.1', port=6633 )

    # Add hosts and switches
    r1 = net.addHost( 'r1' )
    s1 = net.addSwitch( 's1' )
    s2 = net.addSwitch( 's2' )

    h1 = net.addHost( 'h1', ip='10.0.1.10/24', mac='00:00:00:00:00:01' )
    h2 = net.addHost( 'h2', ip='10.0.1.20/24', mac='00:00:00:00:00:02' )
    h3 = net.addHost( 'h3', ip='10.0.2.10/24', mac='00:00:00:00:00:03' )
    h4 = net.addHost( 'h4', ip='10.0.2.20/24', mac='00:00:00:00:00:04' )

    net.addLink( r1, s1 )
    net.addLink( r1, s2 )
    net.addLink( s1, h1 )
    net.addLink( s1, h2 )
    net.addLink( s2, h3 )
    net.addLink( s2, h4 )

    net.build( )
    c0.start( )
    s1.start( [c0] )
    s2.start( [c0] )

    r1.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward') # enable ip forwarding

    for intf, mac, ip in [('0', '01:01','10.0.1.1'),('1', '01:02','10.0.2.1')]:
        addInterface(r1, intf, mac, ip)

    for h in [h1, h2]:
        h.cmd('ip route add default via 10.0.1.1')

    for h in [h3, h4]:
        h.cmd('ip route add default via 10.0.2.1')

    s1.cmd('ovs-ofctl add-flow s1 priority=1,arp,actions=flood')
    s1.cmd('ovs-ofctl add-flow s1 priority=65535,ip,dl_dst=00:00:00:00:01:01,actions=output:1')
    s1.cmd('ovs-ofctl add-flow s1 priority=10,ip,nw_dst=10.0.1.10,actions=output:2')
    s1.cmd('ovs-ofctl add-flow s1 priority=10,ip,nw_dst=10.0.1.20,actions=output:3')

    s2.cmd('ovs-ofctl add-flow s2 priority=1,arp,actions=flood')
    s2.cmd('ovs-ofctl add-flow s2 priority=65535,ip,dl_dst=00:00:00:00:01:02,actions=output:1')
    s2.cmd('ovs-ofctl add-flow s2 priority=10,ip,nw_dst=10.0.2.10,actions=output:2')
    s2.cmd('ovs-ofctl add-flow s2 priority=10,ip,nw_dst=10.0.2.20,actions=output:3')
    print'----------------'
    print s2.name
    print'----------------'

    CLI( net )

    net.stop()

def addInterface(device, intf, mac, ip):
    device.cmd('ifconfig r1-eth'+intf+' 0')
    device.cmd('ifconfig r1-eth'+intf+' hw ether 00:00:00:00:'+mac)
    device.cmd('ip addr add '+ip+'/24 brd + dev r1-eth'+intf)


def addFlow(switch, mac, ip, out):
    switch.cmd('ovs-ofctl add-flow '+switch.name+' priority=1,arp,actions=flood')
    switch.cmd('ovs-ofctl add-flow '+switch.name+' priority=65535,ip,dl_dst=00:00:00:00:01:02,actions=output:1')
    switch.cmd('ovs-ofctl add-flow '+switch.name+' priority=10,ip,nw_dst=10.0.2.10,actions=output:2')
    switch.cmd('ovs-ofctl add-flow '+switch.name+' priority=10,ip,nw_dst=10.0.2.20,actions=output:3')


if __name__ == '__main__':
    setLogLevel( 'info' )
    topology() 
