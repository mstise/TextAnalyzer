from Metromap_generation.nmf import Nmf

def factorize(V, rank, resetter, W=None, H=None, update="log_update", objective="log_obj"):
    #Do this: V = V.tocsr(), before nmf, if update is eucledian or divergence... makes it faster
    nmf_inst = Nmf(V, rank, max_iter=35, W=W, H=H, update=update,
                    objective=objective, resetter=resetter)
    basis, coef, obj = nmf_inst.factorize()
    return basis, coef, obj