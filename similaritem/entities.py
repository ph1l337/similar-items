import collections
from . import utils


class Index(object):

    def __init__(self, signature_size, threshold, high_recall=True):
        self.n_bands, self.n_rows = utils.compute_index_measures(signature_size, threshold, high_recall)
        self.bands = collections.defaultdict(dict)

    def index_documents(self, documents):
        pass
        #TODO: map a doc (ID/signature) to a set of (band, bucket)
