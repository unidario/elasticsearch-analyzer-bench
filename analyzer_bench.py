import requests
import click

number_exec = 1


def calculate_mean(lst):
    s = 0
    for item in lst:
        s += float(item)
    if len(lst) == 0:
        return None
    else:
        return s / float(len(lst))


def col_length(headline, content, dict_key=None):
    """
    calculate the max needed length for a output col by getting the headline, the content of the rows
    (different data types) and in ome cases a specific key
    :param headline: Column headline
    :param content: A list of column contents
    :param dict_key: Extract only a part of the columns
    :return: Maximum length of contents
    """
    length = len(headline)
    if type(content) == list:
        for x in content:
            if type(x) == str:
                if len(x) > length:
                    length = len(x)

    elif type(content) == dict:
        for key in content:
            if type(content[key]) == dict:
                if dict_key in content[key]:
                    if len(str(content[key][dict_key])) > length:
                        length = len(str(content[key][dict_key]))
                else:
                    x = key
                    for key in content[x]:
                        if type(content[x][key]) == dict:
                            if dict_key in content[x][key]:
                                if type(content[x][key]) == dict:
                                    if len(content[x][key][dict_key]) > length:
                                        length = len(content[x][key][dict_key])
            elif type(content[key]) == int or type(content[key]) == float:
                if len(str(content[key])) > length:
                    length = len(str(content[key]))

    elif type(content) == int:
        if len(str(content)) > length:
            length = len(str(content))

    return length


def check_if_index_exists(url):
    response = requests.get(url)
    if response.status_code == 200:
        return True
    else:
        return False


def fetch_analyzer(url, index):
    analyzers = {}
    analyser_resp = requests.get(url + '/_settings')
    analyser_json = analyser_resp.json()
    data = analyser_json[index]['settings']['index']
    # if an analyzer exists, fetch analyzer components from response
    if 'analysis' in data:
        data = data['analysis']['analyzer']
        # in case there is more than one analyzer fetch all of them!
        i = 0
        for key in data:
            token_filter = (data[key]['filter'])
            char_filter = (data[key]['char_filter'])
            analyzer_item = {'tokenizer': (data[key]['tokenizer']), 'token_filter': '', 'char_filter': ''}
            for x in range(0, len(token_filter)):
                analyzer_item['token_filter'] += token_filter[x]
                if x < (len(token_filter) - 1):
                    analyzer_item['token_filter'] += ', '
            for x in range(0, len(char_filter)):
                analyzer_item['char_filter'] += char_filter[x]
                if x < (len(char_filter) - 1):
                    analyzer_item['char_filter'] += ', '
            analyzers[i] = analyzer_item
            i += 1
    # if no analyzer exist, standard analyzer is hardcoded as anlayzer
    else:
        analyzer_item = {'tokenizer': 'standard', 'token_filter': 'standard, lowercase', 'char_filter': ''}
        analyzers[0] = analyzer_item
    return analyzers


def fetch_metrics(base_url, index, queries):
    """
    :param base_url: Elasticsearch base URL to read metrics from
    :param index: Elasticsearch index to collect metrics for
    :param queries: Elasticsearch queries to run
    :return: Elasticsearch response
    """
    successful = 0
    stats = {}
    timing = []
    response_file = open("response_" + index + ".txt", "w")
    cache_file = open("cache_" + index + ".txt", "w")
    stats_file = open("stats_" + index + ".txt", "w")
    url_search = '%s/_search?pretty' % base_url
    url_cache = '%s/_cache/clear?pretty' % base_url
    url_stat = '%s/_stats' % base_url
    # collect doc and size of index
    stats_resp = requests.get(url_stat)
    stats_json = stats_resp.json()
    stats_file.write(str(stats_json))
    stats_file.write("\n")
    stats['docs'] = (stats_json['indices'][index]['total']['docs']['count'])
    stats['size'] = (stats_json['indices'][index]['total']['store']['size_in_bytes'])
    stats_file.close()

    # execute a request to es for each query as often as number_exec, clear the cache before each execution
    for q in queries:
        for x in range(0, number_exec):
            # clear ES cache
            cache = requests.post(url_cache)
            cache_json = cache.json()
            cache_file.write(str(cache_json))
            cache_file.write("\n")
            # execute request for the query
            response = requests.get(url_search, data='{"profile": true,"query":' + q + '}')
            response_json = response.json()
            response_file.write(str(response_json))
            response_file.write("\n")
            if response.status_code == 200:
                x += 1
                successful += 1
                response_json = response.json()
                timing.append(str(response_json['took']))
    mean_timing = calculate_mean(timing)

    response_file.close()
    cache_file.close()

    return mean_timing, successful, stats


def output(index, time_per_index, successful_per_index, stats_per_index, queries_num, analyzer_per_index,
           not_existing_indices):
    # Calculations for the output
    total = queries_num * number_exec
    failed = {}
    suc_rate = {}
    for ind in index:
        failed[ind] = total - successful_per_index[ind]
        if total != 0:
            suc_rate[ind] = successful_per_index[ind] / total * 100
        else:
            suc_rate[ind] = 0
    timing = {}

    # Naming the headline for each row
    index_str = 'Index'
    token_str = 'Tokenizer'
    token_filter_str = 'Token Filters'
    char_filter_str = 'Char Filters'
    query_str = 'Queries'
    rep_str = 'Repetitions'
    total_str = 'Total'
    suc_str = 'Successful'
    failed_str = 'Failed'
    suc_rate_str = 'Success rate'
    docs_str = 'Docs'
    size_str = 'Size [GB]'
    avg_speed_str = 'Average speed [ms]'

    # calculating the length for each row
    index_len = col_length(index_str, index)
    token_len = col_length(token_str, analyzer_per_index, 'tokenizer')
    token_filter_len = col_length(token_str, analyzer_per_index, 'token_filter')
    char_filter_len = col_length(token_str, analyzer_per_index, 'char_filter')
    query_len = col_length(query_str, queries_num)
    rep_len = col_length(rep_str, number_exec)
    total_len = col_length(total_str, total)
    suc_len = col_length(suc_str, successful_per_index)
    failed_len = col_length(failed_str, failed)
    suc_rate_len = col_length(suc_rate_str, suc_rate)
    docs_len = col_length(docs_str, stats_per_index, 'docs')
    size_len = col_length(size_str, stats_per_index, 'size')
    avg_speed_len = col_length(avg_speed_str, time_per_index)

    print()

    # print indices which does not exist if there are any
    if not_existing_indices:
        print("Indices for which no calculation can be done because they don't exist:")
        for x in not_existing_indices:
            print(x)
        print()

    # print analyzers per index
    print('Analyzers:')
    print('| {0:^{4}s} | {1:^{5}s} | {2:^{6}s} | {3:^{7}s} |'.format(index_str,
                                                                     token_str,
                                                                     token_filter_str,
                                                                     char_filter_str,
                                                                     index_len,
                                                                     token_len,
                                                                     token_filter_len,
                                                                     char_filter_len))
    for ind in index:
        for key in analyzer_per_index[ind]:
            print('| {0:^{4}s} | {1:^{5}s} | {2:^{6}s} | {3:^{7}s} |'.format(ind,
                                                                             analyzer_per_index[ind][key]['tokenizer'],
                                                                             analyzer_per_index[ind][key][
                                                                                 'token_filter'],
                                                                             analyzer_per_index[ind][key][
                                                                                 'char_filter'],
                                                                             index_len,
                                                                             token_len,
                                                                             token_filter_len,
                                                                             char_filter_len))
    print()

    # calculate & print query stats per index
    print('Query stats:')
    print(
        '| {0:^{7}s} | {1:^{8}s} | {2:^{9}s} | {3:^{10}s} | {4:^{11}s} | {5:^{12}s} | {6:^{13}s} |'.format(index_str,
                                                                                                           query_str,
                                                                                                           rep_str,
                                                                                                           total_str,
                                                                                                           suc_str,
                                                                                                           failed_str,
                                                                                                           suc_rate_str,
                                                                                                           index_len,
                                                                                                           query_len,
                                                                                                           rep_len,
                                                                                                           total_len,
                                                                                                           suc_len,
                                                                                                           failed_len,
                                                                                                           suc_rate_len))
    for ind in index:
        print('| {0:^{7}s} | {1:^{8}d} | {2:^{9}d} | {3:^{10}d} | {4:^{11}d} | {5:^{12}d} | {6:^{13}s} |'.format(ind,
                                                                                                                 queries_num,
                                                                                                                 number_exec,
                                                                                                                 total,
                                                                                                                 successful_per_index[
                                                                                                                     ind],
                                                                                                                 failed[
                                                                                                                     ind],
                                                                                                                 '%s %%' %
                                                                                                                 suc_rate[
                                                                                                                     ind],
                                                                                                                 index_len,
                                                                                                                 query_len,
                                                                                                                 rep_len,
                                                                                                                 total_len,
                                                                                                                 suc_len,
                                                                                                                 failed_len,
                                                                                                                 suc_rate_len))
    print()

    # print number of docs, size of index and average speed
    print("Speed:")
    print(
        '| {0:^{4}s} | {1:^{5}s} | {2:^{6}s} | {3:^{7}s} |'.format(index_str, docs_str, size_str, avg_speed_str,
                                                                   index_len, docs_len,
                                                                   size_len, avg_speed_len))
    for ind in index:
        print('| {0:^{4}s} | {1:^{5}d} | {2:^{6}f} | {3:^{7}s} |'.format(ind, stats_per_index[ind]['docs'],
                                                                         stats_per_index[ind]['size'] * 0.000000001,
                                                                         str(time_per_index[ind]),
                                                                         index_len, docs_len,
                                                                         size_len, avg_speed_len))
    print()


@click.command()
@click.argument('queries_location')
@click.option('--index', '-i', multiple=True, help='The index to test (no wildcards with * allowed).')
@click.option('--protocol', default="http", help='Hypertext transfer protocol. Either http or https (default: http).')
@click.option('--url', default="localhost", help='The url of elasticsearch (default: localhost).')
@click.option('--port', default=9200, help='The port number of elasticsearch (default: 9200).')
@click.option('--runs', '-r', default=1, help='The amount of repetitions per query.')
def initiation(queries_location, index, protocol, url, port, runs):
    global number_exec

    url_dict = {}
    number_exec = runs
    index = list(index)
    if len(index) == 0:
        print('No index specified. Please use --index foo or -i foo to specify an index.')
    else:
        # create urls and check if index exists
        not_existing_indices = []
        for ind in index:
            if check_if_index_exists('%s://%s:%s/%s' % (protocol, url, str(port), ind)):
                url_dict[ind] = '%s://%s:%s/%s' % (protocol, url, str(port), ind)
            else:
                not_existing_indices.append(ind)
        # remove not existing indices from index list
        if not_existing_indices:
            for x in not_existing_indices:
                index.remove(x)
        # parse queries
        with open(queries_location) as f:
            query_list = f.readlines()
        # removes whitespace chars (e.g. '\n') and leave empty entry
        query_list = [x.strip() for x in query_list]
        # remove empty entry in query_list
        query_list = [x for x in query_list if x]
        timing_per_index = {}
        successful_per_index = {}
        stats_per_index = {}
        analyzer_per_index = {}
        for ind in url_dict:
            timing_per_index[ind], successful_per_index[ind], stats_per_index[ind] = fetch_metrics(url_dict[ind], ind,
                                                                                                   query_list)
            analyzer_per_index[ind] = fetch_analyzer(url_dict[ind], ind)
        output(index, timing_per_index, successful_per_index, stats_per_index, len(query_list), analyzer_per_index,
               not_existing_indices)


if __name__ == '__main__':
    initiation()
