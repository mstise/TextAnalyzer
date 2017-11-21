import time
from NamedEntityDisambiguator import Construct_mention_entity
import os

def main():
    start = time.time()

    for filename in os.listdir("/home/duper/Desktop/entiti/"):
        G = Construct_mention_entity(filename)





    end = time.time()
    print(end - start)

main()