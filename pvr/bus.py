import logging

log = logging.getLogger('mythbox.event')


class Event(object):
    RECORDING_DELETED    = 'RECORDING_DELETED'  # keys: id, program
    RECORDING_STARTED    = 'RECORDING_STARTED'  # keys: id
    RECORDING_ENDED      = 'RECORDING_ENDED'    # keys: id
    SETTING_CHANGED      = 'SETTING_CHANGED'    # keys: id, tag, old, new
    SHUTDOWN             = 'SHUTDOWN'           # keys: None
    SCHEDULER_RAN        = 'SCHEDULER_RAN'      # keys: None
    SCHEDULE_CHANGED     = 'SCHEDULE CHANGED'   # keys: None recording schedule added/deleted/updated
    COMMFLAG_START       = 'COMMFLAG_START'     # [u'BACKEND_MESSAGE', u'COMMFLAG_START 4276 2011-06-02T17:00:00', u'empty']   
    
    
class EventBus(object):
    
    def __init__(self):
        self.listeners = []
        
    def register(self, listener, firstDibs=False):
        if firstDibs:
            self.listeners.insert(0, listener)
        else:
            self.listeners.append(listener)

    def deregister(self, listener):
        try:
            self.listeners.remove(listener)
        except ValueError, ve:
            log.error(ve)

    def publish(self, event):
        """
        @type event: dict
        @param event: Put in whatever you like. The only mandatory key is 'id'
        """
        log.debug('Publishing event %s to %d listeners' % (event, len(self.listeners)))
        for listener in self.listeners[:]:
            try:
                listener.onEvent(event)
            except:
                log.exception('Error publishing event %s to %s' % (event, listener))
