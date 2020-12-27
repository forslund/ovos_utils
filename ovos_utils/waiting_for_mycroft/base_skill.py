import re
from os.path import join, exists
from itertools import chain
from ovos_utils.log import LOG
from ovos_utils import get_mycroft_root
from ovos_utils.waiting_for_mycroft.skill_gui import SkillGUI
try:
    from mycroft.skills.mycroft_skill import MycroftSkill as _MycroftSkill, \
        FallbackSkill as _FallbackSkill
    from mycroft.skills.skill_data import read_vocab_file
    from mycroft.util import resolve_resource_file
except ImportError:
    import sys
    MYCROFT_ROOT_PATH = get_mycroft_root()
    if MYCROFT_ROOT_PATH is not None:
        sys.path.append(MYCROFT_ROOT_PATH)
        from mycroft.skills.mycroft_skill import MycroftSkill as \
            _MycroftSkill, FallbackSkill as _FallbackSkill
        from mycroft.skills.skill_data import read_vocab_file
        from mycroft.util import resolve_resource_file
    else:
        LOG.error("Could not find mycroft root path")
        raise ImportError


class MycroftSkill(_MycroftSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # https://github.com/MycroftAI/mycroft-core/pull/2683
        self.gui = SkillGUI(self)

    # https://github.com/MycroftAI/mycroft-core/pull/2675
    def voc_match(self, utt, voc_filename, lang=None, exact=False):
        """Determine if the given utterance contains the vocabulary provided.
        Checks for vocabulary match in the utterance instead of the other
        way around to allow the user to say things like "yes, please" and
        still match against "Yes.voc" containing only "yes". The method first
        checks in the current skill's .voc files and secondly the "res/text"
        folder of mycroft-core. The result is cached to avoid hitting the
        disk each time the method is called.
        Arguments:
            utt (str): Utterance to be tested
            voc_filename (str): Name of vocabulary file (e.g. 'yes' for
                                'res/text/en-us/yes.voc')
            lang (str): Language code, defaults to self.long
            exact (bool): comparison using "==" instead of "in"
        Returns:
            bool: True if the utterance has the given vocabulary it
        """
        lang = lang or self.lang
        cache_key = lang + voc_filename
        if cache_key not in self.voc_match_cache:
            # Check for both skill resources and mycroft-core resources
            voc = self.find_resource(voc_filename + '.voc', 'vocab')
            if not voc:  # Check for vocab in mycroft core resources
                voc = resolve_resource_file(join('text', lang,
                                                 voc_filename + '.voc'))

            if not voc or not exists(voc):
                raise FileNotFoundError(
                    'Could not find {}.voc file'.format(voc_filename))
            # load vocab and flatten into a simple list
            vocab = read_vocab_file(voc)
            self.voc_match_cache[cache_key] = list(chain(*vocab))
        if utt:
            if exact:
                # Check for exact match
                return any(i.strip() == utt
                           for i in self.voc_match_cache[cache_key])
            else:
                # Check for matches against complete words
                return any([re.match(r'.*\b' + i + r'\b.*', utt)
                            for i in self.voc_match_cache[cache_key]])
        else:
            return False


class FallbackSkill(MycroftSkill, _FallbackSkill):
    """ """
