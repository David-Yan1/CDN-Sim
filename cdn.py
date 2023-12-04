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

def get_stats(user : User):
    for request in user.received:
        elapsed_time = request.receive_time - request.create_time
        if request.item is None: 
            print(f"Request {request.request_id} for item of tag {request.item_tag} not fulfilled")
        else:
            print(f"Request {request.request_id} for item of tag {request.item_tag} fulfilled in {elapsed_time}")

def user_send_request(request, sim):
    user = request.source
    proc_time = sim.simulator_time + calculate_latency(user.coords, user.node.coords)
    func = partial(node_receive_request, request = request, sim = sim)
    heapq.heappush(sim.event_queue, Event(func, proc_time, sim.simulator_time))

def user_receive_item(request, sim):
    request.receive_time = sim.simulator_time
    request.source.received.append(request)

def node_receive_request(request, sim):
    user = request.source
    node = request.dest
    if request.item_tag in node.cache.keys():
        request.item = node.cache[request.item_tag]
        proc_time = sim.simulator_time + calculate_latency(user.coords, node.coords)
        func = partial(user_receive_item, request = request, sim = sim)
        heapq.heappush(sim.event_queue, Event(func, proc_time, sim.simulator_time))
    else:
        proc_time = sim.simulator_time + calculate_latency(node.coords, node.origin.coords)
        func = partial(origin_receive_request, request = request, sim = sim)
        heapq.heappush(sim.event_queue, Event(func, proc_time, sim.simulator_time))

def origin_receive_request(request, sim):
    node = request.dest
    origin = node.origin
    if request.item_tag in origin.content.keys():
        request.item = origin.content[request.item_tag]
    proc_time = sim.simulator_time + calculate_latency(node.coords, origin.coords)
    func = partial(node_receive_item, request = request,  sim = sim)
    heapq.heappush(sim.event_queue, Event(func, proc_time, sim.simulator_time))

def node_receive_item(request, sim):
    user = request.source
    node = request.dest
    if request.item is not None and len(request.item) <= node.cache.maxsize:
        node.cache[request.item_tag] = request.item
    proc_time = sim.simulator_time + calculate_latency(user.coords, node.coords)
    func = partial(user_receive_item, request = request, sim = sim)
    heapq.heappush(sim.event_queue, Event(func, proc_time, sim.simulator_time))

 
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
            count = 0
            user.workload = sorted(user.workload, key=lambda x: x[1])
            for item, time in user.workload:
                request = Request(user, user.node, item, f"{user.id}.{count}" , time)
                func = partial(user_send_request, request = request, sim = self)
                heapq.heappush(self.event_queue, Event(func, time, 0))
                count += 1

    def run(self):
        while len(self.event_queue) != 0:
            event = heapq.heappop(self.event_queue)
            print(event)
            self.simulator_time = event.proc_time 
            event.event_func()     

class Item:
    def __init__(self, tag, size):
        self.item_tag = tag
        self.size = size

    def __len__(self):
        return self.size
     
class Origin:
    def __init__(self, coords, content):
        self.coords = coords
        self.content = content

    def distribute_content(self, server, request):
        pass

class LRU_Node:
    def __init__(self, coords, origin, cache_size, bandwidth):
        self.coords = coords
        self.cache = ct.LRUCache(cache_size, len)
        self.origin = origin
        self.bandwidth = bandwidth

class User:
    received = []
    def __init__(self, coords, workload, node : LRU_Node, id):
        self.coords = coords
        self.workload = workload
        self.node = node
        self.id = id

class Request:
    def __init__(self, source, dest, item_tag, request_id, create_time):
        self.source = source
        self.dest = dest
        self.item_tag = item_tag
        self.item = None
        self.request_id = request_id
        self.create_time = create_time 
        self.receive_time = None

def main():
    origin = Origin((0, 2000 * 10^3), {1 : Item(1,6), 2 : Item(1,6)})
    node = LRU_Node((0,500 * 10^3), origin, 7, 0)
    user = User((0,0), [(1, 5), (1, 250), (2, 26), (2, 300), (3, 19)], node, 0)
    sim = Simulator([user], [origin], [node])
    
    sim.initial_schedule()
    sim.run()

    get_stats(user)


if __name__ == "__main__":
    main()
