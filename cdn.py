from __future__ import annotations
import cachetools as ct
import math
import heapq
import queue
import random
import statistics
from functools import partial
import numpy as np


node_wait = 10 # 200 requests per second
congestion_reroute = False
reroute_threshold = 50

def calculate_distance(point1, point2):
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calculate_latency(point1, point2): # one way latency, assumes dist are in units of kilometers 
    return math.floor(calculate_distance(point1, point2) / 200000 * 1000) # 2/3 speed of light, adjusted for ms units

def get_stats(user : User):
    for request in user.received:
        print(request)

def find_closest_node(user, sim):
    closest_nodes = sorted(sim.nodes, key=lambda x: calculate_distance(user.coords, x.coords))
    for node in closest_nodes:
        if node.request_queue.qsize() < reroute_threshold:
            return node
    return None

def user_send_request(request, sim):
    user = request.source
    node = request.node

    if congestion_reroute and node.request_queue.qsize() >= reroute_threshold:
        reroute_node = find_closest_node(user, sim)
       # print(f"Reroute Node ID: {reroute_node.id}")
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
        proc_time = sim.simulator_time + node_wait
        func = partial(node_serve_requests, node = node, sim = sim) # serve requests will recursively handle requests until the queue is empty
        heapq.heappush(sim.event_queue, Event(func, proc_time, sim.simulator_time)) # node instantly processes first request
    node.request_queue.put(request)

def node_serve_requests(node, sim):
   # print(f"Current Queue Size: {node.request_queue.qsize()}. Time: {sim.simulator_time}" )
    if node.request_queue.qsize() > node.max_queue_length:
        node.max_queue_length = node.request_queue.qsize() 
    request = node.request_queue.get()
    user = request.source
    node.num_requests +=1
    if request.item_tag in node.cache.keys():
        node.cache_hits +=1
        request.cache_hit = True
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
        proc_time = sim.simulator_time + node_wait
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


    def __init__(self, users, origins, nodes):
        self.users = users
        self.origins = origins
        self.nodes = nodes
        self.event_queue = []
        self.simulator_time = 0

    def initial_schedule(self):
        for user in self.users:
            count = 0
            user.workload = sorted(user.workload, key=lambda x: x[1])
            for item, time in user.workload:
                request = Request(user, find_closest_node(user, self), item, f"{user.id}.{count}" , time)
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

class Node:
    def __init__(self, coords, origin, cache_size, cache_type, id):
        self.coords = coords
        self.origin = origin
        self.id = id
        self.used_conns = 0
        self.request_queue = queue.Queue()
        self.max_queue_length = 0
        self.cache_hits = 0
        self.num_requests = 0
        match cache_type:
            case 0:
                self.cache = ct.LRUCache(cache_size, len)
            case 1:
                self.cache = ct.FIFOCache(cache_size, len)
            case 2:
                self.cache = ct.LFUCache(cache_size, len)

class User:
    def __init__(self, coords, workload, id):
        self.coords = coords
        self.workload = workload
        self.id = id
        self.received = []

class Request:
    def __init__(self, source, node : Node, item_tag, request_id, create_time):
        self.source = source
        self.node = node
        self.item_tag = item_tag
        self.item = None
        self.request_id = request_id
        self.create_time = create_time 
        self.receive_time = None
        self.cache_hit = False

    def __str__(self):
        return f"Request {self.request_id} for Tag: {self.item_tag}, Created At: {self.create_time} ms, Completed At: {self.receive_time} ms, Time Elapsed: {self.receive_time - self.create_time}, Cache Hit: {self.cache_hit}"

def run_simulation(coordinates, node_coordinates, user_coordinates, cache_policy, cache_size, max_concurrent_requests, reroute_requests=False):
    # TODO: replace main call with simulation consuming parameters
    # example input: {'userCoordinates': [[61.13194783528646, 44.944437662760414]], 'cachePolicy': 0, 'cacheSize': 50, 'rerouteRequests': False, 'maxConcurrentRequests': 50, 'coordinates': [33.131947835286454, 33.6111094156901], 'nodeCoordinates': [[61.13194783528646, 44.944437662760414], [65.79861450195312, 25.27777099609375], [19.798614501953125, 31.27777099609375], [19.63194783528646, 37.944437662760414], [35.298614501953125, 58.94443766276042], [65.9652811686198, 40.611104329427086]]}
    # note: cache policy: 0= LRU, 1 = FIFO, 2 = LFU
    requests, nodes, elapsed_time = simulate_inputs(coordinates, node_coordinates, user_coordinates, cache_policy, cache_size, max_concurrent_requests, reroute_requests=False)

     
    cache_hit_ratios = [(node.cache_hits / node.num_requests * 100) for node in nodes]
    queue_lengths = [node.max_queue_length for node in nodes]
    elapsed_times = [request.receive_time - request.create_time for request in requests]
    average_hit_ratio = statistics.mean(cache_hit_ratios)
    average_wait_time = statistics.mean(elapsed_times)
    total_wait_time = sum(elapsed_times)
    max_queue_length = max(queue_lengths)
    max_wait_time = max(elapsed_times)
    min_wait_time = min(elapsed_times)

    # for request in requests:
    #     print(request)
    # print(average_hit_ratio)
    # print(average_wait_time)
    # print(queue_lengths)

    # TODO: replace these results
    results = {
        # all requests made, sorted in chronological order
        "requests": [
            # format: [request origin coordinates (normalized to 0-100), request destination coordinates, timestamp, cache hit?]
            [str(request) for request in requests]
        ],
        # coordinates, all normalized to (0-100)
        "user_locations": [
            user_coordinates
        ],
        "origin_location": coordinates,
        "node_locations": [
            node_coordinates
        ],
        #statistics
        "cache_hit_percentage": average_hit_ratio,
        "total_requests": len(requests),
        "average_request_wait_time": average_wait_time,
        "total_wait_time": total_wait_time,
        "min_request_wait_time": min_wait_time,
        "max_wait_time": max_wait_time,
        "total_time_elapsed": elapsed_time,
        "max_queue_length": max_queue_length,
        # plus any other statistics you want to add
    }
    return {"data": results}

def simulate_inputs(origin_coords, node_coords, user_coords, cache_policy, cache_size, max_request_per_second, reroute_requests):
    global node_wait, congestion_reroute
    congestion_reroute = reroute_requests
    node_wait = math.floor(1000 / max_request_per_second)

    origin_coords = [400 * x for x in origin_coords]
    node_coords = [[400 * y for y in x] for x in node_coords]
    user_coords = [[400 * y for y in x] for x in user_coords]

    num_items = random.randint(cache_size * 2, cache_size * 5)
    items = {}
    for i in range(num_items):
        items[i] = Item(i, 1)

    origin = Origin(origin_coords, items)

    nodes = []
    for count, coords in enumerate(node_coords):
        node = Node(coords, origin, cache_size, cache_policy, count)
        nodes.append(node)

    users = []

    samples = np.ones(num_items)
    samples[random.randint(0, num_items-1)] *= num_items

    count = 0
    for coords in user_coords:
        for i in range(100):
            workload = []
            for j in range(20):
                x = random.choices(list(range(0, num_items)), samples)[0]
                y = random.randint(0, 10 * 1000)
                workload.append((x,y))
            user = User(coords, workload, count)
            users.append(user)
            count += 1
    
    sim = Simulator(users, [origin], nodes)
    sim.initial_schedule()
    sim.run()

    requests = [request for user in users for request in user.received ]
    requests = sorted(requests, key=lambda x: x.create_time)

    return requests, nodes, sim.simulator_time
        
def main():
    origin = Origin([0, 2000], {1 : Item(1,4), 2 : Item(2,5), 3 : Item(3,2)})
    node1 = Node([0,500], origin, 100, 0, 0)
    node2 = Node([0,800], origin, 7, 0, 1)
    node3 = Node([0,700], origin, 7, 0, 2)

    workload = []
    random.seed(34239042)

    user1 = User([0,0], [(1, 5), (1, 250), (2, 26), (2, 300), (3, 19)], 0)
    user2 = User([0, 0], workload, 1)
    sim = Simulator([user1], [origin], [node1, node2, node3])

    sim.initial_schedule()
    sim.run()

    get_stats(user1)
  #  get_stats(user2)
    print(f"Cache Hit Percentage: {node1.cache_hits / node1.num_requests * 100}")


if __name__ == "__main__":
    run_simulation([0, 100], [[0,50]],[[0,0]], 2, 10, 200, False)
