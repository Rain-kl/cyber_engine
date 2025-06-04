from utils.event_log import EventLog, EventLogModel


def test_EventLogModel():
    elogger=EventLog(db_path='../data/test_event_log.db')
    elogger.init()
    elogger.log(EventLogModel(user_id=123,type='msg',level=EventLogModel.LEVEL.INFO,message='test'))
