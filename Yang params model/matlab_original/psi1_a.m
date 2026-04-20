%Farnesi 2009
function psi1A = psi1_a(day)
    global P 
        %To get psi_1a
    EP=[0.811, 0.939, 0.96, 0.933, 0.828, 0.485];
    Temp=[16,22,25,28,31,35];

% % Scatter plot
% scatter(Temp, EP, 'o', 'MarkerEdgeColor', 'b', 'MarkerFaceColor', 'r');
% hold on;

% Fit a fifth-degree polynomial
degree = 5;
p = polyfit(Temp, EP, degree);

% % Generate a smooth curve using the fitted polynomial coefficients
% x_fit = linspace(min(Temp), max(Temp), 1000);
% y_fit = polyval(p, x_fit);
% 
% % Plot the fitted curve
% plot(x_fit, y_fit, 'g-', 'LineWidth', 2);
% 
% % Add labels and title
% xlabel('Temperature (°C)');
% ylabel('Eclosion %');
% title('Scatter Plot with Fifth Degree Polynomial Fit');
% 
% % Add a legend
% legend('Data Points', 'Fifth Degree Polynomial Fit', 'Location', 'Best');
% 
% % Add a grid for better readability
% grid on;
% 
% % Release the hold on the plot
% hold off;

    EP_vals=@(day)polyval(p, temp(day, 0));
    psi1A = (P.mu_E_a(day).*EP_vals(day))./(1-EP_vals(day));

end