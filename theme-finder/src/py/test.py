from __future__ import print_function
from __future__ import division


from pprint import pprint
from json import loads
import urllib2
import urllib
import util
import random
import math
import copy
from collections import defaultdict
import prettyplotlib as ppl
import testsets as ts
import numpy as np
import datetime

# prettyplotlib imports 
from prettyplotlib import plt
from prettyplotlib import mpl
from prettyplotlib import brewer2mpl
from matplotlib.font_manager import FontProperties
import random
import pickle

# for 3d graph
from mpl_toolkits.mplot3d import Axes3D
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
                    alpha_plus=.75,
                    alpha_minus=.25):

    return sendQuery(query=query,
                     vector_function=vector_function,
                     relevant=relevant,
                     irrelevant=irrelevant,
                     alpha_plus=alpha_plus,
                     alpha_minus=alpha_minus,
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
    percentages = map(lambda i: i * .02, range(1,35))
    results = [0] * len(percentages)
    for index, percent in enumerate(percentages):
        print('Percentage: {}'.format(percent * 100))
        results[index] = {}
        for fn in VEC_ADJ_FNS:
            results[index][fn] = {'recalls': []}
        for sample_num in range(SAMPLES):
            print('Sample: {}'.format(sample_num + 1))
            # sample percent of subset for running fns against
            relevant_sample = random.sample(relevant,
                                            max(1,
                                                min(int(math.floor(len(relevant) * percent)),
                                                    len(relevant))))
            irrelevant_sample = irrelevant
            for fn in VEC_ADJ_FNS:
                response = sendVectorQuery(vector_function=fn,
                                           relevant=relevant_sample,
                                           irrelevant=irrelevant_sample,
                                           instance=instance)
                relevant_start = copy.copy(relevant_sample)
                for sentence in response['sentences']:
                    sentence_id = int(sentence['id'])
                    if sentence_id in relevant and sentence_id not in relevant_start:
                        relevant_start.append(sentence_id)
                to_find = set(relevant).difference(set(relevant_sample))
                found_not_in_start = set(relevant_start).difference(relevant_sample)


                results[index][fn]['recalls'].append(float(len(found_not_in_start))/max(.0000001, len(to_find)))
            
        for fn in VEC_ADJ_FNS:
            recalls = results[index][fn]['recalls']
            results[index][fn]['recall'] = float(sum(recalls))/len(recalls)


    pprint(results)
    results = {'results': results, 'percentages': percentages}
    with open('results', 'w') as f:
        pickle.dump(results, f)
    graph(results)

def test_rocchio(testset=ts.TEST_3):
    instance = testset['instance']
    relevant = testset['relevant']
    irrelevant = testset['irrelevant']

    percentages = util.step_range(.1,.4,.1)
    results = dict()

    for percent in percentages:
        results[percent] = {}
        
        alpha_pluses = util.step_range(0, 1, .25)
        alpha_minuses = util.step_range(0, 1, .25)
        for alpha_plus in alpha_pluses:
            results[percent][alpha_plus] = {}

            for alpha_minus in alpha_minuses:
                print("Percentage: {} Alpha+: {} Alpha-: {}".format(percent, alpha_plus, alpha_minus))
                results[percent][alpha_plus][alpha_minus] = {'recalls': []}
                for sample_num in range(SAMPLES):
                    relevant_sample = util.percent_sample(relevant, percent)
                    irrelevant_sample = irrelevant

                    response = sendVectorQuery(vector_function='rocchio',
                                               relevant=relevant_sample,
                                               irrelevant=irrelevant_sample,
                                               instance=instance,
                                               alpha_plus=alpha_plus,
                                               alpha_minus=alpha_minus)

                    relevant_returned = copy.copy(relevant_sample)
                    relevent_set = set(relevant)
                    relevant_sample_set = set(relevant_sample)
                    for sentence in response['sentences']:
                        sentence_id = int(sentence['id'])
                        if sentence_id in relevant and sentence_id not in relevant_returned:
                            relevant_returned.append(sentence_id)
                    to_find = relevent_set.difference(relevant_sample_set)
                    found = set(relevant_returned).difference(relevant_sample_set)

                    results[percent][alpha_plus][alpha_minus]['recalls'].append(len(found) / max(.0000001, len(to_find)))
    fname = 'results_rocchio_{}'.format(datetime.datetime.now().strftime("%Y%m%d%H%m%S"))
    with open(fname, 'w') as f:
        pickle.dump(results, f)
    return fname


def graph_rocchio(fname):
    with open(fname) as f:
        results = pickle.load(f)
        percent = .1
        x = []
        y = []
        z = []
        for alpha_pl in results[percent]:
            for alpha_mi in results[percent][alpha_pl]:
                x.append(alpha_pl)
                y.append(alpha_mi)
                recalls = results[percent][alpha_pl][alpha_mi]['recalls']
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

    ax.set_xlabel('alpha+')
    ax.set_ylabel('alpha-')
    ax.set_zlabel('recall')

    plt.show()

def graph(res_dict):    
    results = res_dict['results']
    percentages = res_dict['percentages']
    y_list_mean = []
    y_list_median = []

    points = {'rocchio':     {'x': [],
                              'y': []},
              'ide_dec':     {'x': [],
                              'y': []},
              'ide_regular': {'x': [],
                              'y': []}}

    label_list = []
    for fn in VEC_ADJ_FNS:
        mean_list = []
        median_list = []
        points_list = []
        for index in range(len(percentages)):
            mean_list.append(results[index][fn]['recall'])
            median_list.append(numpy.median(results[index][fn]['recalls']))

            points[fn]['x'].extend([percentages[index]] * SAMPLES)
            points[fn]['y'].extend(results[index][fn]['recalls'])


        y_list_mean.append(tuple(mean_list))
        y_list_median.append(tuple(median_list))

        label_list.append(fn)
    x_list = [percentages] * len(y_list_mean)

    fname='/home/alexm/.fonts/Myriad/MyriadPro-SemiCn.otf'
    tic_font = FontProperties(fname=fname)
    legend_font = FontProperties(fname=fname)
    title_font = FontProperties(fname=fname, size='x-large')
    for fn in ['mean', 'median']:
        fig, ax = plt.subplots(1)
        ax.set_title(fn.capitalize())
        ax.title.set_fontproperties(title_font)
        for x, y, label in zip(x_list, eval('y_list_'+fn), label_list):
            ppl.plot(ax, x, y, label=label, linewidth=2)

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

        fig.savefig('line_plot_{}_{}_samples.png'.format(fn, SAMPLES))

    fig, ax = plt.subplots(1)
    ax.set_title('Recalls')
    ax.title.set_fontproperties(title_font)
    colors = {'rocchio': 'green',
              'ide_dec': 'red',
              'ide_regular': 'blue'}
    for fn, xy in points.iteritems():
        jitter = .05
        xs = [x + random.uniform(-jitter, jitter) for x in xy['x']]
        ppl.scatter(ax, xy['x'], xy['y'], label=fn, facecolor=colors[fn], alpha=0.5)

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

    fig.savefig('scatter_plot_{}_samples.png'.format(SAMPLES))



if __name__ == "__main__":
    #sendStringQuery("test")
    #print(sendQuery(vector_query='true', instance='shakespeare', relevant=[19498]))
    graph_rocchio(test_rocchio())
