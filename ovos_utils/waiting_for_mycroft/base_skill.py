import re
from os.path import join, exists
from itertools import chain
from ovos_utils.waiting_for_mycroft.skill_gui import SkillGUI
from ovos_utils.waiting_for_mycroft.skill_api import SkillApi
try:
    from mycroft.skills.mycroft_skill import MycroftSkill as _MycroftSkill
    from mycroft.skills.fallback_skill import FallbackSkill as _FallbackSkill
    from mycroft.skills.skill_data import read_vocab_file
    from mycroft.util import resolve_resource_file
    from mycroft.skills.mycroft_skill import get_non_properties
except ImportError:
    import sys
    from ovos_utils.log import LOG
    from ovos_utils import get_mycroft_root
    MYCROFT_ROOT_PATH = get_mycroft_root()
    if MYCROFT_ROOT_PATH is not None:
        sys.path.append(MYCROFT_ROOT_PATH)
        from mycroft.skills.mycroft_skill import MycroftSkill as _MycroftSkill
        from mycroft.skills.fallback_skill import FallbackSkill as _FallbackSkill
        from mycroft.skills.skill_data import read_vocab_file
        from mycroft.util import resolve_resource_file
        from mycroft.skills.mycroft_skill import get_non_properties
    else:
        LOG.error("Could not find mycroft root path")
        raise ImportError


class MycroftSkill(_MycroftSkill):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # https://github.com/MycroftAI/mycroft-core/pull/2683
        self.gui = SkillGUI(self)
        # https://github.com/MycroftAI/mycroft-core/pull/1822
        # Skill Public API
        self.public_api = {}

    # https://github.com/MycroftAI/mycroft-core/pull/1822
    def bind(self, bus):
        super(MycroftSkill, self).bind(bus)
        SkillApi.connect_bus(bus)
        self._register_public_api()

    def _send_public_api(self, message):
        """Respond with the skill's public api."""
        self.bus.emit(message.response(data=self.public_api))

    def _register_public_api(self):
        """ Find and register api methods.
        Api methods has been tagged with the api_method member, for each
        method where this is found the method a message bus handler is
        registered.
        Finally create a handler for fetching the api info from any requesting
        skill.
        """

        def wrap_method(func):
            """Boiler plate for returning the response to the sender."""
            def wrapper(message):
                result = func(*message.data['args'], **message.data['kwargs'])
                self.bus.emit(message.response(data={'result': result}))

            return wrapper

        methods = [attr_name for attr_name in get_non_properties(self)
                   if hasattr(getattr(self, attr_name), '__name__')]

        for attr_name in methods:
            method = getattr(self, attr_name)

            if hasattr(method, 'api_method'):
                doc = method.__doc__ or ''
                name = method.__name__
                self.public_api[name] = {
                    'help': doc,
                    'type': '{}.{}'.format(self.skill_id, name),
                    'func': method
                }
        for key in self.public_api:
            if ('type' in self.public_api[key] and
                    'func' in self.public_api[key]):
                LOG.debug('Adding api method: '
                          '{}'.format(self.public_api[key]['type']))

                # remove the function member since it shouldn't be
                # reused and can't be sent over the messagebus
                func = self.public_api[key].pop('func')
                self.add_event(self.public_api[key]['type'],
                               wrap_method(func))

        if self.public_api:
            self.add_event('{}.public_api'.format(self.skill_id),
                           self._send_public_api)

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
