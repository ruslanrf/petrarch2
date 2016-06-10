import time
import logging
import pprint
import json
import requests
import sys
import sys
sys.path.insert(0, '../')
#sys.path.append('../petrarch2')
import petrarch2

sys.path.append('../utilities')
import utilities

sys.path.append('../PETRglobals')
import PETRglobals  # global variables
sys.path.append('../PETRreader')
import PETRreader  # input routines
sys.path.append('../PETRwriter')
import PETRwriter
sys.path.append('../PETRtree')
import PETRtree


def prepare(input, configDir, configFileName):
    # cli_args = parse_cli_args()
    utilities.init_logger('PETRARCH.log')
    logger = logging.getLogger('petr_log')

    PETRglobals.RunTimeString = time.asctime()

    # if cli_args.command_name == 'parse' or cli_args.command_name == 'batch':

    logger.info('Using default config file.')
    PETRreader.parse_Config(utilities._get_data(configDir, configFileName))

    petrarch2.read_dictionaries()
    print('\n\n')

    # paths = PETRglobals.TextFileList
    paths = [input]

    return {'paths': paths}


# Scenario 1
def main():
    params = prepare('data/text/GigaWord.sample.PETR.xml',
                     'tmp/', 'PETR_config.ini')

    # if cli_args.command_name == 'parse':
    #     run(paths, out, cli_args.parsed)

    start_time = time.time()

    # out = ""  # PETRglobals.EventFileName
    out = 'test.out.txt'
    petrarch2.run(params['paths'], out, True)  ## <===

    print("Coding time:", time.time() - start_time)

    print("Finished")


# main()

# Scenario 2.1
def extract_event_1():
    params = prepare('data/text/GigaWord.sample.PETR.xml' # 'my_tmp/noParseSentences1.in'
                     , 'my_tmp/', 'PETR_config.ini')

    pp = pprint.PrettyPrinter(indent=4)

    s_parsed = True
    events = PETRreader.read_xml_input(params['paths'], s_parsed)

    print ('PARSED INPUT:')
    pp.pprint (events)
    print ('=====   =====')

    if not s_parsed:
        events = utilities.stanford_parse(events)

    # out = ""  # PETRglobals.EventFileName
    out = 'test.out.txt'
    updated_events = petrarch2.do_coding(events, out)

    print ('EVENTS:')
    pp.pprint(updated_events)
    print ('=====   =====')
    # PETRwriter.write_events(updated_events, 'evts.' + out_file)

#extract_event_1()

def hypnos_parse():
    headers = {'Content-Type': 'application/json'}
    data = {'text': "At least 37 people are dead after Islamist radical group Boko Haram assaulted a town in northeastern Nigeria.", 'id': 'abc123', 'date': '20010101'}
    data = json.dumps(data)
    r = requests.get('http://localhost:5002/hypnos/extract', data=data,  headers=headers)
    output = r.json()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(output)
    
hypnos_parse()
