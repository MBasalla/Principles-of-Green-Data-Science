import numpy as np
import scipy.sparse as sp
import random
import datetime
import pandas as pd
from pandas import DataFrame as df
import os.path


def run_sparse_tests(matrix1, matrix2,debug=False):
    matrix2_t = matrix2.transpose()

    start = datetime.datetime.now()
    matrix1.dot(matrix2_t)
    end = datetime.datetime.now()
    s_dot = (end - start).total_seconds()
    if debug: print("sparse dot product took %f seconds" % s_dot)
    data = df([s_dot], columns=["dot"])

    return data


def run_full_test(matrix1, matrix2,debug = False):
    matrix2_t = matrix2.transpose()

    start = datetime.datetime.now()
    np.dot(matrix1, matrix2_t)
    end = datetime.datetime.now()
    r_dot = (end - start).total_seconds()
    if debug: print("regular dot product took %f seconds" % r_dot)
    data =df([r_dot], columns=["dot"])

    return data


def run_experiments(formats, dimensions, densities, n_experiments, outpath, override=True):
    if ".csv" not in outpath:
        outpath += ".csv"
    if not override and os.path.isfile(outpath):
        data = pd.read_csv(outpath).dropna()
    else:
        data = df()
    init_seed = 2
    investigated = set()
    if not override and not data.empty:
        for element in data["format"].drop_duplicates():
            investigated.add(element)
        for element in data["n_cols"].drop_duplicates():
            investigated.add(element)
        for element in data["density"].drop_duplicates():
            investigated.add(element)
    for m_type in formats:
        m_type_data = df()
        for x in dimensions:
            row_dim_data = df()
            for y in dimensions:
                col_dim_data= df()
                for d in densities:
                    density_data = df()
                    if override or not m_type in investigated or not x in investigated or not y in investigated or\
                            not d in investigated:
                        for i in range(n_experiments):
                            seed = init_seed + i
                            random.seed(seed)
                            matrix1 = sp.random(x, y, density=d).toarray()
                            matrix2 = sp.random(x, y, density=d).toarray()
                            if m_type == 'full':
                                inner_data = run_full_test(matrix1, matrix2)
                            else:
                                if m_type == 'csc':
                                    matrix1 = sp.csc_matrix(matrix1)
                                    matrix2 = sp.csc_matrix(matrix2)
                                elif m_type == 'csr':
                                    matrix1 = sp.csr_matrix(matrix1)
                                    matrix2 = sp.csr_matrix(matrix2)
                                elif m_type == 'bsr':
                                    matrix1 = sp.bsr_matrix(matrix1)
                                    matrix2 = sp.bsr_matrix(matrix2)
                                elif m_type == 'lil':
                                    matrix1 = sp.lil_matrix(matrix1)
                                    matrix2 = sp.lil_matrix(matrix2)
                                elif m_type == 'dok':
                                    matrix1 = sp.dok_matrix(matrix1)
                                    matrix2 = sp.dok_matrix(matrix2)
                                elif m_type == 'coo':
                                    matrix1 = sp.coo_matrix(matrix1)
                                    matrix2 = sp.coo_matrix(matrix2)
                                else:
                                    matrix1 = sp.dia_matrix(matrix1)
                                    matrix2 = sp.dia_matrix(matrix2)

                                inner_data = run_sparse_tests(matrix1, matrix2)
                            if density_data.empty:
                                density_data = inner_data
                            else:
                                density_data = density_data.append(inner_data, ignore_index=True)
                        density_data["density"] = d
                        if col_dim_data.empty:
                            col_dim_data = density_data
                        else:
                            col_dim_data = col_dim_data.append(density_data, ignore_index=True)
                        investigated.add(d)

                col_dim_data["n_cols"] = y
                if row_dim_data.empty:
                    row_dim_data = col_dim_data
                else:
                    row_dim_data = row_dim_data.append(col_dim_data,ignore_index=True)
                investigated.add(y)

            row_dim_data["n_rows"] = x
            if m_type_data.empty:
                m_type_data = row_dim_data
            else:
                m_type_data = m_type_data.append(row_dim_data,ignore_index=True)
            investigated.add(x)

        m_type_data["format"] = m_type
        if data.empty:
            data = m_type_data
        else:
            data = data.append(m_type_data,ignore_index=True)
        data.to_csv(outpath, index=False)
        investigated.add(m_type)
        print("Finished Experiments for type %s" % m_type)

    return data

# experiments = run_experiments(["full","dia"],[10,100],[0.01,0.1,0.25,0.5],10,"test_experiment.csv", override=False)
# print(experiments.head())
# experiments = run_experiments(["csc","csr"],[10,100],[0.01,0.1,0.25,0.5],10,"test_experiment.csv", override=False)
# print(experiments.head())

#formats = ['full', 'csc', 'csr', 'bsr', 'lil', 'dok', 'coo', 'dia']
formats = ['full', 'csc']
n_experiments = 20
densities = []
dimensions = []
for i in range(1,14):
    dimensions.append(2 ** i)
    densities.append(1/(2 **i))

# experiments = run_experiments(["full","csc"],[10,100,1000],[0.01,0.1,0.25,0.5],10)
# experiments = run_experiments(formats, dimensions, densities, n_experiments,"experiment1.csv", override=False)
# experiments = run_experiments(formats, [2 ** 14], densities.append(1/(2 ** 14)), n_experiments,"experiment1.csv", override=False)
# experiments = run_experiments(["full"], dimensions, densities, n_experiments,"experiment3.csv")

new_exps = run_experiments(formats,[10,100,1000], [1,1/10,1/100,1/1000],100, "experiment_data.csv")