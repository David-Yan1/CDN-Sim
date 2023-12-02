from __future__ import annotations
import cachetools as ct
import math
import heapq
from functools import partial


def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calculate_latency(point1, point2): # one way latency, assumes dist are in units of kilometers 
    return math.floor(calculate_distance(point1, point2) / 200000 * 1000) # 2/3 speed of light, adjusted for ms units

def user_send_request(request, sim):
    user = request.source
    proc_time = sim.simulator_time + calculate_latency(user.coords, user.node.coords)
    func = partial(node_receive_request, request = request, sim = sim)
    heapq.heappush(sim.event_queue, Event(func, proc_time, sim.simulator_time))

def user_receive_request(request, sim):
    request.source.received[request.request_id] = sim.simulator_time
    print(f"Received request of id {request.request_id} at {sim.simulator_time}")

def node_receive_request(request, sim):
    user = request.source
    node = request.dest
    if request.item in node.cache.keys():
        proc_time = sim.simulator_time + calculate_latency(user.coords, node.coords)
        func = partial(user_receive_request, request = request, sim = sim)
        heapq.heappush(sim.event_queue, 
        Event(func, proc_time, sim.simulator_time))
    else:
        pass
            
class Event:
    def __init__(self, event_func, proc_time, schedule_time):
        self.event_func = event_func
        self.proc_time = proc_time # time that event is processed 
        self.schedule_time = schedule_time  # time event was scheduled
    
    def __lt__(self, other):
        return self.proc_time < other.proc_time

    def __ge__(self, other):
        return self.proc_time >= other.proc_time

    def __eq__(self, other):
        return self.proc_time == other.proc_time

    def __str__(self):
        return f"Event Type: {self.event_func.func.__name__}, Event Trigger Time: {self.proc_time}, Scheduled At: {self.schedule_time} "


class Simulator:
    event_queue = []
    simulator_time = 0

    def __init__(self, users, origins, nodes):
        self.users = users
        self.origins = origins
        self.nodes = nodes

    def initial_schedule(self):
        for user in self.users:
            id = 0
            for item, time in user.workload:
                request = Request(user, user.node, item, id)
                func = partial(user_send_request, request = request, sim = self)
                heapq.heappush(self.event_queue, Event(func, time, 0))
                id += 1

    def run(self):
        while len(self.event_queue) != 0:
            event = heapq.heappop(self.event_queue)
            print(event)
            self.simulator_time = event.proc_time 
            event.event_func()     
     
class Origin:
    def __init__(self, coords, content):
        self.coords = coords
        self.content = content

    def distribute_content(self, server, request):
        pass

class LRU_Node:
    def __init__(self, coords, origin, cache_size, bandwidth):
        self.coords = coords
        self.cache = ct.LRUCache(cache_size)
        self.origin = origin
        self.bandwidth = bandwidth


class User:
    received = {}
    def __init__(self, coords, workload, node : LRU_Node):
        self.coords = coords
        self.workload = workload
        self.node = node



class Request:
    def __init__(self, source, dest, item, request_id):
        self.source = source
        self.dest = dest
        self.item = item
        self.request_id = request_id
            

def main():
    origin = Origin((0, 2000 * 10^3), {1 : 500, 2 : 200})
    node = LRU_Node((0,500 * 10^3), origin, 5, 0)
    node.cache[1] =  20
    user = User((0,0), [(1, 5), (1, 26)], node)

    sim = Simulator([user], [origin], [node])
    
    sim.initial_schedule()
    sim.run()

if __name__ == "__main__":
    main()
