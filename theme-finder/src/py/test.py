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

# Constants
DEF_SAMPLES = 10
DEF_START = .05
DEF_END = .7
DEF_STEP = .05
DEF_INSTANCE = 'shakespeare'
DEF_VEC_FN = 'rocchio'
DEF_ALPHA = 1.0
DEF_BETA = 0.75
VEC_ADJ_FNS = ['rocchio', 'ide_dec', 'ide_regular']
VEC_ADJ_FNS_PSEUDO = ['rocchio', 'ide_dec', 'ide_regular', 'pseudo']
COLORS = {'rocchio': 'red',
          'ide_dec': 'blue',
          'ide_regular': 'green',
          'pseudo': 'magenta'}


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
    vector_query -- the previous vector query object
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
    A convenience function to make vector adjustment queries to the server

    Keyword arguments:
    instance -- name of database instance to query (default 'shakespeare')
    relevant -- a list of integers corresponding to relevant sentence ids
    irrrelevant -- a list of integers corresponding to irrelevant sentence ids
    vector_function -- the name of a vector adjustment function (default 'rocchio')
    alpha -- a float with which to weight the old query by during the vector
             adjustment (defualt 1.0)
    beta -- (rocchio only) a float with which to weight the new relevant
            sentences by during vector adjustment (default 0.75)
    query -- the previous vector query object
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


def test(test_set=ts.TEST_2, test_fns=VEC_ADJ_FNS, samples=DEF_SAMPLES,
         start=DEF_START, end=DEF_END, step=DEF_STEP, seed=random.random()):
    """
    Given a test set and a list of vector functions, checks recall rates
    over varried starting percentages of the test set.

    Keyword arguments:
    test_set -- a dictionary containing the 'name' of the set, the database
                'instance', the 'search_term' to use (only 'pseudo'), a list
                of 'relevant' sentence ids, and a list of 'irrelevant'
                sentence ids
    test_fns -- a list of names of vector adjustment functions to use
    samples -- the number of samples to run (default 3)
    start -- a float corresponding to the starting sample percentage (default 0.05)
    end -- a float corresponding to the ending sample percentage (default 0.6)
    step -- a float corresponding to the sample percentage to step by (default 0.05)
    seed -- the random seed to use
    """
    random.seed(seed)

    # load information from the test set
    test_set_name = test_set['name']
    instance = test_set['instance']
    relevant = test_set['relevant']
    irrelevant = test_set['irrelevant']
    search_term = test_set['search_term']

    results = {}
    for percent in util.step_range(start, end, step):
        # instantiate dictionaries
        results[percent] = {}
        for fn in test_fns:
            results[percent][fn] = {'recalls': []}

        for sample_num in range(samples):
            print('Percent: {} Sample: {}'.format(percent, sample_num + 1))

            # take a random percentage of the relevant sentence ids
            relevant_sample = util.percent_sample(relevant, percent)
            # currently we take all irrelevant sentence ids, so this isn't a sampling
            irrelevant_sample = irrelevant

            for fn in test_fns:
                response = sendVectorQuery(vector_function=fn,
                                           relevant=relevant_sample,
                                           irrelevant=irrelevant_sample,
                                           instance=instance)

                # find which sentences were recalled
                relevant_returned = copy.copy(relevant_sample)
                relevent_set = set(relevant)
                relevant_sample_set = set(relevant_sample)
                for sentence in response['sentences']:
                    sentence_id = int(sentence['id'])
                    if sentence_id in relevant and sentence_id not in relevant_returned:
                        relevant_returned.append(sentence_id)
                to_find = relevent_set.difference(relevant_sample_set)
                found = set(relevant_returned).difference(relevant_sample_set)

                # kludgy fix for when user gives percentage range to 100
                results[percent][fn]['recalls'].append(len(found) / max(.0000001, len(to_find)))

    results = {'results': results,
               'test_set': test_set_name,
               'vector_functions': test_fns,
               'start_percentage': start,
               'end_percentage': end,
               'step_percentage': step,
               'seed': seed}

    # save file and graph
    fname = "results_name_{}".format(datetime.datetime.now().strftime("%Y%m%d_%H%m%S"))
    with open(fname, 'w') as f:
        pickle.dump(results, f)
    graph(fname)


FN_TUPLES = zip(['mean', 'median', 'std'], [np.mean, np.median, np.std])

def graph(fname, analysis_fns = FN_TUPLES):   
    """
    Graphs mean and median of vector functions over a given starting
    percentage of relevant sentence ids.

    Arguments:
    fname -- the filename of the pickled output
    analysis_fns -- a list of (fn_name, fn) to run over the data
    """
    with open(fname) as f:
        results = pickle.load(f)
        test_set = results['test_set']
        vector_functions = results['vector_functions']
        step_percentage = results['step_percentage']
        results = results['results']  
        percents = sorted(results.keys())

        
        for fn_name, fn in analysis_fns:
            fig, ax = plt.subplots(1)
            ax.set_title(fn_name.capitalize())
            for vec_fn in vector_functions:
                xs = sorted(results.keys())
                x_axis = [x * 100 for x in xs]
                y_axis = [fn(results[percent][vec_fn]['recalls']) * 100 for percent in xs]
                ppl.plot(ax, x_axis, y_axis, label=vec_fn, linewidth=2, color=COLORS[vec_fn])

            ax.set_xticks([i * 100 for i in percents])
            ax.set_xlim([percents[0]*100, percents[-1]*100])

            ax.set_xlabel('Starting (%)')
            ax.set_ylabel('Recall (%)')
            if fn_name == 'std':
                ax.set_ylabel('Std')

            # shink current axis's height by 10% on the bottom for legend
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width, box.height * 0.9])

            # put a legend below current axis
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
                      fancybox=True, shadow=True, ncol=5)

            fig.savefig('line_plot_{}_{}.png'.format(fn_name, test_set))

        fig, ax = plt.subplots(1)
        ax.set_title('Recalls')

        # jitter to see all series
        current = -(len(vector_functions) / 2)
        step = 1
        for vec_fn in vector_functions:
                # intermediate variables are for plebs
                x, y = zip(*[item for sublist in [[((percent*100)+current, val*100) for val in results[percent][vec_fn]['recalls']] for percent in percents] for item in sublist])
                current += step
                ppl.scatter(ax, x, y, label=vec_fn, facecolor=COLORS[vec_fn], alpha=0.3)

        # set x ticks and limit ranges
        ax.set_xticks([i * 100 for i in percents])
        ax.set_xlim([(percents[0] - step_percentage) * 100, (percents[-1] + step_percentage) * 100])
        ax.set_ylim([-5,100])

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
    fname = 'results_rocchio_{}'.format(datetime.datetime.now().strftime("%Y%m%d_%H%m%S"))
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
    pass
