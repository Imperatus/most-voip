'''
Created on 06/mag/2014

@author: smonni
'''
class VoipEvent(object):

    Name                    = 'VOIP_EVENT'

    Null                          = '%s__NULL' % Name
    Initializing                    = '%s__INITIALIZING' % Name               # VOIP NO YET INITIALIZED
    Initialized                   = '%s__INITIALIZED' % Name              # VOIP INITIALIZED
    Initialize_failed             = '%s__INITIALIZE_FAILED' % Name         # VOIP INITIALIZATION FAILED
    Connecting                    = '%s__CONNECTING' % Name               # CONNECTING TO SIP SERVER
    Connected                     = '%s__CONNECTED' % Name                # SIP SERVER ON LINE
    Connection_failed             = '%s__CONNECTION_FAILED' % Name
    Registering                   = '%s__REGISTERING' % Name             # REGISTERING LOCAL USER TO SIP SERVER
    Unregistering                   = '%s__UNREGISTERING' % Name             # UNREGISTERING LOCAL USER FROM SIP SERVER
    Registered                    = '%s__REGISTERED' % Name
    Unregistered                    = '%s__UNREGISTERED' % Name
    Registration_failed           = '%s__REGISTRATION_FAILED' % Name
    Unregistration_failed           = '%s__UNREGISTRATION_FAILED' % Name
    Remote_user_subscribing       = '%s__REMOTE_USER_SUBSCRIBING' % Name  # REGISTERING REMOTE USER AS BUDDY
    Remote_user_subscribing_failed  = '%s__REMOTE_USER_SUBSCRIBING_FAILED' % Name
    Remote_user_subscribed        = '%s__REMOTE_USER_SUBSCRIBED' % Name    # REMOTE BUDDY REGISTERED
    Remote_user_connected         = '%s__REMOTE_USER_CONNECTED' % Name     # REMOTE BUDDY CONNECTED
    Remote_user_disconnected      = '%s__REMOTE_USER_DISCONNECTED' % Name
    Dialing                       = '%s__CALL_DIALING' % Name          # OUTCOMING CALL
    Incoming                       = '%s__CALL_INCOMING' % Name        # INCOMING CALL
    Calling                       = '%s__CALL_ACTIVE' % Name
    Holding                       = '%s__CALL_HOLDING' % Name
    RemoteHolding                 = '%s__CALL_REMOTE_HOLDING' % Name
    RemoteLocalHolding            = '%s__CALL_REMOTE_AND_LOCAL_HOLDING' % Name
    Unholding                     = '%s__CALL_UNHOLDING' % Name
    Hangup                        = '%s__CALL_HANGUP' % Name
    RemoteHangup                  = '%s__CALL_REMOTE_HANGUP' % Name
    RemoteDisconnectionHangup     = '%s__CALL_REMOTE_DISCONNECTION_HANGUP' % Name
    Deinitializing              = '%s__DEINITIALIZING' % Name
    DeinitializeDone              = '%s__DEINITIALIZE_DONE' % Name
    DeinitializeFailed              = '%s__DEINITIALIZE_FAILED' % Name


class CallState:
    Name                    = 'CALL_STATE'
    IDLE = '%s__IDLE' % Name
    INCOMING = '%s__INCOMING' % Name
    ACTIVE = '%s__ACTIVE' % Name
    DIALING = '%s__DIALING' % Name
    HOLDING = '%s__HOLDING' % Name
    REMOTE_HOLDING = '%s__REMOTE_HOLDING' % Name
    
    
class BuddyState:
    Name      = 'BUDDY_STATE' 
    NOT_FOUND = "%s__NOT_FOUND" % Name
    OFF_LINE= "%s__OFF_LINE" % Name
    ON_LINE= "%s__ON_LINE" % Name
    ON_HOLD= "%s__ON_HOLD" % Name
    UNKNOWN= "%s__UNKNOWN" % Name
 

class ServerState:
    Name      = 'SIP_SERVER_STATE' 
    NOT_FOUND = "%s__NOT_FOUND" % Name
    DISCONNECTED = "%s__DISCONNECTED" % Name
    CONNECTED = "%s__CONNECTED" % Name
