from lxml import etree
import paths
from NamedEntityDisambiguator import Prior
from NamedEntityDisambiguator import References
from NamedEntityDisambiguator import LinksToEntity

names = ['Kashmir', 'Grønland']

tree = etree.parse(paths.get_wikipedia_article_path())
root = tree.getroot()

prior = Prior.popularityPrior(names, root)
similarity = References.References(root)


test = 5