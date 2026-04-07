clearvars
% close all
clc

global P

file_path = '/Users/joanponce/Library/CloudStorage/Dropbox/Spatial Mosquito project/Data/Mosquito counts/full_table_Lita.csv';
% Read the data from the CSV file
table_data = readtable(file_path);

% Convert the 'temp_date' column to datetime format
table_data.temp_date = datetime(table_data.temp_date);

% Calculate the number of days that have passed since the first date
days_passed = (table_data.temp_date - table_data.temp_date(1))+1;

% Add the 'Days_Passed' column to the table
table_data.Days_Passed = days(days_passed);

% Display the updated table
disp(table_data);

% Save the table to a MAT-file
save('full_table_Lita.mat', 'table_data');


%------
% Initial guess for parameters
initial_guess = [0.5, 0.5]; % Initial guess for betas
    
% Optimize parameters
params = fminsearch(@(p) error_fun_betas(p, data), initial_guess);

% Display estimated parameters
disp('Estimated parameters (beta1, beta2):');
disp(params);