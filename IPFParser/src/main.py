import logging
import os
import re
import sys

from ipf_parser import unpacker, constants
from ipf_parser.parsers import parser
from ipf_parser.parsers.parser_enums import TOSRegion

# Configure logging
logging.basicConfig(format='[%(asctime)s] [%(levelname)s]\t%(message)s', datefmt='%Y-%m-%d %I:%M:%S', level=logging.DEBUG)
logging.getLogger('PIL').setLevel(logging.WARN)

# Configure working directory
os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

# Parse region
region = TOSRegion.value_of(sys.argv[1]) if len(sys.argv) == 2 else TOSRegion.iTOS
constants.region(region)

# Patch the game with the latest version
version, version_new = unpacker.unpack(region)
version_hotfix = '1'

# Parse
parser.parse(region, version, version_new + ('_hotfix_' + version_hotfix) if len(version_hotfix) else '')

# Save new version
path = os.path.join(constants.PATH_WEB_APP, 'shared', 'service', 'update.service.ts')
regex = "'" + TOSRegion.to_string(region) + "': '(.*)', \/\* " + TOSRegion.to_string(region) + "-needle \*\/"
regex_replace = "'" + TOSRegion.to_string(region) + "': '" + str(version_new) + "', /* " + TOSRegion.to_string(region) + "-needle */"

file = [re.sub(regex, regex_replace, line) for line in open(path, 'r').readlines()]
open(path, 'w').writelines(file)