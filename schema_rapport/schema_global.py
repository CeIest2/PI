from diagrams import Cluster, Diagram
from diagrams.programming.language import Python

with Diagram("Parallélisme", show=False):
    source = Python("Source")
    
    with Cluster("Traitement en Parallèle"):
        worker1 = Python("Worker 1")
        worker2 = Python("Worker 2")
        worker3 = Python("Worker 3")
        
    source >> [worker1, worker2, worker3]