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
    params = prepare( 'my_tmp/noParseSentences1.in' #'data/text/GigaWord.sample.PETR.xml'
                     , 'my_tmp/', 'PETR_config.ini')

    pp = pprint.PrettyPrinter(indent=4)

    s_parsed = False
    events = PETRreader.read_xml_input(params['paths'], s_parsed)

    print ('PARSED INPUT:')
    pp.pprint (events)
    print ('=====   =====')

    if not s_parsed:
        events = stanford_parse(events)

    # out = ""  # PETRglobals.EventFileName
    out = 'test.out.txt'
    updated_events = petrarch2.do_coding(events, out)

    print ('EVENTS:')
    pp.pprint(updated_events)
    print ('=====   =====')
    # PETRwriter.write_events(updated_events, 'evts.' + out_file)

def hypnos_parse():
    headers = {'Content-Type': 'application/json'}
    data = {'text': "At least 37 people are dead after Islamist radical group Boko Haram assaulted a town in northeastern Nigeria.", 'id': 'abc123', 'date': '20010101'}
    data = json.dumps(data)
    r = requests.get('http://localhost:5002/hypnos/extract', data=data,  headers=headers)
    output = r.json()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(output)
    
# hypnos_parse()


import corenlp

def stanford_parse(event_dict):
    logger = logging.getLogger('petr_log')
    # What is dead can never die...
    print("\nSetting up StanfordNLP. The program isn't dead. Promise.")
    logger.info('Setting up StanfordNLP')
    core = corenlp.StanfordCoreNLP(PETRglobals.stanfordnlp,
                                   properties=_get_data('data/config/',
                                                        'petrarch.properties'),
                                   memory='2g')
    total = len(list(event_dict.keys()))
    print(
        "Stanford setup complete. Starting parse of {} stories...".format(total))
    logger.info(
        'Stanford setup complete. Starting parse of {} stories.'.format(total))
    for i, key in enumerate(event_dict.keys()):
        if (i / float(total)) * 100 in [10.0, 25.0, 50, 75.0]:
            print('Parse is {}% complete...'.format((i / float(total)) * 100))
        for sent in event_dict[key]['sents']:
            logger.info('StanfordNLP parsing {}_{}...'.format(key, sent))
            sent_dict = event_dict[key]['sents'][sent]

            if len(sent_dict['content']) > 512 or len(
                    sent_dict['content']) < 64:
                logger.warning(
                    '\tText length wrong. Either too long or too short.')
                pass
            else:
                try:
                    stanford_result = core.raw_parse(sent_dict['content'])
                    s_parsetree = stanford_result['sentences'][0]['parsetree']
                    if 'coref' in stanford_result:
                        sent_dict['coref'] = stanford_result['coref']

                    # TODO: To go backwards you'd do str.replace(' ) ', ')')
                    sent_dict['parsed'] = _format_parsed_str(s_parsetree)
                except Exception as e:
                    print('Something went wrong. See log file.')
                    logger.warning(
                        'Error on {}_{}. {}'.format(key, sent, e))
    print('Done with StanfordNLP parse...\n\n')
    logger.info('Done with StanfordNLP parse.')

    return event_dict

extract_event_1()