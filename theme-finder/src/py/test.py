from __future__ import print_function


from pprint import pprint
from json import loads
import urllib2
import urllib
import random
import math
import copy
from collections import defaultdict
import prettyplotlib as ppl
import testsets as ts
import numpy

# prettyplotlib imports 
from prettyplotlib import plt
from prettyplotlib import mpl
from prettyplotlib import brewer2mpl
from matplotlib.font_manager import FontProperties


SAMPLES = 100
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


def sendStringQuery(string, instance="shakespeare"):
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
                    irrelevant=[]):
    print('Calling vector query')
    return sendQuery(query=query,
                     vector_function=vector_function,
                     relevant=relevant,
                     irrelevant=irrelevant,
                     instance=instance,
                     string_query='false',
                     vector_query='true')

def sendFeatureQuery(instance="shakespeare", relevant=[], irrelevant=[]):
    print('Calling feature query')
    return sendQuery(relevant=relevant,
                     irrelevant=irrelevant,
                     instance=instance,
                     string_query='false',
                     vector_query='true')

VEC_ADJ_FNS = ['rocchio', 'ide_dec', 'ide_regular']

def test(testset=ts.TEST_2):
    instance = testset['instance']
    relevant = testset['relevant']
    irrelevant = testset['irrelevant']
    percentages = map(lambda i: i * .1, range(1,5))
    results = [0] * len(percentages)
    for index, percent in enumerate(percentages):
        results[index] = {}
        for fn in VEC_ADJ_FNS:
            results[index][fn] = {'recalls': []}
        for _ in range(SAMPLES):
            # sample percent of subset for running fns against
            relevant_sample = random.sample(relevant, int(math.ceil(len(relevant) * percent)))
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


                results[index][fn]['recalls'].append(float(len(found_not_in_start))/len(to_find))
            
        for fn in VEC_ADJ_FNS:
            recalls = results[index][fn]['recalls']
            results[index][fn]['recall'] = float(sum(recalls))/len(recalls)

    pprint(results)

    y_list_mean = []
    y_list_median = []

    points = {'rocchio': {'x': [],
                          'y': []},
              'ide_dec': {'x': [],
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
    ax.set_title(fn.capitalize())
    ax.title.set_fontproperties(title_font)
    colors = {'rocchio': 'red',
              'ide_dec': 'blue',
              'ide_regular': 'green'}
    for fn, xy in points.iteritems():
        ppl.scatter(ax, xy['x'], xy['y'], label=fn, facecolor=colors[fn])

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
    test()