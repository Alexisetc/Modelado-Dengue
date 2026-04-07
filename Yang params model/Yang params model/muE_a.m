%Farnesi 2009
function mu_E_a = muE_a(day)
    global P 
    %     %To get Mu_E
    % CE=[489.3, 98.3, 77.4, 61.6, 48.4, 50.3];
    % Temp=[16,22,25,28,31,35];
    % mu_E = (1./CE) *24;
    % 
    % % Fit a polynomial using polyfit
    % coefficients = polyfit(Temp, mu_E, 5);
    coefficients = [-0.0000,0.0004,-0.0168, 0.3890,-4.3705,19.0735];
    % Generate points for the fitted polynomial curve
    x_values=temp(day, 0);
    mu_E_a = 1./polyval(coefficients, x_values);
    %plot(linspace(13, 33, 40), 1./polyval((coefficients), (linspace(13,
    %33, 40)))) %to plot parameter vs temperature
end