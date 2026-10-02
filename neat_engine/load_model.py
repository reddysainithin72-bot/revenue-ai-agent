from pathlib import Path
import pickle, neat
ROOT=Path(__file__).resolve().parents[1]; MODEL=ROOT/'data/neat_best.pkl'; CONFIG=ROOT/'neat_engine/config-feedforward.txt'
def load_model():
    if not MODEL.exists(): raise FileNotFoundError('Run python neat_engine/trainer.py first')
    with open(MODEL,'rb') as f: genome=pickle.load(f)
    config=neat.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,str(CONFIG)); return neat.nn.FeedForwardNetwork.create(genome,config)
