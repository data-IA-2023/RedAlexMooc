from mongolo import *
MONGOURL = os.environ.get('MONGO_URL')

# Fonction pour extraire les informations
def extract_info(course_id):
    # Regex pour chaque format avec limite de 5 caractères pour le cours
    regex1 = r'^(.*?)/(.*?)(?:S.*?)?/(.*?)$'
    regex2 = r'^course-v1:(.*?)\+(.*?)(?:S.*?)?\+(.*?)$'

    # Vérifier et extraire les informations pour le premier format
    match1 = re.match(regex1, course_id)
    if match1:
        return match1.groups()

    # Vérifier et extraire les informations pour le deuxième format
    match2 = re.match(regex2, course_id)
    if match2:
        return match2.groups()

    # Retourner None si aucun format ne correspond
    return None, None, None


# Fonction pour convertir en minuscules et supprimer les backslashes
def transform_string(s):
    if isinstance(s, str):
        return s.lower().replace('\\', '')
    return s

def get_the_df():
    dfmessage = read_mongo(
        db='RemiGOAT',
        collection='Message',
        query={}, 
        host=os.environ.get('MONGO_HOST'),
        port=27017,
        username= os.environ.get('MONGO_USERNAME'),
        password=os.environ.get('MONGO_PSW'),
        join_collection='Session',
        local_field='course_id',
        foreign_field='session',
        as_field='session_details',
    )

    dfusers = read_mongo(
        db='RemiGOAT',
        collection='UserData',
        query={},  
        host=os.environ.get('MONGO_HOST'),
        port=27017,
        username= os.environ.get('MONGO_USERNAME'),
        password=os.environ.get('MONGO_PSW'),
    )


    dfgrades = read_mongo(
        db='RemiGOAT',
        collection='SessionByUser',
        query={}, 
        host=os.environ.get('MONGO_HOST'),
        port=27017,
        username= os.environ.get('MONGO_USERNAME'),
        password=os.environ.get('MONGO_PSW'),
    )


    # Fusionner les deux DataFrames sur la colonne "username"
    df_merged_1 = pd.merge(dfmessage, dfusers, on='username', how='inner')


    # Extraire les valeurs de chaque dictionnaire dans la liste et créer de nouvelles colonnes avec ces valeurs
    for key in df_merged_1['session_details'][0][0].keys():
        df_merged_1[key] = df_merged_1['session_details'].apply(lambda x: x[0][key] if isinstance(x, list) and len(x) > 0 else None)

    # Supprimer la colonne "session_details" originale
    df_merged_1.drop(columns=['session_details'], inplace=True)


    # Fusionner les deux DataFrames sur la colonne "username"
    df_merged_final = pd.merge(df_merged_1, dfgrades, on=['username','session'])

    # Filtrer les lignes où la valeur de la colonne "IsEval" est égale à True
    df_IsEval = df_merged_final[df_merged_final['IsEval'] == True]

    df_IsEval.drop(columns=['session', '_id'], inplace=True)



    # Créer un dictionnaire pour stocker les valeurs correspondantes pour chaque thread_id
    thread_id_values = {}

    # Parcourir les lignes du DataFrame
    for index, row in df_IsEval.iterrows():
        # Si le thread_id n'est pas dans le dictionnaire, l'ajouter avec les valeurs actuelles
        if row['thread_id'] not in thread_id_values:
            thread_id_values[row['thread_id']] = {
                'title': row['title'],
                'context': row['context'],
                'courseware_title': row['courseware_title'],
                'thread_type' : row['thread_type']
            }
        # Si le thread_id est dans le dictionnaire mais a des valeurs manquantes, remplacer NaN par les valeurs existantes
        else:
            if pd.isna(thread_id_values[row['thread_id']]['title']):
                thread_id_values[row['thread_id']]['title'] = row['title']
            if pd.isna(thread_id_values[row['thread_id']]['context']):
                thread_id_values[row['thread_id']]['context'] = row['context']
            if pd.isna(thread_id_values[row['thread_id']]['courseware_title']):
                thread_id_values[row['thread_id']]['courseware_title'] = row['courseware_title']
            if pd.isna(thread_id_values[row['thread_id']]['thread_type']):
                thread_id_values[row['thread_id']]['thread_type'] = row['thread_type']

    # Remplacer les valeurs NaN dans le DataFrame original par les valeurs du dictionnaire correspondant au thread_id
    df_IsEval['title'] = df_IsEval.apply(lambda row: thread_id_values[row['thread_id']]['title'] if pd.isna(row['title']) else row['title'], axis=1)
    df_IsEval['context'] = df_IsEval.apply(lambda row: thread_id_values[row['thread_id']]['context'] if pd.isna(row['context']) else row['context'], axis=1)
    df_IsEval['courseware_title'] = df_IsEval.apply(lambda row: thread_id_values[row['thread_id']]['courseware_title'] if pd.isna(row['courseware_title']) else row['courseware_title'], axis=1)
    df_IsEval['thread_type'] = df_IsEval.apply(lambda row: thread_id_values[row['thread_id']]['thread_type'] if pd.isna(row['thread_type']) else row['thread_type'], axis=1)


    df_IsEval = df_IsEval.sort_values(by='thread_id')
    # Remplacer les NaN par None
    df_IsEval.replace({pd.NA: None}, inplace=True)
    df_IsEval_User = df_IsEval
    df_IsEval_User.drop(['message_id', 'parent_id', 'thread_id', 'thread_type', 'title', 'context', 'courseware_title', 'type', 'created_at', 'updated_at', 'vote_down_count', 'vote_up_count', 'vote_point', 'vote_count', 'IsEval'], axis=1, inplace=True)

    # Filtrer les données où la valeur de la target n'est pas None
    df_IsEval_User = df_IsEval_User[df_IsEval_User['grade'].notna()]

    # Appliquer la fonction aux données
    df_IsEval_User[['université', 'cours', 'session']] = df_IsEval_User['course_id'].apply(extract_info).apply(pd.Series)
    df_IsEval_User.drop(['course_id',"session",'id',"username" ],axis=1, inplace=True)

    df_cnam                   = df_IsEval_User[df_IsEval_User['université'] == 'CNAM']
    df_IsEval_User            = df_IsEval_User.drop(df_cnam.index)
    # Ajouter la colonne isEmail
    df_IsEval_User['isEmail'] = df_IsEval_User['email'].notna() & (df_IsEval_User['email'] != '')

    columns_of_interest = ['city', 'country', 'gender', 'level_of_education', 'email', 'CSP', 'year_of_birth']
    # Remplacer 'None', 'none', et '' par np.nan
    df_IsEval_User[columns_of_interest] = df_IsEval_User[columns_of_interest].replace(['None', 'none', '',None], np.nan)
    df_IsEval_User['datagiven'] = df_IsEval_User[columns_of_interest].notna().sum(axis=1)
    df_IsEval_User.drop(["csp","Certificate Type","Enrollment Track"],axis=1, inplace=True)
    duplicated_emails = df_IsEval_User[df_IsEval_User.duplicated(subset=['email','cours'], keep=False)]
    email_not_none = duplicated_emails[duplicated_emails['email'].notna()]
    date_none = email_not_none[email_not_none['date_grade_report'].isna()]
    df_IsEval_User_cleaned_final = df_IsEval_User.drop(date_none.index)
    df_final_test = df_IsEval_User_cleaned_final.drop(columns=['email','date_grade_report','date_grade_report','date_problem_grade_report','université','Certificate Eligible','idUser','body','Verification Status','Cohort Name'],axis = 1)
    df_fulldata = df_final_test[df_final_test['datagiven'] == 7]
    df_fullfiltered = df_fulldata[df_fulldata['Certificate Delivered'].isin(['N/A']) | df_fulldata['Certificate Delivered'].isna()]
    # Supprimer les lignes de df_IsEval_User présentes dans date_none
    df_full_final = df_fulldata.drop(df_fullfiltered.index)
    
    string_column = ['city', 'country', 'gender', 'level_of_education', 'CSP']
    for col in string_column:
        df_full_final[col] = df_full_final[col].apply(transform_string)

    return df_full_final

def get_df_for_classifier(df):
    # Convert the 'grade' column to numeric, forcing non-numeric values to NaN
    df['grade'] = pd.to_numeric(df['grade'], errors='coerce')
    
    df_full_final_classifier = df
    
    # Filter the DataFrame based on 'Certificate Delivered' and 'grade'
    df_certificate_N = df.loc[(df_full_final_classifier['Certificate Delivered'] == 'N') & (df_full_final_classifier['grade'] > 0.5)]
    
    # Drop the filtered rows from the original DataFrame
    df_full_final_classifier = df_full_final_classifier.drop(df_certificate_N.index)
    
    # Create a multiplier DataFrame for balancing classes
    df_full_final_classifier_multiplier = df_full_final_classifier.loc[df_full_final_classifier['Certificate Delivered'] == 'N']
    
    # Concatenate the original DataFrame with the multiplied DataFrame
    df_full_final_classifier = pd.concat([df_full_final_classifier] + [df_full_final_classifier_multiplier] * 5, ignore_index=True)
    
    return df_full_final_classifier

def get_df_for_regressor(df):
    # Assurez-vous que la colonne 'grade' contient uniquement des valeurs numériques
    df['grade'] = pd.to_numeric(df['grade'], errors='coerce')
    # Appliquer le filtrage
    df_full_final_regressor = df
    df_full_final_regressor_multiplier = df_full_final_regressor[df_full_final_regressor['grade'] < 0.5]
    df_full_final_regressor = pd.concat([df_full_final_regressor] + [df_full_final_regressor_multiplier] * 6, ignore_index=True)
    
    return df_full_final_regressor


"""df = get_the_df()

df_classifier = get_df_for_classifier(df)

# Enregistrez le DataFrame dans un fichier CSV
df_classifier.to_csv('output.csv', index=False)

print("Le DataFrame a été enregistré dans le fichier 'output.csv'")"""