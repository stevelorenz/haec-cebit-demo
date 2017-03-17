angular.module("topology", []).controller("Topology", function($scope, $http, $timeout) {

    $scope.scale = 50;

    function switchPos(name, offset) {
            var x = parseInt(name[offset+2]);
            var y = parseInt(name[offset+1]);
            var z = parseInt(name[offset+0]);
            return {
                x: x, y: y, z: z
            };
    }

    function curve(src, dst) {
        var startx = (src.x*4 + src.y)*$scope.scale;
        var starty = (src.z*4 - src.y)*$scope.scale;
        var start = startx+","+starty;

        var endx = (dst.x*4 + dst.y)*$scope.scale;
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

    function ip_to_number(ip) {
        var parts = ip.split(".");
        var x = parseInt(parts[3])-1;
        var y = parseInt(parts[2])-1;
        var z = parseInt(parts[1])-1;

        return x + y*3 + z*9;
    }

    function hue(flow) {
        var srcval = (ip_to_number(flow.src)*19)%27;
        var dstval = (ip_to_number(flow.dst)*23)%27;
        var val = srcval+dstval*27;
        var norm = val/(27*27);

        return 360*val/(27*27);
    }

    $http({
        method: "GET",
        url: "v1.0/topology/switches"
    }).then(function(response) {
        $scope.switches = response.data.map(function (s) {
            return switchPos(s.dpid,13);
        });

        $scope.links = Array.prototype.concat.apply([], response.data.map(function (s) {
            return s.ports.map(function (p) {
                var src = switchPos(p.name,1);
                var dst = switchPos(p.name,6);

                return {
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
            $scope.flows = Object.keys(response.data).map(function (id) {
                var flow = response.data[id];
                var ifname = flow.ifname;

                var src = switchPos(ifname, 1);
                var dst = switchPos(ifname, 6);

                return {
                    src: src,
                    dst: dst,
                    path: curve(src, dst),
                    color: "hsl("+hue(flow)+", 100%, 50%)"
                };
            });
        });

        setTimeout(refresh, 1000);
    }

    refresh();
});
