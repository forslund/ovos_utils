from setuptools import setup

setup(
    name='ovos_utils',
    version='0.0.4',
    packages=['ovos_utils',
              'ovos_utils.waiting_for_mycroft',
              'ovos_utils.misc',
              'ovos_utils.intents',
              'ovos_utils.sound',
              'ovos_utils.mark1',
              'ovos_utils.skills',
              'ovos_utils.lang'],
    url='https://github.com/OpenVoiceOS/ovos_utils',
    install_requires=["phoneme_guesser",
                      "mycroft-messagebus-client",
                      "inflection",
                      "colour",
                      "pexpect",
                      "requests"],
    include_package_data=True,
    license='Apache',
    author='jarbasAI',
    author_email='jarbasai@mailfence.com',
    description='collection of simple utilities for use across the mycroft ecosystem'
)
