#!/usr/local/bin/python
import pandas as pd
import remove_empty_columns
#check if redcap data is in raw or labels format based on columns, return boolean
def isRedcapRaw(df):
    error = ''
    isError = False

    if 'record_id' in df.columns or 'subid' in df.columns:
        return True, isError, error
    elif 'Record ID' in df.columns or 'Subject ID' in df.columns or 'Participant ID':
        return False, isError, error
    else:
        isError = True
        error = 'Uploaded Redcap csv missing record_id, subid, Record ID, or Subject ID column'
        return None, isError, error

#set redcap timepoint column name to tp, return df
def redcapLabelTimepoint(df, redcapRaw):
    error = ''
    isError = False

    if 'Timepoint' in df.columns:
        df = df.rename(columns={'Timepoint':'tp'})
    elif 'timepoint' in df.columns:
        df = df.rename(columns={'timepoint':'tp'})
    elif redcapRaw == True and 'redcap_event_name' in df.columns:
        df['tp'] = df['redcap_event_name'].str.split('_').str[0].str.lower()
    elif redcapRaw == False and 'Event Name' in df.columns:
        df['tp'] = df['Event Name'].str.split().str[0].str.lower()
    else:
        df = None
        isError = True
        error = 'Uploaded Redcap csv missing timepoint column or event name in unrecognized format'
    return df, isError, error

#find and return redcap subject id column
def getIdCol(df, redcapRaw):
    error = ''
    isError = False

    if redcapRaw == True and 'record_id' in df.columns:
        idCol = 'record_id'
    elif redcapRaw == False and 'Record ID' in df.columns:
        idCol = 'Record ID'
    elif redcapRaw == True and 'subid' in df.columns:
        idCol = 'subid'
    elif redcapRaw == False and 'Subject ID' in df.columns:
        idCol = 'Subject ID'
    elif redcapRaw == False and 'Participant ID' in df.columns:
        idCol = 'Participant ID'
    else:
        idCol = None
        isError = True
        error = 'Uploaded Redcap csv missing subject id column or in unrecognized format (not record_id, Record ID, subid, or Subject ID'
    return idCol, isError, error

#check for missing timepoints, create and return list of subject ids with missing timepoints,
#return df with missing timepoint records dropped
def checkMissing(df, idCol, tpCol):
    if df[tpCol].isnull().values.any(): #look for blank timepoints
        missingTP = df[df[tpCol].isna()][idCol]
        df = df.dropna(subset=[tpCol])
        return df, missingTP
    else:
        return df, 0

#check for duplicate subject id and timepoint combinations,
#create and return list of subject ids with duplicate timepoints,
#return df with duplicate dropped
def checkDups(df, idCol, tpCol):
    if df.duplicated(subset=[idCol, tpCol]).values.any():
        dups = df[df.duplicated(subset=[idCol, tpCol])][idCol]
        df = df.drop_duplicates(subset=[idCol, tpCol])
        return df, dups
    else:
        return df, 0


#check for duplicate column names in upload file by removing .1s and comparing names
#read_csv automatically adds .1 to duplicate column names
#return boolean
def checkDupColumns(df):
    columns = df.columns.str.replace('\.1','')
    checkDupColumns = columns.duplicated()
    for column in checkDupColumns:
        if column == True:
            return True
    return False


#main function
def datafix2(filename, wide_filename, display_back, is_redcap, id_col, tp_col):
    isAnyError = False
    errors = []

    old_file_path = 'uploads/' + filename
    path_to_file_new = 'uploads/' + wide_filename

    #create dataframe
    df = pd.read_csv(old_file_path)#, keep_default_na=False, na_values=['#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', '-nan', '1.#IND', '1.#QNAN', 'N/A', 'NA', 'NULL', 'NaN', 'n/a', 'nan', 'null']) #can change to keep certain NA values rather than turn to blanks, also need to change checkMissing function

    #if redcap csv, get subject id column and set timepoint column to tp
    if is_redcap == 'True':
        redcapRaw, isErrorRaw, errorRaw = isRedcapRaw(df)
        if isErrorRaw: #check for errors from redcap raw check
            isAnyError = True
            errors.append(errorRaw)
            return None, None, isAnyError, errors, None

        df, isErrorTp, errorTp = redcapLabelTimepoint(df, redcapRaw)
        if isErrorTp: #check for errors from redcap timepoint label
            isAnyError = True
            errors.append(errorTp)
            return None, None, isAnyError, errors

        id_col, isErrorId, errorId = getIdCol(df, redcapRaw)
        if isErrorId: #check for errors from getting redcap ID column
            isAnyError = True
            errors.append(errorId)
            return None, None, isAnyError, errors, None

        tp_col = 'tp'

    else:
        #check input id and timepoint columns present in csv
        if id_col not in df.columns or tp_col not in df.columns:
            isAnyError = True
            inputError = 'Input id or timepoint column not in csv'
            errors.append(inputError)
            return None, None, isAnyError, errors, None

    df, missingTPs = checkMissing(df, id_col, tp_col) #check for missing timepoints
    df, duplicates = checkDups(df, id_col, tp_col) #check for duplicate id/timepoint combinations
    isDupColumns = checkDupColumns(df) #check for duplicate column names
    df[tp_col] = df[tp_col].astype(str) #make sure tp column values are string for mapping
    df = df.set_index([id_col, tp_col]).stack(dropna=False).unstack([1,2]) #convert long to wide based on id and tp
    df.columns = list(map("_".join, df.columns)) #merge stacked column names

    #move tp to end of column names if requested
    if display_back == 'True':
        df.columns = df.columns.str.split('_', n=1).str[1] + '_' + df.columns.str.split('_', n=1).str[0]

    #remove empty columns
    df, removedCol = remove_empty_columns.remove_empty_columns(df)
    if removedCol != '':
        removedCol = '<div align="center">The following columns were empty for a specific time_point and dropped from the export:</div>  <div align="center"> '+removedCol+'</div> <div align="center">We did not drop columns that were potentially grouped with other non-empty columns.</div>'
    df.to_csv(path_to_file_new)
    return duplicates, missingTPs, isAnyError, errors, isDupColumns, removedCol
