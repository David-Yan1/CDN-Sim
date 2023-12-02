import cachetools as ct
import math
import heapq


def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calculate_latency(point1, point2): # one way latency, assumes dist are in units of kilometers 
    return math.floor(calculate_distance(point1, point2) / 200000 * 1000) # 2/3 speed of light, adjusted for ms units

            
class Event:
    def __init__(self, event_func, proc_time, schedule_time, *args):
        self.event_func = event_func
        self.proc_time = proc_time # time that event is processed 
        self.schedule_time = schedule_time  # time event was scheduled
        self.args = args
    
    def __lt__(self, other):
        return self.proc_time < other.proc_time

    def __ge__(self, other):
        return self.proc_time >= other.proc_time

    def __eq__(self, other):
        return self.proc_time == other.proc_time


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
                request = Request(user, item, id)
                heapq.heappush(self.event_queue, Event(user.send_request, time, 0, request))
                id += 1

    def run(self):
        while len(self.event_queue) != 0:
            event = heapq.heappop(self.event_queue)
            self.simulator_time = event.proc_time 
            event.event_func(*event.args, self)     
     
class Origin:
    def __init__(self, coords, content):
        self.coords = coords
        self.content = content

    def distribute_content(self, server, request):
        pass

class Request:
    def __init__(self, user, item, request_id):
        self.user = user
        self.item = item
        self.request_id = request_id

class LRU_Node:
    def __init__(self, coords, origin, cache_size, bandwidth):
        self.coords = coords
        self.cache = ct.LRUCache(cache_size)
        self.origin = origin
        self.bandwidth = bandwidth

    def receive_request(self, request : Request, sim):
        if request.item in self.cache.keys():
            proc_time = sim.simulator_time + calculate_latency(self.coords, request.user.coords)
            heapq.heappush(sim.event_queue, 
            Event(request.user.receive_requested, proc_time, sim.simulator_time, request.request_id))
        else:
            return self.origin.distribute_content(self, request)

class User:
    received = {}
    def __init__(self, coords, workload, node : LRU_Node):
        self.coords = coords
        self.workload = workload
        self.node = node

    def send_request(self, request, sim):
        proc_time =  sim.simulator_time + calculate_latency(self.coords, self.node.coords)
        heapq.heappush(sim.event_queue, Event(self.node.receive_request, proc_time, sim.simulator_time, request))

    def receive_requested(self,request_id, sim):
        self.received[request_id] = sim.simulator_time
        print(f"Received request of id {request_id} at {sim.simulator_time}")
            

def main():
    origin = Origin((0, 2000), {1 : 500, 2 : 200})
    node = LRU_Node((0,500), origin, 5, 0)
    node.cache[1] =  20
    user = User((0,0), [(1, 5), (1, 26)], node)

    sim = Simulator([user], [origin], [node])
    
    sim.initial_schedule()
    sim.run()

if __name__ == "__main__":
    main()
