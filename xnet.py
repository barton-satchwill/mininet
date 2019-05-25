from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.node import UserSwitch
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
import sys

class Router( UserSwitch ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( Router, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( Router, self ).terminate()

    def start( self, controller ):
        super( Router, self ).start(controller)


class MX480( Router ):
    "A Node with IP forwarding enabled."

    # def config( self, **params ):
    #     super( MX480, self).config( **params )

    # def terminate( self ):
    #     super( MX480, self ).terminate()


class Xnet(Topo):
    """A model of the X network"""
    dp_id = 12

    def __init__(self, arg=None):
        super(Xnet, self).__init__(arg)
        self.arg = arg


    def build( self, *args, **params ):
        yeg480 = self.addRouter( 'yeg', cls=MX480 )
        r_itel = self.addRouter( 'itel', cls=Router )
        r_canarie_a = self.addRouter( 'can_a', cls=Router )
        r_super_a = self.addRouter( 'sup_a', cls=Router )
        # ----------------------------------------------
        yyc480 = self.addRouter( 'yyc', cls=MX480 )
        r_super_b = self.addRouter( 'sup_b', cls=Router )
        r_canarie_b = self.addRouter( 'can_b', cls=Router )
        r_lx = self.addRouter('lx', cls=Router )
        
        self.addLink( r_itel, yeg480 )
        self.addLink( yeg480, r_super_a )
        self.addLink( yeg480, r_canarie_a )        
        self.addLink( r_super_a, r_super_b)
        # self.addLink( r_canarie_a, r_canarie_b)
        self.addLink( r_canarie_b, yyc480 )
        self.addLink( r_super_b, yyc480 )
        self.addLink( yyc480, r_lx )
        
        # Lethbridge equipment
        # Lethbridge equipment links
        # Lethbridge hosts
        # Lethbridge host links


    def addRouter( self, name, inNamespace=True, **params ):
        r = self.addSwitch('r_'+name+"_%i" % self.dpid(), **params)
        h = self.addHost('h_'+name)
        self.addLink(r,h)
        return r


    def addDWDM( self, name, source, dest=None, fanout=1): 
        rx = self.addSwitch( name+"_rx%i" % self.dpid() )
        tx = self.addSwitch( name+"_tx%i" % self.dpid() )
        self.addLink( rx, tx )
        if dest == None:
            dest = self.addHost( 'h_'+name )

        # Hm, pingall stops working when fanout >1
        for n in range(fanout):      
            self.addLink( source, rx )
            self.addLink( tx, dest )


    def dpid(self):
        self.dp_id = self.dp_id + 1
        return self.dp_id




def test(cli):
    print("\n\n------- testing Xnet model --------\n")
    topology = Xnet()
    xnet = Mininet(topology)
    xnet.start()
    # dumpNodeConnections(xnet.hosts)
    xnet.pingAll()
    if cli == 'cli':
        CLI(xnet)
    xnet.stop()



if __name__ == '__main__':
    setLogLevel('info')
    arg = None
    if len(sys.argv) == 2 :
        arg = sys.argv[1]
    test(arg)
