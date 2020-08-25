import argparse
import asyncio
import inspect
import logging
from importlib import import_module

DEFAULT_FORMATTER = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s]:%(message)s'
logging.basicConfig(format=DEFAULT_FORMATTER, level=logging.INFO)


def script_main(params):
    client = params.get('client')
    module = import_module('.'.join(['clients', client]))
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and str(obj).find('clients') != -1:
            instance = obj()
            func = getattr(instance, 'run')
            try:
                asyncio.get_event_loop().run_until_complete(func(**params))
            except Exception as e:
                logging.warning(e)
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client', required=True)
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    parser.add_argument('--git-url')
    parser.add_argument('--headless', action='store_true')
    args = parser.parse_args()
    params = vars(args)
    params['headless'] = True if not params['headless'] else False
    script_main(params)


if __name__ == '__main__':
    main()
