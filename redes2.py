import time
import heapq

class Interface:
    def __init__(self, ip):
        self.ip = ip
        self.input_queue = []
        self.output_queue = []

class Packet:
    def __init__(self, src_ip, dest_ip, ttl, tos):
        self.src_ip = src_ip
        self.dest_ip = dest_ip
        self.ttl = ttl
        self.tos = tos

class Network:
    def __init__(self):
        self.nodes = set()
        self.edges = {}
    
    def add_node(self, node):
        self.nodes.add(node)
    
    def add_edge(self, node1, node2, weight):
        if node1 not in self.edges:
            self.edges[node1] = {}
        self.edges[node1][node2] = weight
        if node2 not in self.edges:
            self.edges[node2] = {}
        self.edges[node2][node1] = weight

class Router:
    def __init__(self, algo, network):
        self.interfaces = [Interface("10.10.10.1"), Interface("20.20.20.1"), Interface("30.30.30.1"), Interface("40.40.40.1")]
        self.routing_table = {}
        self.routing_table["10.10.10.0/24"] = {"interface": "eth0", "metric": 1}
        self.routing_table["20.20.20.0/24"] = {"interface": "eth1", "metric": 1}
        self.routing_table["30.30.30.0/24"] = {"interface": "eth2", "metric": 1}
        self.routing_table["40.40.40.0/24"] = {"interface": "eth3", "metric": 1}
        self.algo = algo
        self.routing_packets = []
        self.network = network
        
    def send_packet(self, packet):
        dest_network = self.get_network_address(packet.dest_ip)
        if dest_network in self.routing_table:
            interface = self.routing_table[dest_network]["interface"]
            self.interfaces[self.get_interface_index(interface)].output_queue.append(packet)
        else:
            print("Packet dropped: destination network not found in routing table")
    
    def receive_packet(self, interface):
        if len(interface.input_queue) > 0:
            packet = interface.input_queue.pop(0)
            if packet.ttl > 0:
                packet.ttl -= 1
                self.send_packet(packet)
                print("Packet sent: " + packet.src_ip + " -> " + packet.dest_ip)
            else:
                print("Packet dropped: TTL expired")
    
    def update_routing_table(self):
        if self.algo == "link_state":
            print("Using link state algorithm")
            # Crie uma lista vazia para armazenar as informações de roteamento
            routing_table = []
            
            # Para cada nó na rede
            for node in self.network.nodes:
                # Execute o algoritmo de Dijkstra para encontrar o caminho mais curto para todos os outros nós
                shortest_paths = self._dijkstra(node)
                
                # Adicione as informações de roteamento para esse nó na lista de roteamento
                routing_table.append({"node": node, "shortest_paths": shortest_paths})
                
            # Atualize a tabela de roteamento
            self.routing_table = routing_table
            print("Routing table updated", self.routing_table)
        else:
            print("Using distance vector algorithm")
            # Crie um dicionário para armazenar a tabela de roteamento atualizada
            updated_routing_table = {}

            # Para cada interface
            for interface in self.interfaces:
                for dest_network, dest_info in self.routing_table.items():
                    if dest_info["interface"] != interface.ip:
                        # Calcule a nova distância para a interface
                        new_distance = dest_info["metric"] + 1  # 1 é o custo da interface

                        if dest_network not in updated_routing_table:
                            # Adicione a nova entrada na tabela de roteamento atualizada
                            updated_routing_table[dest_network] = {"interface": interface.ip, "metric": new_distance}
                        else:
                            # Se a nova distância for menor do que a distância registrada, atualize a entrada na tabela de roteamento atualizada
                            if new_distance < updated_routing_table[dest_network]["metric"]:
                                updated_routing_table[dest_network]["interface"] = interface.ip
                                updated_routing_table[dest_network]["metric"] = new_distance

            # Atualize a tabela de roteamento
            self.routing_table = updated_routing_table
            print("Routing table updated", self.routing_table)

    def start(self):
        print("Starting router...")
        while True:
            print("Router listening...")
            # Recebe pacotes de todas as interfaces
            for interface in self.interfaces:
                self.receive_packet(interface)
            
            # Envia pacotes para todas as interfaces
            for interface in self.interfaces:
                for packet in self.routing_packets:
                    interface.output_queue.append(packet)
            
            # Atualiza a tabela de roteamento
            self.update_routing_table()
            
            # Espera 1 segundo
            time.sleep(1)
            
    def get_network_address(self, ip):
        return ".".join(ip.split(".")[:3]) + ".0/24"
    
    def get_interface_index(self, interface_name):
        for i in range(len(self.interfaces)):
            if self.interfaces[i].ip == interface_name:
                return i
        return -1
    

    def _dijkstra(self, start_node):
        # Crie um dicionário para armazenar as distâncias mínimas para cada nó
        distances = {node: float('inf') for node in self.network.nodes}
        
        # Defina a distância mínima para o nó inicial como zero
        distances[start_node] = 0
        
        # Crie uma fila de prioridade usando heapq
        pq = [(0, start_node)]
        
        # Enquanto a fila de prioridade não estiver vazia
        while pq:
            
            # Retire o nó com a menor distância da fila de prioridade
            current_distance, current_node = heapq.heappop(pq)
            
            # Se a distância atual for maior do que a distância registrada, pule
            if current_distance > distances[current_node]:
                continue
            
            # Para cada vizinho do nó atual
            for neighbor, weight in self.network.edges[current_node].items():
                
                # Calcule a distância até o vizinho
                distance = current_distance + weight
                
                # Se a distância for menor do que a distância registrada, atualize a distância mínima e adicione o vizinho à fila de prioridade
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(pq, (distance, neighbor))
                    
        # Retorne um dicionário com as distâncias mínimas para cada nó
        return distances
    
def main():
    # Cria a rede
    network = Network()

    # Adiciona os nós
    network.add_node("node1")
    network.add_node("node2")
    network.add_node("node3")
    network.add_node("node4")

    # Adiciona as conexões
    network.add_edge("node1", "node2", 2)
    network.add_edge("node1", "node3", 1)
    network.add_edge("node2", "node3", 1)
    network.add_edge("node3", "node4", 3)
    network.add_edge("node1", "node4", 1)

    router = Router("link_state", network)
    router.start()

if __name__ == "__main__":
    main()
