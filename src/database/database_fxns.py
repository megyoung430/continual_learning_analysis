import numpy as np
import pandas as pd
import json

def get_dates_as_strings(dates):

    """
    This function takes datetime objects for all your session dates and returns them as an array of strings.

    Inputs:
        - dates (array of datetime objects): the dates as datetime objects for each session. This will be the automatic format of the 
        dataframe column with the header "sessiondate" (i.e., df.sessiondate).
    
    Outputs:
        - dates_as_strings (array): array of the dates as strings in the format 'M/D/Y' (e.g., '11/20/23' for 20th Nov 2023)
    """

    dates_as_strings = []
    for date in dates:
        dates_as_strings.append(date.strftime('%D'))
    return np.array(dates_as_strings)

def get_session_dates(dbe, task_name, startdate):

    query = 'select * from beh.sessview where protocol="' + task_name + '"'
    df = pd.read_sql(query, dbe)
    sessiondates = get_dates_as_strings(df.sessiondate)
    startdate_ind = np.where(sessiondates == startdate)[0]
    return sessiondates[startdate_ind:]

def get_sess_ids(dbe, task_name, subjid=None, sessiondate=None, settings_name=None, just_ids=True):

    """
    This function will get the session IDs for particular sessions you want to analyze.
    These sessions IDs can then be used to create specific queries to get the data for only specific sessions.

    Inputs:
        - dbe (Engine object): database engine
        - task_name (string): name of a task (e.g., "prey_foraging_fm")
        - subjid (string): name of a subject of interest (e.g., "EXN-R-0013")
        - sessiondate (char): date of a session of interest. MUST BE in 'M/D/Y' format (e.g., '11/20/23' for 20th Nov 2023)
        - settings_name (string): name of your settings of interest, likely reflecting a training state of interest (e.g., "default")
        - just_ids (bool): If true, it will return just the session_ids as an array, where the 0th index corresponds to the 1st session ID.
        If false, it will stay in the pandas dataframe format where you need to index it by its row in the dataframe. This means that the
        1st session may not have a 0th index but will retain the its original index from the dataframe.
    
    Outputs:
        - If just_ids is True:
            just_sess_ids (array): array of the session IDs associated with sessions that you want to analyze.
        - If just_ids is False:
            sess_ids (array): array of the session IDs associated with sessions that you want to analyze.
            sess_ids_inds (array): array of the indices for the session IDs.
    """

    query = 'select * from beh.sessview where protocol="' + task_name + '"'
    df = pd.read_sql(query, dbe)
    sess_ids = df.sessid
    sess_ids_inds = np.arange(0,sess_ids.shape[0])

    if subjid is not None:
        subjid_inds = np.where(df.subjid == subjid)[0]
        sess_ids_inds = np.intersect1d(sess_ids_inds, subjid_inds)
        sess_ids = sess_ids[sess_ids_inds]
    
    if sessiondate is not None:
        sessiondates = get_dates_as_strings(df.sessiondate)
        sessiondate_inds = np.where(sessiondates == sessiondate)[0]
        sess_ids_inds = np.intersect1d(sess_ids_inds, sessiondate_inds)
        sess_ids = sess_ids[sess_ids_inds]

    if settings_name is not None:
        settings_name_inds = np.where(df.settings_name == settings_name)[0]
        sess_ids_inds = np.intersect1d(sess_ids_inds, settings_name_inds)
        sess_ids = sess_ids[sess_ids_inds]

    if just_ids:
        just_sess_ids = []
        for i in range(sess_ids_inds.shape[0]):
            just_sess_ids.append(sess_ids[sess_ids_inds[i]])
        return np.asarray(just_sess_ids)
    else:
        return sess_ids, sess_ids_inds

def get_sess_ids_across_multiple_dates(dbe, task_name, sessiondates, subjid=None, settings_name=None):

    """
    This function will get the session IDs for particular sessions you want to analyze.
    These sessions IDs can then be used to create specific queries to get the data for only specific sessions.

    Inputs:
        - dbe (Engine object): database engine
        - task_name (string): name of a task (e.g., "prey_foraging_fm")
        - subjid (string): name of a subject of interest (e.g., "EXN-R-0013")
        - sessiondate (list of chars): list of dates of sessions of interest. MUST BE in 'M/D/Y' format (e.g., '11/20/23' for 20th Nov 2023)
        - settings_name (string): name of your settings of interest, likely reflecting a training state of interest (e.g., "default")
    
    Outputs:
        - sess_ids: array of the session IDs associated with sessions that you want to analyze.
    """
    
    all_sess_ids = []
    for session in sessiondates:
        just_sess_ids = get_sess_ids(dbe, task_name, subjid=subjid, sessiondate=session, settings_name=settings_name, just_ids=True)
        all_sess_ids = all_sess_ids + just_sess_ids.tolist()
    return all_sess_ids

def get_sess_ids_across_multiple_animals(dbe, task_name, subjids, sessiondate=None, settings_name=None):

    """
    This function will get the session IDs for multiple animals for a specific session you want to analyze.
    These sessions IDs can then be used to create specific queries to get the data for only specific animals.

    Inputs:
        - dbe (Engine object): database engine
        - task_name (string): name of a task (e.g., "prey_foraging_fm")
        - subjids (list of strings): list of names of subjects of interest (e.g., "EXN-R-0013")
        - sessiondate (char): date of a session of interest. MUST BE in 'M/D/Y' format (e.g., '11/20/23' for 20th Nov 2023)
        - settings_name (string): name of your settings of interest, likely reflecting a training state of interest (e.g., "default")
    
    Outputs:
        - sess_ids: array of the session IDs associated with the animals that you want to analyze.
    """
    
    all_sess_ids = []
    for subjid in subjids:
        just_sess_ids = get_sess_ids(dbe, task_name, subjid=subjid, sessiondate=sessiondate, settings_name=settings_name, just_ids=True)
        all_sess_ids = all_sess_ids + just_sess_ids.tolist()
    return all_sess_ids

def get_session_df(dbe, sess_id):

    """
    This function will get the full pandas dataframe for a particular session.
    
    Inputs: 
        - dbe (Engine object): database engine
        -sess_id (int): session ID of interest
    
    Outputs:
        - df (dataframe): pandas dataframe for the whole session
    """

    query = 'select * from beh.trialsview where sessid = ' + str(sess_id)
    df = pd.read_sql(query, dbe)
    return df

def get_session_parsed_events(dbe, sess_id, all_trials=True, trial_nums=None):

    """
    This function will get the parsed events, decoded from json, from a particular session. You can either get the parsed events from all trials
    or specify a specific subset of trials.

    Inputs:
        - dbe (Engine object): database engine
        - sess_id (int): session ID of interest
        - all_trials (bool): If true, this function will get the parsed events for all the trials in the session. If false, you can get the parsed 
        events from only a subset of trials, specified in trial_num
        - trial_nums (list): list of the trials of interest, only used if all_trials is false
    
    Outputs: 
        - If all_trials is True: 
            - parsed_events_all_trials (list): list of dictionaries for the parsed_events for all the trials in the session
        - If all_trials is False: 
            - If you want data from a subset of trials: parsed_events_subset (list): list of dictionaries for the parsed_events for the 
            subset of trials you are interested in for the session
            - If you only want data from one trial: parsed_events (dictionary): dictionary for the parsed_events for that particular trial
    """

    query = 'select * from beh.trialsview where sessid = ' + str(sess_id)
    df = pd.read_sql(query, dbe)
    
    if all_trials:
        parsed_events_all_trials = []
        for i in range(df.shape[0]):
            utf_parsed_events = df['parsed_events'][i].decode('utf8')
            parsed_events = json.loads(utf_parsed_events)['vals']
            parsed_events_all_trials.append(parsed_events)
        return parsed_events_all_trials
    else:
        parsed_events_subset = []
        if len(trial_nums) == 1:
            print(trial_nums[0])
            print(df['parsed_events'].shape)
            utf_parsed_events = df['parsed_events'][trial_nums[0]].decode('utf8')
            parsed_events = json.loads(utf_parsed_events)['vals']
            return parsed_events
        else:
            for trial_num in trial_nums:
                utf_parsed_events = df['parsed_events'][trial_num].decode('utf8')
                parsed_events = json.loads(utf_parsed_events)['vals']
                parsed_events_subset.append(parsed_events = json.loads(utf_parsed_events)['vals'])
            return parsed_events_subset

def get_session_data(dbe, sess_id, all_trials=True, trial_nums=None):

    """
     This function will get the data, decoded from json, from a particular session. You can either get the data from all trials
    or specify a specific subset of trials.

    Inputs:
        - dbe (Engine object): database engine
        - sess_id (int): session ID of interest
        - all_trials (bool): If true, this function will get the data for all the trials in the session. If false, you can get the data from only
        a subset of trials, specified in trial_nums
        - trial_nums (list): list of the trials of interest, only used if all_trials is false
    
    Outputs: 
        - If all_trials is True: 
            - data_events_all_trials (list): list of dictionaries for the data for all the trials in the session
        - If all_trials is False: 
            - If you want data from a subset of trials: data_subset (list): list of dictionaries for the data for the 
            subset of trials you are interested in for the session
            - If you only want data from one trial: data (dictionary): dictionary for the data for that particular trial
    """

    query = 'select * from beh.trialsview where sessid = ' + str(sess_id)
    df = pd.read_sql(query, dbe)
    
    if all_trials:
        data_all_trials = []
        for i in range(df.shape[0]):
            utf_data = df['data'][i].decode('utf8')
            data = json.loads(utf_data)['vals']
            data_all_trials.append(data)
        return data_all_trials
    else:
        data_subset = []
        if len(trial_nums) == 1:
            utf_data = df['data'][trial_nums[0]].decode('utf8')
            data = json.loads(utf_data)['vals']
            return data
        else:
            for trial_num in trial_nums:
                utf_data = df['data'][i].decode('utf8')
                data = json.loads(utf_data)['vals']
                data_subset.append(data)
            return data_subset

def get_session_settings(dbe, sess_id, all_trials=True, trial_nums=None):

    """
    This function will get the settings, decoded from json, from a particular session. You can either get the settings from all trials
    or specify a specific subset of trials.

    Inputs:
        - dbe (Engine object): database engine
        - sess_id (int): session ID of interest
        - all_trials (bool): If true, this function will get the data for all the trials in the session. If false, you can get the settings from only
        a subset of trials, specified in trial_nums
        - trial_nums (list): list of the trials of interest, only used if all_trials is false
    
    Outputs: 
        - If all_trials is True: 
            - settings_all_trials (list): list of dictionaries for the settings for all the trials in the session
        - If all_trials is False: 
            - If you want settings from a subset of trials: settings_subset (list): list of dictionaries for the settings for the 
            subset of trials you are interested in for the session
            - If you only want settings from one trial: settings (dictionary): dictionary for the settings for that particular trial
    """

    query = 'select * from beh.trialsview where sessid = ' + str(sess_id)
    df = pd.read_sql(query, dbe)
    
    if all_trials:
        settings_all_trials = []
        for i in range(df.shape[0]):
            utf_settings = df['settings'][i].decode('utf8')
            settings = json.loads(utf_settings)['vals']
            settings_all_trials.append(settings)
        return settings_all_trials
    else:
        settings_subset = []
        if len(trial_nums) == 1:
            utf_settings = df['settings'][trial_nums[0]].decode('utf8')
            settings = json.loads(utf_settings)['vals']
            return settings
        else:
            for trial_num in trial_nums:
                utf_settings = df['settings'][i].decode('utf8')
                settings = json.loads(utf_settings)['vals']
                settings_subset.append(settings)
            return settings_subset

def get_default_settings(dbe, sess_id):

    default_settings = get_session_settings(dbe, sess_id, all_trials=False, trial_nums=[0])
    return default_settings
