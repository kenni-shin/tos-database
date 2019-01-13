# coding=utf-8
import csv
import logging
import os

import constants
import globals
from parserr import parser_assets
from parserr import parser_translations
from utils.tosenum import TOSEnum


class TOSJobDifficulty(TOSEnum):
    EASY = 0
    HARD = 1
    NORMAL = 2

    @staticmethod
    def value_of(string):
        return {
            '쉬움': TOSJobDifficulty.EASY,
            '어려움': TOSJobDifficulty.HARD,
            '보통': TOSJobDifficulty.NORMAL,
            '': None,
        }[string]


class TOSJobTree(TOSEnum):
    ARCHER = 0
    CLERIC = 1
    SCOUT = 2
    WARRIOR = 3
    WIZARD = 4

    @staticmethod
    def value_of(string):
        return {
            'ARCHER': TOSJobTree.ARCHER,
            'CLERIC': TOSJobTree.CLERIC,
            'SCOUT': TOSJobTree.SCOUT,
            'WARRIOR': TOSJobTree.WARRIOR,
            'WIZARD': TOSJobTree.WIZARD,
        }[string.upper()]


class TOSJobType(TOSEnum):
    ATTACK = 0
    ATTACK_INSTALL = 1
    ATTACK_MOBILITY = 2
    ATTACK_SUMMON = 3
    CRAFTING = 4
    DEFENSE = 5
    DEFENSE_PROVOKE = 6
    SUPPORT = 7
    SUPPORT_CONTROL = 8
    SUPPORT_PARTY = 9

    @staticmethod
    def value_of(string):
        return {
            '공격': TOSJobType.ATTACK,
            '조련': TOSJobType.SUPPORT_CONTROL,
            '제작': TOSJobType.CRAFTING,
            '방어': TOSJobType.DEFENSE,
            '설치형 공격': TOSJobType.ATTACK_INSTALL,
            '기동형 공격': TOSJobType.ATTACK_MOBILITY,
            '파티': TOSJobType.SUPPORT_PARTY,
            '도발': TOSJobType.DEFENSE_PROVOKE,
            '소환': TOSJobType.ATTACK_SUMMON,
            '지원': TOSJobType.SUPPORT,
            '보조': TOSJobType.SUPPORT,
            '': None
        }[string]


def parse(is_rebuild):
    parse_jobs()

    if is_rebuild:
        parse_jobs_stats()


def parse_jobs():
    logging.debug('Parsing jobs...')

    ies_path = os.path.join(constants.PATH_INPUT_DATA, 'ies.ipf', 'job.ies')

    with open(ies_path, 'rb') as ies_file:
        for row in csv.DictReader(ies_file, delimiter=',', quotechar='"'):
            obj = {}
            obj['$ID'] = int(row['ClassID'])
            obj['$ID_NAME'] = row['ClassName']
            obj['Description'] = parser_translations.translate(row['Caption1'])
            obj['Icon'] = parser_assets.parse_entity_icon(row['Icon'])
            obj['Name'] = parser_translations.translate(row['Name'])

            obj['CircleMax'] = int(row['MaxCircle'])
            obj['JobDifficulty'] = TOSJobDifficulty.value_of(row['ControlDifficulty'])
            obj['JobTree'] = TOSJobTree.value_of(row['CtrlType'])
            obj['JobType'] = [TOSJobType.value_of(v.strip()) for v in row['ControlType'].split(',')] if len(row['ControlType']) else None
            obj['IsHidden'] = row['HiddenJob'] == 'YES'
            obj['IsSecret'] = obj['IsHidden'] and len(row['PreFunction']) > 0
            obj['IsStarter'] = int(row['Rank']) == 1
            obj['Rank'] = int(row['Rank'])
            obj['Stat_CON'] = int(row['CON'])
            obj['Stat_DEX'] = int(row['DEX'])
            obj['Stat_INT'] = int(row['INT'])
            obj['Stat_SPR'] = int(row['MNA'])
            obj['Stat_STR'] = int(row['STR'])
            obj['StatBase_CON'] = 0
            obj['StatBase_DEX'] = 0
            obj['StatBase_INT'] = 0
            obj['StatBase_SPR'] = 0
            obj['StatBase_STR'] = 0

            obj['Link_Attributes'] = []
            obj['Link_Skills'] = []

            globals.jobs[obj['$ID']] = obj
            globals.jobs_by_name[obj['$ID_NAME']] = obj


def parse_jobs_stats():
    logging.debug('Parsing base stats for jobs...')

    ies_path = os.path.join(constants.PATH_INPUT_DATA, 'ies.ipf', 'statbase_pc.ies')

    with open(ies_path, 'rb') as ies_file:
        for row in csv.DictReader(ies_file, delimiter=',', quotechar='"'):
            if not len(row['ClassName']):
                continue

            job_tree = TOSJobTree.value_of(row['ClassName'])

            for job in globals.jobs.values():
                if job['JobTree'] == job_tree:
                    job['StatBase_CON'] = int(row['CON'])
                    job['StatBase_DEX'] = int(row['DEX'])
                    job['StatBase_INT'] = int(row['INT'])
                    job['StatBase_SPR'] = int(row['MNA'])
                    job['StatBase_STR'] = int(row['STR'])


def parse_links():
    parse_links_attributes()
    parse_links_skills()


def parse_links_attributes():
    logging.debug('Parsing attributes for jobs...')

    ies_path = os.path.join(constants.PATH_INPUT_DATA, 'ies.ipf', 'job.ies')

    with open(ies_path, 'rb') as ies_file:
        for row in csv.DictReader(ies_file, delimiter=',', quotechar='"'):
            job = globals.jobs_by_name[row['ClassName']]

            ies_path = os.path.join(constants.PATH_INPUT_DATA, 'ies_ability.ipf', 'ability_' + row['EngName'] + '.ies')

            # If this job is still under development, skip
            if not os.path.isfile(ies_path):
                continue

            with open(ies_path, 'rb') as ies_file:
                for row in csv.DictReader(ies_file, delimiter=',', quotechar='"'):
                    attribute = globals.attributes_by_name[row['ClassName']]

                    if not attribute['Link_Skill'] or isinstance(attribute['Link_Skill'], basestring) and attribute['Link_Skill'] == 'All':
                        job['Link_Attributes'].append(globals.get_attribute_link(row['ClassName']))


def parse_links_skills():
    logging.debug('Parsing skills for jobs...')

    ies_path = os.path.join(constants.PATH_INPUT_DATA, 'ies.ipf', 'skilltree.ies')

    with open(ies_path, 'rb') as ies_file:
        for row in csv.DictReader(ies_file, delimiter=',', quotechar='"'):
            # Ignore discarded skills (e.g. Bokor's 'Summon: ' skills)
            if row['SkillName'] not in globals.skills_by_name:
                continue

            job = '_'.join(row['ClassName'].split('_')[:2])
            job = globals.jobs_by_name[job]
            job['Link_Skills'].append(globals.get_skill_link(row['SkillName']))