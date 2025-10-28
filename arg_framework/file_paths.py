import os

project_root = os.getcwd()
results_root = os.path.join(project_root, "stats")
assoc_root_path = os.path.join(project_root, "players")

###---Bot Component File Paths---###

# w2v_boardwords_associations =         os.path.join(assoc_root_path, 'w2v_all_words.json')
# glove_50_boardwords_associations =    os.path.join(assoc_root_path, 'glove_50_all_words.json')
# glove_100_boardwords_associations =   os.path.join(assoc_root_path, 'glove_100_all_words.json')
# glove_200_boardwords_associations =   os.path.join(assoc_root_path, 'glove_200_all_words.json')
# glove_300_boardwords_associations =   os.path.join(assoc_root_path, 'glove_300_all_words.json')
# w2v_glove_boardwords_associations =   os.path.join(assoc_root_path, 'w2v_glove_all_words.json')
cn_nb_boardwords_associations =       os.path.join(assoc_root_path, 'arg_framework','cn_nb_associations.json')
# d2v_boardwords_associations =         os.path.join(assoc_root_path, 'd2v_all_words.json')
# elmo_boardwords_associations =        os.path.join(assoc_root_path, 'elmo_all_words.json')
# bert1_boardwords_associations =       os.path.join(assoc_root_path, 'bert1_all_words.json')
# bert2_boardwords_associations =       os.path.join(assoc_root_path, 'bert2_all_words.json')
# fast_text_boardwords_associations =   os.path.join(assoc_root_path, 'fast-text_all_words.json')


# w2v_vectors_path =          os.path.join(assoc_root_path, 'w2v_lm.txt')
# glove_50_vectors_path =     os.path.join(assoc_root_path, 'glove_50_lm.txt')
# glove_100_vectors_path =    os.path.join(assoc_root_path, 'glove_100_lm.txt')
# glove_200_vectors_path =    os.path.join(assoc_root_path, 'glove_200_lm.txt')
# glove_300_vectors_path =    os.path.join(assoc_root_path, 'glove_300_lm.txt')
# w2v_glove_vectors_path =    os.path.join(assoc_root_path, 'w2v_glove_lm.txt')
cn_nb_vectors_path =        os.path.join(assoc_root_path, 'arg_framework','cn_nb_word_vectors.txt')
# d2v_vectors_path =          os.path.join(assoc_root_path,'d2v_lm.txt')
# elmo_vectors_path =         os.path.join(assoc_root_path, 'elmo_lm.txt')
# bert1_vectors_path =        os.path.join(assoc_root_path, 'bert1_lm.txt')
# bert2_vectors_path =        os.path.join(assoc_root_path, 'bert2_lm.txt')
# fast_text_vectors_path =    os.path.join(assoc_root_path, 'fast-text_lm.txt')

###---filepaths to be set in file_manager---###
#all are implemented as arrays because the experiments use many of each
# class ExperimentPaths:
#     #raw data
#     round_logs_dir_path = None
#     learn_logs_dir_path = None
#     round_log_filepaths = []
#     learn_log_filepaths_cm = [] 
#     learn_log_filepaths_g = []
#     #data transformation
#     parsed_data_dir_path = None
#     processed_data_dir_path = None
#     parsed_data_filepaths = []
#     processed_data_filepaths = []
#     #data interpretation
#     cm_stats_dir_path = None
#     learn_figs_dir_path = None
#     performance_progression_dir_path = None 
#     performance_progression_sliding_window_dir_path = None 
#     arm_weights_dir_path = None 
#     percent_selected_dir_path = None
#     final_stat_distribution_dir_path = None
#     tournament_tables_dir_path = None
#     learn_tables_dir_path = None
#     param_comparison_figs_dir_path = None
#     cm_stat_filepaths = [] #each element is a dictionary
#     performance_progression_filepaths = {} #cm or g, stat
#     performance_progression_sliding_window_filepaths = {}
#     arm_weights_filepaths = {} #cm or g
#     percent_selected_filepaths = {} #cm or g
#     final_stat_distribution_filepaths = {}
#     param_comparison_fig_filepaths = {} #each element is a dictionary
#     tournament_table_filepaths = []
#     learn_table_filepaths = []

#     #compiled data
#     learn_period_analyses_dir_path = None
#     learn_experiment_analyses_dir_path = None
#     param_experiment_analysis_filepath = None #not an array because there is at most one
#     learn_experiment_analysis_filepath_cm = None #not an array because there is at most one
#     learn_experiment_analysis_filepath_g = None #not an array because there is at most one
#     learn_period_analysis_filepaths_cm = [] 
#     learn_period_analysis_filepaths_g = [] 

# ###---Stat filepaths___###
# dist_assoc_solitair_table_path = os.path.join(results_root, "comparison_files", "comparison_objects", "processed_data_distance_associator_solitair.json")
model_path = os.path.join(assoc_root_path, "arg_framework","sklinear36model-nobias.joblib")

# ###---DETECT---###
# freq_path = os.path.join(project_root, "raw_data", "word_freqs.json")
# d2v_path = os.path.join(project_root, "raw_data", "d2v_lm.txt")

# ###---Word Pools---###
# wordlist_path = os.path.join(project_root, 'raw_data', 'actual-final-wl.txt')
# board_words_path = os.path.join(project_root, 'raw_data', 'common_boardwords.txt')

# anc_log_path = os.path.join(results_root, "other", "anc_log_temp.txt")
