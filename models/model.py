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
i = lm.add_intent('TestIntent')
i.samples.append(Expandable('this is a <test|check>'))
i = lm.add_intent('ChannelChangeIntent')
i.samples.append(Expandable('change <|channel |channels >to <|channel ><{channel_name}|{channel_number}>'))
i.add_slot(name='channel_name', slot_type='AMAZON.TelevisionChannel')
i.add_slot(name='channel_number', slot_type='AMAZON.NUMBER')
m.save('en-US.json')