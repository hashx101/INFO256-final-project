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
from matplotlib.font_manager import FontProperties

# for 3d graph
from matplotlib import cm
from matplotlib.mlab import griddata


SAMPLES = 10
HEADERS = {'User-Agent': ['Twisted Web Client'],
           'Origin': ['http://localhost'],
           'Accept-Language': ['en-US','en'],
           'Content-Type': ['application/x-www-form-urlencoded'],
           'Accept': ['*/*'],
           'Referer': ['http://localhost/theme-finder/'],
           'X-Requested-With': ['XMLHttpRequest'],
           'Connection': ['keep-alive']}

def sendQuery(**kwargs):
    data = urllib.urlencode(kwargs)
    req = urllib2.Request('http://localhost/theme-finder/src/php/similarsentences/similarsentences.php', data)
    response = urllib2.urlopen(req)
    for line in response:
        try:
            return loads(line)
        except:
            print('Derped on {}'.format(line))


def sendStringQuery(string,
                    instance="shakespeare"):
    return sendQuery(query=string,
                     instance=instance,
                     string_query='true',
                     vector_query='false')



def sendVectorQuery(query={'relevant': [],
                           'irrelevant': [],
                           'features': []},
                    vector_function='rocchio',
                    instance="shakespeare",
                    relevant=[],
                    irrelevant=[],
                    alpha=1,
                    beta=.75):

    return sendQuery(query=query,
                     vector_function=vector_function,
                     relevant=relevant,
                     irrelevant=irrelevant,
                     alpha=alpha,
                     beta=beta,
                     instance=instance,
                     string_query='false',
                     vector_query='true')

def sendFeatureQuery(instance="shakespeare", relevant=[], irrelevant=[]):
    return sendQuery(relevant=relevant,
                     irrelevant=irrelevant,
                     instance=instance,
                     string_query='false',
                     vector_query='true')

VEC_ADJ_FNS = ['rocchio', 'ide_dec', 'ide_regular']

def test(testset=ts.TEST_3):
    instance = testset['instance']
    relevant = testset['relevant']
    irrelevant = testset['irrelevant']


    percentages = util.step_range(.1, .5, .05)
    results = {}
    for percent in percentages:
        results[percent] = {}
        for fn in VEC_ADJ_FNS:
            results[percent][fn] = {'recalls': []}
        for sample_num in range(SAMPLES):
            print('Percent: {} Sample: {}'.format(percent, sample_num + 1))
            relevant_sample = util.percent_sample(relevant, percent)
            irrelevant_sample = irrelevant
            for fn in VEC_ADJ_FNS:
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
            
        for fn in VEC_ADJ_FNS:
            recalls = results[percent][fn]['recalls']
            results[percent][fn]['recall'] = sum(recalls) / len(recalls)


    results = {'results': results, 'testset': testset['name']}
    fname = "results_{}".format(datetime.datetime.now().strftime("%Y%m%d%H%m%S"))
    with open(fname, 'w') as f:
        pickle.dump(results, f)
    graph(fname)


def graph(fname):   
    with open(fname) as f:
        results = pickle.load(f)
        testset = results['testset']
        results = results['results']

        font_name='/home/alexm/.fonts/Myriad/MyriadPro-SemiCn.otf'
        tic_font = FontProperties(fname=font_name)
        legend_font = FontProperties(fname=font_name)
        title_font = FontProperties(fname=font_name, size='x-large')    

        mean = lambda vals: sum(vals) / len(vals)
        median = np.median              
        
        for fn in ['mean', 'median']:
            fig, ax = plt.subplots(1)
            ax.set_title(fn.capitalize())
            ax.title.set_fontproperties(title_font)

            for vec_fn in VEC_ADJ_FNS:
                x_axis = sorted(results.keys())
                y_axis = [eval(fn)(results[percent][vec_fn]['recalls']) for percent in x_axis]
                ppl.plot(ax, x_axis, y_axis, label=vec_fn, linewidth=2)

            for label in ax.get_xticklabels():
                label.set_fontproperties(tic_font)

            for label in ax.get_yticklabels():
                label.set_fontproperties(tic_font)

            ax.set_xlabel('Starting (%)')
            ax.set_ylabel('Recall (%)')

            # Shink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width, box.height * 0.9])

            # Put a legend below current axis
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
                      fancybox=True, shadow=True, ncol=5, prop=legend_font)

            fig.savefig('line_plot_{}_{}.png'.format(fn, testset))

        fig, ax = plt.subplots(1)
        ax.set_title('Recalls')
        ax.title.set_fontproperties(title_font)
        colors = {'rocchio': 'green',
                  'ide_dec': 'red',
                  'ide_regular': 'blue'}
        percents = sorted(results.keys())
        for vec_fn in VEC_ADJ_FNS:
                # intermediate variables are for plebs
                x, y = zip(*[item for sublist in [[(percent, val) for val in results[percent][vec_fn]['recalls']] for percent in percents] for item in sublist])
                ppl.scatter(ax, x, y, label=vec_fn, facecolor=colors[vec_fn], alpha=0.5)

        for label in ax.get_xticklabels():
            label.set_fontproperties(tic_font)

        for label in ax.get_yticklabels():
            label.set_fontproperties(tic_font)

        ax.set_xlabel('Starting (%)')
        ax.set_ylabel('Recall (%)')

        # Shink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                         box.width, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
                  fancybox=True, shadow=True, ncol=5, prop=legend_font)

        fig.savefig('scatter_plot_{}.png'.format(testset))

def test_rocchio(testset=ts.TEST_2):
    instance = testset['instance']
    relevant = testset['relevant']
    irrelevant = testset['irrelevant']

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
                for sample_num in range(SAMPLES):
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
    graph_rocchio(test_rocchio())
    #test()
    #graph('results_20131209011200')