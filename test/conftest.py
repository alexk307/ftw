import pytest
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from ftw import ruleset

def get_rulesets(ruledir):
    """
    List of ruleset objects extracted from the yaml directory
    """
    from ftw import ruleset, util
    yaml_files = util.get_files(ruledir, 'yaml')
    extracted_files = util.extract_yaml(yaml_files)
    rulesets = []
    for extracted_yaml in extracted_files:
        rulesets.append(ruleset.Ruleset(extracted_yaml))
    return rulesets

def get_testdata(rulesets):
    """
    In order to do test-level parametrization (is this a word?), we have to
    bundle the test data from rulesets into tuples so py.test can understand 
    how to run tests across the whole suite of rulesets
    """
    testdata = []
    for ruleset in rulesets:
        for test in ruleset.tests:
            testdata.append((ruleset, test))

    return testdata

def test_id(val):
    """
    Dynamically names tests, useful for when we are running dozens to hundreds
    of tests
    """
    if isinstance(val, (dict,ruleset.Test,)):
        return '%s_ruleid_%s' % (val.ruleset_meta['name'], val.rule_id)

@pytest.fixture
def destaddr(request):
    """
    Destination address override for tests
    """
    return request.config.getoption('--destaddr')

@pytest.fixture
def http_serv_obj():
    """
    Return an HTTP object listening on localhost port 80 for testing
    """
    return HTTPServer(('localhost', 80), SimpleHTTPRequestHandler)

def pytest_addoption(parser):
    """
    Adds command line options to py.test
    """
    parser.addoption('--ruledir', action='store', default='.',
        help='rule directory that holds YAML files for testing')
    parser.addoption('--destaddr', action='store', default=None,
        help='destination address to direct tests towards')

def pytest_generate_tests(metafunc):
    """
    Pre-test configurations, mostly used for parametrization
    """
    if metafunc.config.option.ruledir:
        rulesets = get_rulesets(metafunc.config.option.ruledir)
        if 'ruleset' in metafunc.fixturenames and 'test' in metafunc.fixturenames:
            metafunc.parametrize('ruleset,test', get_testdata(rulesets),
                ids=test_id)
