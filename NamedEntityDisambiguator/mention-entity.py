from lxml import etree
import paths
from NamedEntityDisambiguator import Prior
from NamedEntityDisambiguator import References
from NamedEntityDisambiguator import LinksToEntity

names = ['Kashmir', 'Grønland']

tree = etree.parse(paths.get_wikipedia_article_path())
root = tree.getroot()

priors = Prior.popularityPrior(names, root)
entities = []
for prior in priors:
    for entity in prior[1]:
        entities.append(entity[0])
similarity = References.References(root)
links_to_entity = LinksToEntity.links_to_me(entities, root)


test = 5