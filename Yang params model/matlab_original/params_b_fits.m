%Parameters for Albopictus: 
%1. Fit parameters to Mordecai values to obtain polynomial coeffs to
%estimate: mu_F, psi_2_b, 
%mu_F_b
%Mordecai paper data
    lifespan_table = readtable("/Users/joanponce/Library/CloudStorage/Dropbox/Spatial Mosquito project/Data/params data extraction Mordecai/Albopictus data/Adult_Lifespan_alb.csv");
    fit_lifespan = polyfit(lifespan_table.Temperature,lifespan_table.AdultLifespan,5);        
    % Generate x-values
    x_values = linspace(13, 33, 40);
    % Evaluate the polynomial
    y_values = polyval(fit_lifespan, x_values);
    % Plot the seventh-degree polynomial
    figure;
    plot(x_values, 1./y_values, 'LineWidth', 2);
    title('mu_F_b');
    xlabel('x');
    ylabel('y');
    grid on;

    format long;

% Display the coefficients
disp(fit_lifespan);

% Reset the display format to the default
format short;


    %MDR to obtain psi_2_b: 
    dev_table = readtable("/Users/joanponce/Library/CloudStorage/Dropbox/Spatial Mosquito project/Data/params data extraction Mordecai/Albopictus data/MDR_alb.csv");
    fit_dev = polyfit(dev_table.Temperature,dev_table.MDR,6);
    % Generate x-values
    x_values = linspace(10, 40, 40);
    % Evaluate the polynomial
    y_values = polyval(fit_dev, x_values);
    % Plot the seventh-degree polynomial
    figure;
    plot(x_values, y_values, 'LineWidth', 2);
    title('Psi_2_b');
    xlabel('x');
    ylabel('y');
    grid on;

    format long;

% Display the coefficients
disp(fit_dev);

% Reset the display format to the default
format short;


%phi_b    
    fecundity_table = readtable("/Users/joanponce/Library/CloudStorage/Dropbox/Spatial Mosquito project/Data/params data extraction Mordecai/Albopictus data/Fecundity_alb.csv");
    biting_rate = readtable("/Users/joanponce/Library/CloudStorage/Dropbox/Spatial Mosquito project/Data/params data extraction Mordecai/Albopictus data/Biting_rate.csv");
    fit_fecund = polyfit(fecundity_table.Temperature,fecundity_table.eggs_per_female_per_cycle,6);
    fit_br = polyfit(biting_rate.Temperature,biting_rate.Biting_rate,6);
    f_prod = @(x) polyval(fit_br,x).*polyval(fit_fecund,x);
    % Generate x-values
    x_values = linspace(10, 35, 40);
    % Evaluate the polynomial
    y_values = f_prod(x_values);
    % Plot the seventh-degree polynomial
    figure;
    plot(x_values, y_values, 'LineWidth', 2);
    title('Fecundity per female per day');
    xlabel('x');
    ylabel('y');
    grid on;

% \mu_L_b
    eas_table = readtable("/Users/joanponce/Library/CloudStorage/Dropbox/Spatial Mosquito project/Data/params data extraction Mordecai/Albopictus data/EAS_alb.csv");
    fit_eas = polyfit(eas_table.Temperature,eas_table.EAS,6);
    x_vals = linspace(10, 40, 30);
    y_vals = polyval(fit_eas, x_vals);
    figure;
    plot(x_vals, y_vals, '-', 'LineWidth', 2);
    mu_L_b = @(x) polyval(fit_dev, x)./polyval(fit_eas,x)-polyval(fit_dev,x);
    % Generate x-values
    x_values = linspace(10, 35, 40);
    % Evaluate the polynomial
    y_values = mu_L_b(x_values);
    % Plot the seventh-degree polynomial
    figure;
    plot(x_values, y_values, 'LineWidth', 2);
    title('mu_L');
    xlabel('x');
    ylabel('y');
    grid on;



%Marini paper    
%Psi_1_b
    x_values = [10, 15, 25, 30];
    y_values = [2, 4.5, 7.4, 6.7];
    development_rate = polyfit(x_values, y_values, 3);
    x_vals = linspace(10, 35, 20);
    y_vals = polyval(development_rate, x_vals);
    figure;
    plot(x_values, y_values, 'o', x_vals, y_vals, '-', 'LineWidth', 2);

    plot(x_vals, 1./y_vals, '-', 'LineWidth', 2);
    title('Psi_1_b');

% \mu_E_b
    x_values = [10, 15, 25, 30];
    y_values = [0.04, 0.08, 0.49, 0.51];
    Egg_L1 = polyfit(x_values, y_values, 3);
    x_vals = linspace(10, 30, 20);
    y_vals = polyval(Egg_L1, x_vals);
    figure;
    plot(x_values, y_values, 'o', x_vals, y_vals, '-', 'LineWidth', 2);
    %Egg_L1 = psi_1/(psi_1+mu_E), mu_E=\psi_1/EL1-psi_1
    mu_E_b = @(x) ((1./polyval(survival_rate, x))./polyval(Egg_L1,x))-(1./polyval(survival_rate,x));
    % Generate x-values
    x_values = linspace(10, 35, 40);
    % Evaluate the polynomial
    y_values = mu_E_b(x_values);
    % Plot the seventh-degree polynomial
    figure;
    plot(x_values, y_values, 'LineWidth', 2);
    title('mu_E');
    xlabel('x');
    ylabel('y');
    grid on;

    figure;
    plot(x_values, 1./y_values, 'LineWidth', 2);
    title('1/mu_E');
    xlabel('x');
    ylabel('y');
    grid on;

%%%%%%%%%%

    fecundity_table = readtable("/Users/joanponce/Library/CloudStorage/Dropbox/Spatial Mosquito project/Data/params data extraction Mordecai/Albopictus data/Fecundity_alb.csv");

    fit_fecund = polyfit(fecundity_table.Temperature,fecundity_table.eggs_per_female_per_cycle,6);
% Generate x-values
    x_values = linspace(10, 35, 40);
    % Evaluate the polynomial
    y_values = polyval(fit_fecund, x_values);
    % Plot the seventh-degree polynomial
    figure;
    plot(x_values, y_values, 'LineWidth', 2);
    title('Fecundity');
    xlabel('x');
    ylabel('y');
    grid on;

%to get fecundity extract biting rate
    bit_rate = fit_dev;
    f_prod = @(x) polyval(fit_dev,x).*polyval(fit_fecund,x);

    % Generate x-values
    x_values = linspace(10, 35, 40);
    % Evaluate the polynomial
    y_values = f_prod(x_values);
    % Plot the seventh-degree polynomial
    figure;
    plot(x_values, y_values, 'LineWidth', 2);
    title('Fecundity per female per day');
    xlabel('x');
    ylabel('y');
    grid on;


