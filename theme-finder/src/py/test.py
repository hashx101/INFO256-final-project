from __future__ import print_function
from __future__ import division

from json import loads
import urllib2
import urllib
import util
import random
import copy
import prettyplotlib as ppl
import testsets as ts
import numpy as np
import datetime
import pickle

# prettyplotlib imports 
from prettyplotlib import plt
from prettyplotlib import mpl
from prettyplotlib import brewer2mpl

# for 3d graph
from matplotlib import cm
from matplotlib.mlab import griddata

# headers for http queries
HEADERS = {'User-Agent': ['Twisted Web Client'],
           'Origin': ['http://localhost'],
           'Accept-Language': ['en-US','en'],
           'Content-Type': ['application/x-www-form-urlencoded'],
           'Accept': ['*/*'],
           'Referer': ['http://localhost/theme-finder/'],
           'X-Requested-With': ['XMLHttpRequest'],
           'Connection': ['keep-alive']}

# defaults for functions, graphing as well
DEF_SAMPLES = 3
DEF_INSTANCE = 'shakespeare'
DEF_VEC_FN = 'rocchio'
DEF_ALPHA = 1.0
DEF_BETA = 0.75

VEC_ADJ_FNS = ['rocchio', 'ide_dec', 'ide_regular']
VEC_ADJ_FNS_PSEUDO = ['rocchio', 'ide_dec', 'ide_regular', 'pseudo']
COLORS = {'rocchio': 'red',
          'ide_dec': 'blue',
          'ide_regular': 'green',
          'pseudo': 'purple'}

def sendQuery(**kwargs):
    """
    Sends a query to similarsentences.php with the given keyword arguments.
    Expects JSON, but will handle invalid lines, returning a python dictionary
    created from the first line of valid JSON.
    """
    data = urllib.urlencode(kwargs)
    req = urllib2.Request('http://localhost/theme-finder/src/php/similarsentences/similarsentences.php', data)
    response = urllib2.urlopen(req)
    for line in response:
        try:
            return loads(line)
        except:
            print('Derped on {}'.format(line))


def sendStringQuery(query,
                    vector_query={'relevant':    [],
                                   'irrelevant': [],
                                   'features':   []},
                    instance=DEF_INSTANCE):
    """
    A convenience function to make string queries to the server. Takes a
    string, query.

    Keyword arguments:
    instance -- name of database instance to query (default 'shakespeare')
    vector_query -- a vector query object
    """
    return sendQuery(instance=instance,
                     string_query='true',
                     vector_query=vector_query,
                     query=query)

def sendVectorQuery(instance=DEF_INSTANCE,
                    relevant=[],
                    irrelevant=[],
                    vector_function=DEF_VEC_FN,
                    alpha=DEF_ALPHA,
                    beta=DEF_BETA,
                    query={'relevant':   [],
                           'irrelevant': [],
                           'features':   []}):
    """
    A convenience function to make vector adjustment queryies to the server


    given a database instance name to query ('shakespeare' or 'personals'),
    a list of relevant sentence ids, a list of irrelevant sentence ids, a
    vector adjustment function name ('rocchio', 'ide_dec', 'ide_regular', or
    'pseudo'), alpha, a float
    """

    return sendQuery(instance=instance,
                     string_query='false',
                     vector_query='true',
                     relevant=relevant,
                     irrelevant=irrelevant,
                     vector_function=vector_function,
                     alpha=alpha,
                     beta=beta,
                     query=query)

def sendFeatureQuery(instance="shakespeare", relevant=[], irrelevant=[]):
    return sendQuery(relevant=relevant,
                     irrelevant=irrelevant,
                     instance=instance,
                     string_query='false',
                     vector_query='true')

def test(test_set=ts.TEST_2, test_fns=VEC_ADJ_FNS, samples=DEF_SAMPLES):
    instance = test_set['instance']
    relevant = test_set['relevant']
    irrelevant = test_set['irrelevant']
    search_term = test_set['search_term']


    percentages = util.step_range(.1, .5, .05)
    results = {}
    for percent in percentages:
        results[percent] = {}
        for fn in test_fns:
            results[percent][fn] = {'recalls': []}
        for sample_num in range(samples):
            print('Percent: {} Sample: {}'.format(percent, sample_num + 1))
            relevant_sample = util.percent_sample(relevant, percent)
            irrelevant_sample = irrelevant
            for fn in test_fns:
                if fn == 'pseudo':
                    pseudo_query = sendStringQuery(query=search_term,
                                                   instance=instance)['query']
                    response = sendVectorQuery(vector_function=fn,
                                               query=pseudo_query,
                                               instance=instance)
                else:
                    response = sendVectorQuery(vector_function=fn,
                                               relevant=relevant_sample,
                                               irrelevant=irrelevant_sample,
                                               instance=instance)

                relevant_returned = copy.copy(relevant_sample)
                relevent_set = set(relevant)
                relevant_sample_set = set(relevant_sample)
                for sentence in response['sentences']:
                    sentence_id = int(sentence['id'])
                    if sentence_id in relevant and sentence_id not in relevant_returned:
                        relevant_returned.append(sentence_id)
                to_find = relevent_set.difference(relevant_sample_set)
                found = set(relevant_returned).difference(relevant_sample_set)


                results[percent][fn]['recalls'].append(len(found) / max(.0000001, len(to_find)))
            
        for fn in test_fns:
            recalls = results[percent][fn]['recalls']
            results[percent][fn]['recall'] = sum(recalls) / len(recalls)


    results = {'results': results, 'test_set': test_set['name']}
    fname = "results_{}".format(datetime.datetime.now().strftime("%Y%m%d%H%m%S"))
    with open(fname, 'w') as f:
        pickle.dump(results, f)
    graph(fname, test_fns)


def graph(fname, fns):   
    with open(fname) as f:
        results = pickle.load(f)
        test_set = results['test_set']
        results = results['results']  

        mean = lambda vals: sum(vals) / len(vals)
        median = np.median              
        
        for fn in ['mean', 'median']:
            fig, ax = plt.subplots(1)
            ax.set_title(fn.capitalize())
            for vec_fn in fns:
                x_axis = sorted(results.keys())
                y_axis = [eval(fn)(results[percent][vec_fn]['recalls']) for percent in x_axis]
                ppl.plot(ax, x_axis, y_axis, label=vec_fn, linewidth=2)

            ax.set_xlabel('Starting (%)')
            ax.set_ylabel('Recall (%)')

            # Shink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width, box.height * 0.9])

            # Put a legend below current axis
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
                      fancybox=True, shadow=True, ncol=5)

            fig.savefig('line_plot_{}_{}.png'.format(fn, test_set))

        fig, ax = plt.subplots(1)
        ax.set_title('Recalls')
        percents = sorted(results.keys())
        for vec_fn in fns:
                # intermediate variables are for plebs
                x, y = zip(*[item for sublist in [[(percent, val) for val in results[percent][vec_fn]['recalls']] for percent in percents] for item in sublist])
                ppl.scatter(ax, x, y, label=vec_fn, facecolor=COLORS[vec_fn], alpha=0.5)

        ax.set_xlabel('Starting (%)')
        ax.set_ylabel('Recall (%)')

        # Shink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                         box.width, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
                  fancybox=True, shadow=True, ncol=5)

        fig.savefig('scatter_plot_{}.png'.format(test_set))

def test_rocchio(test_set=ts.TEST_2, samples=DEF_SAMPLES):
    instance = test_set['instance']
    relevant = test_set['relevant']
    irrelevant = test_set['irrelevant']

    percentages = util.step_range(.1,.4,.1)
    results = dict()

    for percent in percentages:
        results[percent] = {}
        
        alphas = util.step_range(0, 1, .1)
        betas = util.step_range(0, 1, .1)
        for alpha in alphas:
            results[percent][alpha] = {}

            for beta in betas:
                print("Percentage: {} Alpha: {} Beta: {}".format(percent, alpha, beta))
                results[percent][alpha][beta] = {'recalls': []}
                for sample_num in range(samples):
                    relevant_sample = util.percent_sample(relevant, percent)
                    irrelevant_sample = irrelevant

                    response = sendVectorQuery(vector_function='rocchio',
                                               relevant=relevant_sample,
                                               irrelevant=irrelevant_sample,
                                               instance=instance,
                                               alpha=alpha,
                                               beta=beta)

                    relevant_returned = copy.copy(relevant_sample)
                    relevent_set = set(relevant)
                    relevant_sample_set = set(relevant_sample)
                    for sentence in response['sentences']:
                        sentence_id = int(sentence['id'])
                        if sentence_id in relevant and sentence_id not in relevant_returned:
                            relevant_returned.append(sentence_id)
                    to_find = relevent_set.difference(relevant_sample_set)
                    found = set(relevant_returned).difference(relevant_sample_set)

                    results[percent][alpha][beta]['recalls'].append(len(found) / max(.0000001, len(to_find)))
    fname = 'results_rocchio_{}'.format(datetime.datetime.now().strftime("%Y%m%d%H%m%S"))
    with open(fname, 'w') as f:
        pickle.dump(results, f)
    return fname


def graph_rocchio(fname):
    with open(fname) as f:
        results = pickle.load(f)
        for percent in results.keys():
            x = []
            y = []
            z = []
            for alpha in results[percent]:
                for beta in results[percent][alpha]:
                    x.append(alpha)
                    y.append(beta)
                    recalls = results[percent][alpha][beta]['recalls']
                    z.append(sum(recalls) / len(recalls))

            fig = plt.figure()
            ax = fig.gca(projection='3d')
            xi = np.linspace(min(x), max(x))
            yi = np.linspace(min(y), max(y))
            X, Y = np.meshgrid(xi, yi)
            Z = griddata(x, y, z, xi, yi)

            surf = ax.plot_surface(X, Y, Z, rstride=5, cstride=5, cmap=cm.jet,
                                   linewidth=1, antialiased=True)
            ax.set_zlim3d(np.min(Z), np.max(Z))
            fig.colorbar(surf)

            ax.set_xlabel('alpha')
            ax.set_ylabel('beta')
            ax.set_zlabel('recall')

            plt.show()



if __name__ == "__main__":
    #sendStringQuery("test")
    #print(sendQuery(vector_query='true', instance='shakespeare', relevant=[19498]))
    #graph_rocchio(test_rocchio())
    #test()
    test(test_fns=VEC_ADJ_FNS_PSEUDO)
    #graph('results_20131209011200')