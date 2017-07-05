# Elasticsearch Analyzer Test

A time measurement script for Elasticsearch analyzers written in Python.

## Use cases

Elastisearch [analyzers](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis.html) convert text into tokens which are added to the inverted index for searching.
An analyzer consist of three blocks: character filters, tokenizers and token filters.
In this order the analyzer performs operations on the input stream (character filters), then divides the input stream into tokens (tokenizer) and later on it performs some more operations on the tokens (token filters).

This python script executes search queries to the Elasticsearch search API and collects the time needed to execute this queries.
Before the execution of each query the cache gets cleared by the script.

## Prerequisites

There are a few things you need, before you can start working. Please make sure you've installed and properly configured the following software:

* [Elasticsearch 5.4.3](https://www.elastic.co/downloads/elasticsearch)
* [Python 3](https://www.python.org/downloads/)
* [Python Requests Library](http://docs.python-requests.org/en/master/) for executing curl requests.
`pip3 install requests`
* [Python Click Library](http://click.pocoo.org/5/) for the CLI. `pip3 install click`

Not required but helpful:
* [Elasticdump](https://www.npmjs.com/package/elasticdump) to dump docs easily into a testing Elasticsearch database
* [Cerebro](https://github.com/lmenezes/cerebro) to create Elasticsearch index templates

## Getting Started

Clone this repository.
```
git clone https://github.com/unidario/elasticsearch-analyzer-timing.git
```

Change the directory to `elasticsearch-analyzer-timing`
```
cd elasticsearch-analyzer-timing
```

Create a txt file with example queries in this directory.
Each query has to be written in a new line inside the txt file.

Start the script by providing the path to the queries txt file and at least one index.

```
python3 analyzer_test.py $PATH_TO_QUERY_TXT_FILE -i $index -i $index2
```

See the [configuration](#Configuration) for all options.

## Configuration

| Option          | Description                                                  | Required | Default     |
|-----------------|--------------------------------------------------------------|----------|-------------|
| `--help`        | Show help message and exit                                   |          |             |
| `-i`, `--index` | One Elasticsearch index to test (can be used multiple times) | yes      |             |
| `--protocol`    | Hypertext transfer protocol (either `http` or `https`)       | no       | `http`      |
| `--url`         | The url of Elasticsearch                                     | no       | `localhost` |
| `--port`        | The port number of Elasticsearch                             | no       | `9200`      |
| `-r`, `--runs`  | The amount of executions per query                           | no       | `1`         |

## Output

The script creates the output inside the bash.

The output contains of 4 Elements:
1. Indices which could not be tested because they don't exist in the database (only if necessary).
2. Output of all analyzers for each index.
3. Stats for the executed queries per index.
4. Stats for the timing, doc amount and size of the index.

Sample Output:
```
Indices for which no calculation can be done because they don't exist:
index_x, index_y

Analyzers:
|  Index  | Tokenizer |    Token Filters    |    Char Filters     |
| index_a | standard  | standard, lowercase |                     |
| index_b |  pattern  |  lowercase, unique  | html_strip, mapping |

Query stats:
|  Index  | Queries | Repetitions | Total | Successful | Failed |   Success rate    |
| index_a |    6    |     70      |  420  |    420     |   0    |      100.0 %      |
| index_b |    6    |     70      |  420  |    350     |   70   | 0.8333333333333 % |

Speed:
|  Index  |  Docs  | Size [GB] | Average speed [ms] |
| index_a | 193438 | 0.238148  | 257.3333333333333  |
| index_a | 386876 | 0.423296  |       312.42       |

```

## Authors

* **Dario Segger** - *Initial work*


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
