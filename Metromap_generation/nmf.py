from scipy.sparse import csr_matrix, isspmatrix
import numpy as np
from Metromap_generation.MatrixUtils import dot
import math
import sys
__all__ = ['Nmf']


class Nmf:
    def __init__(self, V, rank, resetter, W=None, H=None, max_iter=30,
                 min_residuals=1e-5, update='log_update', objective='log_obj'):
        self.name = "nmf"
        self.resetter = resetter
        self.__dict__.update(vars())
        self.row_sumH = None
        self.update = getattr(self, self.update)
        self.objective = getattr(self, self.objective)
        self.reformat_matrices()

    def factorize(self):
        self.lil_V = self.V.tolil()
        self.lil_VT = self.V.T.tolil()
        self.W = csr_matrix(self.W)
        if self.H is not None:
            self.H = csr_matrix(self.H)
        self.tau = 0.8
        self.worse_obj_flag = False
        expected_initial_row_sum = list(self.W.shape)[0] / 2 #when chosen randomly the row_sum tends to be half of the number of rows
        self.step_size = 1 / 10**len(str(int(expected_initial_row_sum))) #we want a step_size where 1's in rows does not go below 0 in the first step (so if row_sum is in the 100's step size is 0.001, while 1000's => 0.0001)
        p_obj = c_obj = sys.float_info.max #p_obj is objective function value from previous iteration. c_obj is current
        iter = 0
        while self.is_satisfied(p_obj, c_obj, iter):
            self.current_W = self.W.copy()
            self.current_H = self.H.copy() if self.H is not None else None
            if self.worse_obj_flag:
                p_obj = self.W_prev
                c_obj = self.W_obj
                self.step_size = self.step_size * self.tau
                self.W = self.current_W
                self.H = self.current_H
                self.worse_obj_flag = False
                print('step_size: ' + str(self.step_size))
            else: #Her gemmes data for at kunne rewinde, hvis obj er worse!!!!
                self.W_prev = p_obj
                self.W_obj = c_obj

            self.row_sumW = self.W.sum(axis=0)
            if self.H is not None:
                self.row_sumH = self.H.sum(axis=0)
            # if not set test_conv is None (it can be an int that determines number of iterations beteen each convergence test)
            p_obj = c_obj
            self.update() #Call update function in this script that updates H and W (fx. eucledian())
            iter += 1
            c_obj = self.objective() #Call objective function in this script which we want to MINIMIZE (fx. fro())
        # if multiple runs are performed, fitted factorization model with
        # the lowest objective function value is retained
        if self.worse_obj_flag == True:
            self.W = self.current_W
        self.n_iter = iter
        self.final_obj = c_obj
        #mffit = mf_fit.Mf_fit(copy.deepcopy(self))

        return self.W, self.H, c_obj

    def is_satisfied(self, p_obj, c_obj, iter):
        print('iteration: ' + str(iter))
        if self.max_iter and self.max_iter <= iter:
            return False
        if self.min_residuals and iter > 0 and p_obj - c_obj < self.min_residuals:
            if iter > 5:
                self.worse_obj_flag = True
            return True
        if iter > 0 and c_obj > p_obj: #Denne sørger for at objective function altid falder eller også stopper algoritmen
            self.worse_obj_flag = True
            return True #used to return false
        if self.step_size < 0.0005:
            return False
        return True

    def log_update(self):
        print('hat?')
        num_terms, rank = self.W.shape
        #newW = csr_matrix(self.W.shape)
        highest_mult_val = 1 #default if divide by zero comes up in beginning
        for u in range(0, num_terms):
            term1 = 0
            neighbours = self.lil_V.rows[u]
            neighbour_sum = 0
            for neighbour in neighbours:
                neighbour_sum += self.W[neighbour, :]
                numerator = np.exp(-dot(self.W[u, :], self.W[neighbour, :].T).toarray())[0]
                #print('numerator: ' + str(numerator))
                mult_val, highest_mult_val = self.find_multiplier(numerator, highest_mult_val)
                term1 += self.W[neighbour,:].multiply(mult_val)

            term2 = self.row_sumW - self.W[u, :] - neighbour_sum
            if not isspmatrix(term1): #if u has no neighbours basically
                gradient = term2
            else:
                gradient = -(term1.toarray() - term2) #minus gradient fordi vi MINIMIZER et maximization problem :b
            old_roW = self.W[u, :].toarray()
            debug_updated_row = self.W[u,:].toarray() - self.step_size*gradient.A1
            updated_row = csr_matrix(np.maximum(self.resetter, (self.W[u,:].toarray() - self.step_size*gradient)))
            self.row_sumW = term2 + updated_row + neighbour_sum
            self.W[u, :] = updated_row
            if u == 143:
                print(updated_row.data)
            #print('finished node: ' + str(u))


    def find_multiplier(self, numerator, highest_mult_val):
        if numerator[0] == 1.0:  # Then there is a divide by zero situation that is solved by making multiplier highest one yet
            mult_val = highest_mult_val
            if highest_mult_val > 1.0:
                mult_val = 1.0
        else:
            mult_val = numerator / (1 - numerator)
        if mult_val > highest_mult_val:
            highest_mult_val = mult_val
        return mult_val, highest_mult_val

    def log_update_2_mat(self):
        self.W, self.row_sumH = self.update_matrix(self.W, self.H, self.row_sumH, self.lil_V)
        #lil_V before transposed was N x C, where N=num_terms and C=num_clusters
        self.H, self.row_sumW = self.update_matrix(self.H, self.W, self.row_sumW, self.lil_VT)

    def update_matrix(self, M, fixed, row_sum, lil_V):
        print('update')
        highest_mult_val = 1 #default if divide by zero comes up in beginning
        for u in range(0, M.shape[0]):
            term1 = 0
            neighbours = lil_V.rows[u] #These neighbours are always referring to those in fixed
            neighbour_sum = 0
            for neighbour in neighbours:
                neighbour_sum += fixed[neighbour, :]
                numerator = np.exp(-dot(M[u, :], fixed[neighbour, :].T).toarray())[0]
                #print('numerator: ' + str(numerator))
                mult_val, highest_mult_val = self.find_multiplier(numerator, highest_mult_val)
                term1 += fixed[neighbour,:].multiply(mult_val)

            term2 = row_sum - M[u, :] - neighbour_sum
            if not isspmatrix(term1): #if u has no neighbours basically
                gradient = term2
            else:
                gradient = -(term1.toarray() - term2) #minus gradient fordi vi MINIMIZER et maximization problem :b
            old_roW = M[u, :].toarray()
            debug_updated_row = M[u,:].toarray() - self.step_size*gradient.A1
            updated_row = csr_matrix(np.maximum(self.resetter, (M[u,:].toarray() - self.step_size*gradient)))
            row_sum = term2 + updated_row + neighbour_sum
            M[u, :] = updated_row
            if u == 143:
                print(updated_row.data)
            #print('finished node: ' + str(u))
        return M, row_sum

    def log_obj(self):
        Aterm1 = 0
        Asum_dot_product = 0
        print('obj')
        overall_obj = 0
        num_terms, rank = self.W.shape
        lowest_log_val = math.log(0.1)
        for u in range(0, num_terms):
            #print('node u: ' + str(u))
            term1 = 0
            neighbours = self.lil_V.rows[u]
            neighbour_sum = 0
            for neighbour in neighbours:
                neighbour_sum += self.W[neighbour, :]
                before_expon = -dot(self.W[u, :], self.W[neighbour, :].T).toarray()
                expon = np.exp(-dot(self.W[u, :], self.W[neighbour, :].T).toarray())[0]
                # log by zero situation is solved by logresult the lowest one yet
                result, lowest_log_val = self.log_by_zero_solver(expon, lowest_log_val)
                term1 += result

            sum_non_neighbours = self.row_sumW - self.W[u, :] - neighbour_sum
            sum_dot_product = self.W[u, :].dot(sum_non_neighbours.T).A1[0]
            Aterm1 += term1
            Asum_dot_product += sum_dot_product
            objective = -(term1 - sum_dot_product) #minus gradient fordi vi MINIMIZER et maximization problem :b
            overall_obj += objective
            #print('objective is: ' + str(objective))
        print('overall_objective is: ' + str(overall_obj))
        return overall_obj

    def log_by_zero_solver(self, expon, lowest_log_val):
        if expon[0] == 1.0:
            # print(str(lowest_log_val))
            result = lowest_log_val
        else:
            result = math.log(1 - expon)
            # print(result)
        if result < lowest_log_val:
            lowest_log_val = result
        return result, lowest_log_val

    def log_obj_2_mat(self):
        print('hatobj?')
        overall_obj = 0
        num_terms, rank = self.W.shape
        lowest_log_val = math.log(0.1)
        for u in range(0, num_terms):
            #print('node u: ' + str(u))
            term1 = 0
            neighbours = self.lil_V.rows[u]
            neighbour_sumH = 0
            for neighbour in neighbours:
                neighbour_sumH += self.H[neighbour, :]
                before_expon = -dot(self.W[u, :], self.H[neighbour, :].T).toarray()
                expon = np.exp(-dot(self.W[u, :], self.H[neighbour, :].T).toarray())[0]
                # log by zero situation is solved by logresult the lowest one yet
                result, lowest_log_val = self.log_by_zero_solver(expon, lowest_log_val)
                term1 += result

            sum_non_neighboursH = self.row_sumH - self.W[u, :] - neighbour_sumH
            sum_dot_product = self.W[u, :].dot(sum_non_neighboursH.T).A1[0]
            objective = -(term1 - sum_dot_product) #minus gradient fordi vi MINIMIZER et maximization problem :b
            overall_obj += objective
            #print('objective is: ' + str(objective))
        print('overall_objective is: ' + str(overall_obj))
        return overall_obj

    def __str__(self):
        return '%s - update: %s obj: %s' % (self.name, self.update.__name__, self.objective.__name__)

    def reformat_matrices(self):
        if isspmatrix(self.V):
            self.V = self.V.tocsr().astype('d')
        else:
            self.V = np.asmatrix(self.V) if self.V.dtype == np.dtype(
                float) else np.asmatrix(self.V, dtype='d')
        if isspmatrix(self.W):
            self.W = self.W.tocsr().astype('d')
        else:
            self.W = np.asmatrix(self.W) if self.W.dtype == np.dtype(
                float) else np.asmatrix(self.W, dtype='d')
        if self.H is not None:
            if isspmatrix(self.H):
                self.H = self.H.tocsr().astype('d')
            else:
                self.H = np.asmatrix(self.H) if self.H.dtype == np.dtype(
                    float) else np.asmatrix(self.H, dtype='d')