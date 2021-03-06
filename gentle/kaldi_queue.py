import sys
from gentle import standard_kaldi

if sys.version[0] == '2':
    from Queue import Queue
else:
    from queue import Queue

def build(resources, nthreads=4, hclg_path=None):

    if hclg_path is None: hclg_path = resources.full_hclg_path

    kaldi_queue = Queue()
    for i in range(nthreads):
        kaldi_queue.put(standard_kaldi.Kaldi(
            resources.nnet_gpu_path,
            hclg_path,
            resources.proto_langdir)
        )
    return kaldi_queue
