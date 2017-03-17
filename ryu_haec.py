# Copyright (C) 2014 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Usage example

1. Join switches (use your favorite method):
$ sudo mn --controller remote --topo tree,depth=3

2. Run this application:
$ PYTHONPATH=. ./bin/ryu run \
    --observe-links ryu/app/gui_topology/gui_topology.py

3. Access http://<ip address of ryu host>:8080 with your web browser.
"""

import os, json, random

from webob.static import DirectoryApp

from ryu.app.wsgi import ControllerBase, WSGIApplication, route, Response
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet, ipv4, arp
from ryu.lib.packet import ether_types
from ryu.lib.mac import haddr_to_bin
from ryu.lib.dpid import dpid_to_str

PATH = os.path.dirname(__file__)

# Serving static files
class HaecApp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]
    _CONTEXTS = {
        'wsgi': WSGIApplication,
    }

    def __init__(self, *args, **kwargs):
        super(HaecApp, self).__init__(*args, **kwargs)

        wsgi = kwargs['wsgi']
        wsgi.register(HaecController, {'haec_api_app': self})

        self.flows = {}

    def get_flows(self):
        return self.flows

    def add_flow(self, dp, srcip, dstip, out_port, ifname):
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser

        dpid = dpid_to_str(dp.id)

        cookie = int(dpid[-3:] + "".join(srcip.split(".")[1:]) + "".join(dstip.split(".")[1:]))

        # to add a flow we have to define some match criteria
        match = ofp_parser.OFPMatch(
            dl_type=0x0800, # ipv4
            nw_src=srcip,
            nw_dst=dstip)

        # we also need to define the desired action
        actions = [ofp_parser.OFPActionOutput(out_port)]

        # now we build a flow table entry
        flow = ofp_parser.OFPFlowMod(
            datapath=dp, # assign datapath
            command=ofp.OFPFC_ADD, # we want to add a new flow
            match=match, # define match criteria for the flow table entry
            cookie=cookie, # can be used to identify the flow
            idle_timeout=10, hard_timeout=0, # the flow entry never times out
            priority=ofp.OFP_DEFAULT_PRIORITY,
            flags=ofp.OFPFF_SEND_FLOW_REM,
            actions=actions)

        # send it to the switch
        dp.send_msg(flow)

        self.flows[cookie] = {"dpid": dpid_to_str(dp.id), "port": out_port, "src": srcip, "dst": dstip, "ifname": ifname}

    def port_from_ip(self, dp, ip):
        from ryu.topology.api import get_switch, get_link, get_host

        ofp = dp.ofproto
        #links = get_switch(self, dp.id)

        switch = get_switch(self, dp.id)[0]
        ports = switch.ports

        curpos = dpid_to_str(dp.id)[-3:]
        dstpos = "".join(ip.split(".")[-3:])

        for i in range(3):
            ports = [p for p in ports if p.name[-3+i] == dstpos[i]]
            print(i, dpid_to_str(dp.id), ip, [h.name for h in ports])
            if curpos[i] != dstpos[i]:
                break

        if len(ports) > 0:
            print("done", dpid_to_str(dp.id), ip, [h.name for h in ports])
            hop = random.choice(ports)
            return (hop.port_no, hop.name)
        else:
            return (None, "DROP")

    @set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def flow_removed_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto

        if msg.cookie in self.flows:
            del self.flows[msg.cookie]

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        arppkt = pkt.get_protocol(arp.arp)
        ip = pkt.get_protocol(ipv4.ipv4)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        if arppkt:
            out_port, _ = self.port_from_ip(dp, arppkt.dst_ip)
        elif ip:
            out_port, ifname = self.port_from_ip(dp, ip.dst)
            self.add_flow(dp, ip.src, ip.dst, out_port, ifname)
        else:
            self.logger.debug('Message for unknown: %s' % msg)
            out_port = None
            return

        if out_port:
            actions = [ofp_parser.OFPActionOutput(out_port)]
        else:
            actions = []

        out = ofp_parser.OFPPacketOut(datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port, actions=actions)
        dp.send_msg(out)

class HaecController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(HaecController, self).__init__(req, link, data, **config)
        self.haec_api_app = data['haec_api_app']
        path = "%s/html/" % PATH
        self.static_app = DirectoryApp(path)

    @route('topology', '/v1.0/flows')
    def flows_handler(self, req, **kwargs):
        body = json.dumps(self.haec_api_app.get_flows())
        return Response(content_type='application/json', body=body)

    @route('topology', '/{filename:.*}')
    def static_handler(self, req, **kwargs):
        if kwargs['filename']:
            req.path_info = kwargs['filename']
        return self.static_app(req)


app_manager.require_app('ryu.app.rest_topology')
app_manager.require_app('ryu.app.ws_topology')
app_manager.require_app('ryu.app.ofctl_rest')
