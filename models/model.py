import json

from lambdaskill.model import InteractionModel, Expandable

m = InteractionModel()
lm = m.add_language_model('tivo')
lm.add_intent('AMAZON.HelpIntent')
lm.add_intent('AMAZON.StopIntent')
lm.add_intent('AMAZON.CancelIntent')
i = lm.add_intent('PauseIntent')
i.samples.append(Expandable('<pause|stop|suspend|freeze>'))
i = lm.add_intent('ResumeIntent')
i.samples.append(Expandable('<resume|restart|continue|go>'))
i = lm.add_intent('AdvanceIntent')
i.samples.append(Expandable('<advance|skip ahead>'))
i = lm.add_intent('SelectIntent')
i.samples.append(Expandable('<select|confirm>'))
i = lm.add_intent('LiveIntent')
i.samples.append(Expandable('<|go ><live|live tv|swap tuners>'))
i = lm.add_intent('LastChannelIntent')
i.samples.append(Expandable('<|go to |change to ><|the ><last|previous><| channel>'))
st = lm.add_slot_type('DIRECTION_KEY')
st.add_values(['up', 'down', 'left', 'right'])
i = lm.add_intent('DirectionIntent')
i.samples.append(Expandable('<|go >{direction}'))
i.add_slot(name='direction', slot_type='DIRECTION_KEY')
st = lm.add_slot_type('TYPED_INPUT')
st.add_values(['transcendental',
               "dilly's",
               'stilettoes',
               'juncoes bedroom',
               'reconciliation neurotically',
               "senna reel's",
               'intolerant spare Xenophon',
               "peak's denigrating Oswald",
               "trucker's crippled groundlessly",
               "fondues Uris dibble's commandment's",
               "psalmist Titania pizzicato flywheel's",
               "meteor Polaris Margo's consigned",
               "aviary's maxilla marvels demagog's repaid",
               "bonniest Acevedo's hoods dolling inland's",
               "scurf's organ eyeglass nontechnical gybe",
               'finery sealed renaissance drain pancakes shying',
               "Tuscany's popgun's ounces baboon's vertebrae auspiciousness",
               'klutzy fouls kindle murmurs bestirring malefactors',
               "Georgina intercom's warhorse tumble's soufflés climate's freebie's",
               "loophole's classics Dushanbe tithes unlikeliest dislodges complaisantly",
               "leaps shipbuilder patchier polygon restlessness racking tweeter's",
               "sorcerer's dissenting viscount's indigestible sibling Bolivian revivified compulsory's"])
i = lm.add_intent('TypedIntent')
i.samples.append('<type|input> {words_to_type}')
i.add_slot(name='words_to_type', slot_type='TYPED_INPUT')
i = lm.add_intent('ChannelChangeIntent')
i.samples.append(Expandable('change <|channel |channels >to <|channel ><{channel_name}|{channel_number}>'))
i.add_slot(name='channel_name', slot_type='AMAZON.TelevisionChannel')
i.add_slot(name='channel_number', slot_type='AMAZON.NUMBER')
m.save('en-US.json')