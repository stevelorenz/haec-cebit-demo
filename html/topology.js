angular.module("topology", []).controller("Topology", function($scope, $http, $timeout) {

    $scope.scale = 50;
    $scope.switches = [];
    $scope.links = [];
    $scope.flows = [];

    function switchPos(name, offset) {
            var x = parseInt(name[offset+2]);
            var y = parseInt(name[offset+1]);
            var z = parseInt(name[offset+0]);
            return {
                x: x, y: y, z: z
            };
    }

    function curve(src, dst) {
        var startx = (src.x*4-4 + src.y)*$scope.scale;
        var starty = (src.z*4 - src.y)*$scope.scale;
        var start = startx+","+starty;

        var endx = (dst.x*4-4 + dst.y)*$scope.scale;
        var endy = (dst.z*4 - dst.y)*$scope.scale;
        var end = endx+","+endy;

        var shift = 0;
        if (src.z == dst.z && (Math.abs(src.x - dst.x) > 1 || Math.abs(src.y - dst.y) > 1)) {
            shift = 50;
        }

        var cstart = startx+","+(starty+shift);
        var cend = endx+","+(endy+shift);

        return "M"+start+" C"+cstart+" " +cend+" "+end;
    }

    $http({
        method: "GET",
        url: "v1.0/topology/switches"
    }).then(function(response) {
        $scope.switches = response.data.map(function (data) {
            var s = switchPos(data.dpid,13);
            s.dpid = data.dpid;
            return s;
        });

        $scope.links = Array.prototype.concat.apply([], response.data.map(function (s) {
            return s.ports.map(function (p) {
                var src = switchPos(p.name,1);
                var dst = switchPos(p.name,6);

                return {
                    ifname: p.name,
                    src: src,
                    dst: dst,
                    path: curve(src, dst)
                };
            });
        })).filter(function (l) {
            return l.src.z == l.dst.z;
        });
    });

    function refresh() {
        $http({
            method: "GET",
            url: "v1.0/flows"
        }).then(function(response) {
            $scope.flows = Object.keys(response.data).reduce(function (flows, hopid) {
                var hop = response.data[hopid];
                var flowid = hop.src + "->" + hop.dst;
                var flow = flows.find(function (f) { return f.id == flowid; });
                if (!flow) {
                    flow = $scope.flows.find(function (f) { return f.id == flowid; });
                    if (flow) {
                        flow.hops = [];
                    } else {
                        flow = {
                            id: flowid,
                            hops: [],
                            color: "hsl("+(360*Math.random())+", 100%, 50%)"
                        };
                    }
                    flows.push(flow);
                }

                var ifname = hop.ifname;
                var src = switchPos(ifname, 1);
                var dst = switchPos(ifname, 6);

                flow.hops.push({
                    id: ifname,
                    src: src,
                    dst: dst,
                    path: curve(src, dst)
                });

                return flows;
            }, []);
        });

        setTimeout(refresh, 1000);
    }

    refresh();
});
