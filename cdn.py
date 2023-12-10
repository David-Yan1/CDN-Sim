from __future__ import annotations
import cachetools as ct
import math
import heapq
import queue
import random
from functools import partial

NODE_WAIT = 10 # 200 requests per second
CONGESTION_REROUTE = True
REROUTE_THRESHOLD = 40

def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calculate_latency(point1, point2): # one way latency, assumes dist are in units of kilometers 
    return math.floor(calculate_distance(point1, point2) / 200000 * 1000) # 2/3 speed of light, adjusted for ms units

def get_stats(user : User):
    for request in user.received:
        print(request)

def find_closest_node(user, sim):
    closest_nodes = sorted(sim.nodes, key=lambda x: calculate_distance(user.coords, x.coords))
    for node in closest_nodes:
        if node.request_queue.qsize() < REROUTE_THRESHOLD:
            return node
    return None

def user_send_request(request, sim):
    user = request.source
    node = request.node

    if CONGESTION_REROUTE and node.request_queue.qsize() >= REROUTE_THRESHOLD:
        reroute_node = find_closest_node(user, sim)
        print(f"Reroute Node ID: {reroute_node.id}")
        if reroute_node is not None:
            request.node = reroute_node
            node = reroute_node

    proc_time = sim.simulator_time + calculate_latency(user.coords, node.coords)
    func = partial(node_receive_request, request = request, sim = sim)
    heapq.heappush(sim.event_queue, Event(func, proc_time, sim.simulator_time))

def user_receive_item(request, sim):
    request.receive_time = sim.simulator_time
    request.source.received.append(request)

def node_receive_request(request, sim):
    node = request.node
    if node.request_queue.qsize() == 0: 
        proc_time = sim.simulator_time + NODE_WAIT
        func = partial(node_serve_requests, node = node, sim = sim) # serve requests will recursively handle requests until the queue is empty
        heapq.heappush(sim.event_queue, Event(func, proc_time, sim.simulator_time)) # node instantly processes first request
    node.request_queue.put(request)

def node_serve_requests(node, sim):
    print(f"Current Queue Size: {node.request_queue.qsize()}. Time: {sim.simulator_time}" )
    request = node.request_queue.get()
    user = request.source
    node.num_requests +=1
    if request.item_tag in node.cache.keys():
        node.cache_hits +=1
        request.item = node.cache[request.item_tag]
        proc_time = sim.simulator_time + calculate_latency(user.coords, node.coords)
        func = partial(user_receive_item, request = request, sim = sim)
        heapq.heappush(sim.event_queue, Event(func, proc_time, sim.simulator_time))
    else:
        proc_time = sim.simulator_time + calculate_latency(node.coords, node.origin.coords)
        func = partial(origin_receive_request, request = request, sim = sim)
        heapq.heappush(sim.event_queue, Event(func, proc_time, sim.simulator_time))
    
    if node.request_queue.qsize() != 0:
        func = partial(node_serve_requests, node = node, sim = sim)
        proc_time = sim.simulator_time + NODE_WAIT
        heapq.heappush(sim.event_queue, Event(func, proc_time, sim.simulator_time)) 

def origin_receive_request(request, sim):
    node = request.node
    origin = node.origin
    if request.item_tag in origin.content.keys():
        request.item = origin.content[request.item_tag]
    proc_time = sim.simulator_time + calculate_latency(node.coords, origin.coords)
    func = partial(node_receive_item, request = request,  sim = sim)
    heapq.heappush(sim.event_queue, Event(func, proc_time, sim.simulator_time))

def node_receive_item(request, sim):
    user = request.source
    node = request.node
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
        return (self.proc_time, self.schedule_time) < (other.proc_time, other.schedule_time)

    def __ge__(self, other):
        return (self.proc_time, self.schedule_time) >= (other.proc_time, other.schedule_time)

    def __eq__(self, other):
        return (self.proc_time, self.schedule_time) == (other.proc_time, other.schedule_time)

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
            #print(event)
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
    def __init__(self, coords, origin, cache_size, id):
        self.coords = coords
        self.cache = ct.LRUCache(cache_size, len)
        self.origin = origin
        self.id = id
        self.used_conns = 0
        self.request_queue = queue.Queue()
        self.cache_hits = 0
        self.num_requests = 0

class User:
    def __init__(self, coords, workload, node : LRU_Node, id):
        self.coords = coords
        self.workload = workload
        self.node = node
        self.id = id
        self.received = []

class Request:
    def __init__(self, source, node : LRU_Node, item_tag, request_id, create_time):
        self.source = source
        self.node = node
        self.item_tag = item_tag
        self.item = None
        self.request_id = request_id
        self.create_time = create_time 
        self.receive_time = None

    def __str__(self):
        return f"Request {self.request_id} for Tag: {self.item_tag}, Created At: {self.create_time} ms, Completed At: {self.receive_time} ms, Time Elapsed: {self.receive_time - self.create_time}"

def run_simulation(coordinates, node_coordinates, user_coordinates, cache_policy, cache_size, max_concurrent_requests, reroute_requests=False):
    # TODO: replace main call with simulation consuming parameters
    # example input: {'userCoordinates': [[61.13194783528646, 44.944437662760414]], 'cachePolicy': 0, 'cacheSize': 50, 'rerouteRequests': False, 'maxConcurrentRequests': 50, 'coordinates': [33.131947835286454, 33.6111094156901], 'nodeCoordinates': [[61.13194783528646, 44.944437662760414], [65.79861450195312, 25.27777099609375], [19.798614501953125, 31.27777099609375], [19.63194783528646, 37.944437662760414], [35.298614501953125, 58.94443766276042], [65.9652811686198, 40.611104329427086]]}
    # note: cache policy: 0= LRU, 1 = FIFO, 2 = LFU
    main()

    # TODO: replace these results
    dummy_return = {
        # all requests made, sorted in chronological order
        "requests": [
            # format: [request origin coordinates (normalized to 0-100), request destination coordinates, timestamp, cache hit?]
            [[50,82], [23, 42], 5341, True],
            [[50,20], [1, 17], 6954, False]
        ],
        # coordinates, all normalized to (0-100)
        "user_locations": [
            [50,82], [50,20]
        ],
        "origin_location": [10,54],
        "node_locations": [
            [23, 42], [1, 17]
        ],
        #statistics
        "cache_hit_percentage": 54.5,
        "total_requests": 10023432,
        "average_request_wait_time": 332,
        "total_time": 3464363
        # plus any other statistics you want to add
    }
    return {"data": dummy_return}


def main():
    origin = Origin((0, 2000 * 10^3), {1 : Item(1,4), 2 : Item(2,5), 3 : Item(3,2)})
    node1 = LRU_Node((0,500 * 10^3), origin, 7, 0)
    node2 = LRU_Node((0,800 * 10^3), origin, 7, 1)
    node3 = LRU_Node((0,700 * 10^3), origin, 7, 2)

    workload = []
    for i in range(900):
        x = random.randint(1,3)
        y = random.randint(0, 5000)
        workload.append((x,y))
    user1 = User((0,0), [(1, 5), (1, 250), (2, 26), (2, 300), (3, 19)], node1, 0)
    user2 = User((0, 0), workload, node1, 1)
    sim = Simulator([user1, user2], [origin], [node1, node2, node3])


    sim.initial_schedule()
    sim.run()

    get_stats(user1)
    get_stats(user2)
    print(f"Cache Hit Percentage: {node1.cache_hits / node1.num_requests * 100}")


if __name__ == "__main__":
    main()
